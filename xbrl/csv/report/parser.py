import json
import os.path
from urllib.parse import urljoin
import io
import csv
import urllib

from xbrl.json.schema import json_validate, DuplicateKeyError
from xbrl.xbrlerror import XBRLError
from xbrl.xml import qname
from xbrl.const import NS, DocumentType
from xbrl.xml.taxonomy.document import SchemaRef

from .report import Report
from .tabletemplate import TableTemplate
from .table import Table
from .column import Column, FactColumn, PropertyGroupColumn
from .values import ParameterReference, RowNumberReference, parseReference
from .validators import isValidIdentifier, validateURIMap
from .specialvalues import processSpecialValues
from .csvdialect import XBRLCSVDialect

class XBRLCSVReportParser:

    def __init__(self, processor):
        self.processor = processor

    def parse(self, url):

        metadata = self.loadMetaData(url)

        nsmap = metadata.get("documentInfo").get("namespaces", {})
        validateURIMap(nsmap)
        taxonomy = self.getTaxonomy(metadata, url)

        templates = dict()

        for name, template in metadata.get("tableTemplates",{}).items():
            if not(isValidIdentifier(name)):
                raise XBRLError("xbrlce:invalidIdentifier", "Table template name '%s' is not a valid identifier" % name)
            columnDefs = template.get("columns", {})
            columns = dict()
            for colname, coldef in columnDefs.items():
                if not(isValidIdentifier(colname)):
                    raise XBRLError("xbrlce:invalidIdentifier", "Column name '%s' is not a valid identifier" % colname)
                if {"dimensions", "propertiesFrom"} & coldef.keys():
                    if "propertyGroups" in coldef:
                        raise XBRLError("xbrlce:conflictingColumnType", 'If "dimensions" or "propertiesFrom" is present on column definition, "propertyGroups" must be absent %s/%s' % (name, colname))
                    dims = self.parseDimensions(coldef.get("dimensions",{}), nsmap)
                    pfs = coldef.get("propertiesFrom", [])
                    for pf in pfs:
                        if pf not in columnDefs:
                            raise XBRLError("xbrlce:invalidPropertyGroupColumnReference", "Property Group column '%s' referenced from column '%s' does not exist" %  (pf, colname))
                    columns[colname] = FactColumn(colname, dims, pfs)
                elif "propertyGroups" in coldef:
                    columns[colname] = PropertyGroupColumn(colname)
                else:
                    if "decimals" in coldef:
                        raise XBRLError("xbrlce:misplacedDecimalsOnNonFactColumn", "Decimals property may not appear on non-fact column '%s'" % colname)
                    columns[colname] = Column(colname)

            templates[name] = TableTemplate(name, columns, self.parseDimensions(template.get("dimensions", {}), nsmap))

        tables = []
        for name, table in metadata.get("tables",{}).items():
            if not(isValidIdentifier(name)):
                raise XBRLError("xbrlce:invalidIdentifier", "Table name '%s' is not a valid identifier" % name)
            # Template name defaults to table name
            templateName = table.get("template", name)
            if not(isValidIdentifier(templateName)):
                raise XBRLError("xbrlce:invalidIdentifier", "Template name '%s' is not a valid identifier" % templateName)
            template = templates.get(templateName, None)
            if template is None:
                raise XBRLError("xbrlce:unknownTableTemplate", "Template definition not found for %s (table: %s)" % (templateName, name));
            tables.append(Table(name, template, urljoin(url, table.get("url")), parameters=table.get("parameters",{}), optional = table.get("optional", False)))

        parameters = self.parseReportParameters(url, metadata)

        report = Report(
            templates = templates, 
            dimensions = self.parseDimensions(metadata.get("dimensions",{}),nsmap),
            parameters = parameters,
            nsmap = nsmap,
            tables = tables,
            taxonomy = taxonomy)

        report.loadTables(self.processor.resolver)

    def getTaxonomy(self, metadata, url):
        taxonomy = metadata.get("documentInfo").get("taxonomy", [])
        if len(taxonomy) == 0:
            raise XBRLError("oime:noTaxonomy", "No taxonomy specified in metadata")

        schemaRefs = list(SchemaRef(urljoin(url, t)) for t in taxonomy)
        return self.processor.loadTaxonomy(schemaRefs)


    def loadMetaData(self, url):
        
        # Make sure we raise unsupportedDocumentType rather than
        # invalidJSONStructure if documentType is not present.
        try:
            with self.processor.resolver.open(url) as src:
                jsonStr = src.read().decode("utf-8") 
                j = json.loads(jsonStr)
        except UnicodeDecodeError as e:
            raise XBRLError("xbrlce:invalidJSON", "Unicode decode error loading %s: %s" % (src, str(e)))
        except json.JSONDecodeError as e:
            raise XBRLError("xbrlce:invalidJSON", "JSON decode error %s: %s" % (src, str(e)))
        docInfo = j.get("documentInfo",{})
        docType = docInfo.get("documentType", None)
        if docType != DocumentType.xbrlcsv:
            raise XBRLError("oimce:unsupportedDocumentType", "Unsupported document type: %s" % docType)

        with self.processor.resolver.open(url) as src:
            try:
                err = json_validate(os.path.join(os.path.dirname(__file__), "xbrl-csv-metadata.json"), src)
            except DuplicateKeyError as e:
                raise XBRLError("xbrlce:invalidJSON", str(e))
        if err is not None:
            raise XBRLError("xbrlce:invalidJSONStructure", err)


        extensible = {
            "documentInfo": {
                "namespaces": dict,
                "linkTypes": dict,
                "linkGroups": dict,
                "features": dict,
                "taxonomy": list,
                "documentType": None
            },
            "tableTemplates": dict,
            "tables": dict,
            "dimensions": dict,
            "final": dict,
            "parameters": dict,
        }

        taxonomy = []
        for e in docInfo.get("extends", []):
            m = self.loadMetaData(urljoin(url, e))
            importedDocType = m["documentInfo"]["documentType"]
            if importedDocType != docType:
                raise XBRLError("xbrlce:multipleDocumentTypesInExtensionChain", "Document type for %s conflicts with document type for %s (%s vs %s)" % (e, url, importedDocType, docType))

            self.mergeDict(j, m, extensible)

        return j

    def mergeDict(self, a, b, extensible):
        for k, v in b.items():
            if k in extensible:
                ext = extensible[k]
                if type(ext) == dict:
                    self.mergeDict(a.setdefault(k, {}), b[k], extensible[k])
                elif ext == dict:
                    if k in a:
                        if a[k] != b:
                            raise XBRLError("xbrlce:conflictingMetadataValue", 'Conflicting value for %s ("%s" vs "%s")' % (k, a[k], v))
                    else:
                        a[k] = b
                elif ext == list:
                    a[k] = b[k] + a.get(k, [])
                elif ext is not None:
                    raise ValueError("Unexpected value in extensible dict: %s" % v)


            elif k in a:
                raise XBRLError("xbrlce:illegalRedefinitionOfNonExtensibleProperty", "'%s' cannot appear in more than one metadata file" % k)


    def parseDimensions(self, dimensions, nsmap):
        processedDims = dict()
        for name, value in dimensions.items():
            dimQName = qname(name, nsmap = { None: NS.xbrl, **nsmap })

            processedValue = processSpecialValues(value)
            if type(processedValue) == str:
                if processedValue.startswith("$"):
                    if processedValue.startswith("$$"):
                        processedValue = processedValue[1:]
                    else:
                        processedValue = parseReference(processedValue)
            if dimQName == qname("xbrl:concept"):
                if processedValue is None:
                    raise XBRLError("xbrlce:invalidJSONStructure", "Concept dimension must not be nil")
                if type(processedValue) == str:
                    # XXX need proper QName validation
                    if ":" not in processedValue:
                        raise XBRLError("xbrlce:invalidJSONStructure", "Invalid QName for concept dimension (%s)" % processedValue)
                    try:
                        # XXX we should do this after resolving parameter references
                        processedValue = qname(processedValue, { "xbrl": NS.xbrl, **nsmap})
                    except KeyError:
                        raise XBRLError("oimce:unboundPrefix", "Missing namespace prefix (%s)" % processedValue)

            processedDims[dimQName] = processedValue


        return processedDims
         


    def parseReportParameters(self, primaryURL, metadata):
        reportParameters = metadata.get("parameters", {})
        parameterURL = metadata.get("parameterURL")
        if parameterURL is not None:
            url = urljoin(primaryURL, parameterURL)
            try:
                with self.processor.resolver.open(url) as fin:
                    reader = csv.reader(io.TextIOWrapper(fin, "utf-8-sig"), XBRLCSVDialect)
                    headerRow = next(reader, None)
                    if headerRow is None:
                        raise XBRLError("xbrlce:invalidParameterCSVFile", "Parameter CSV file '%s' must contain at least a head row" % url)
                    r = iter(headerRow)
                    if ("name", "value") != (next(r, ""), next(r, "")):
                        raise XBRLError("xbrlce:invalidParameterCSVFile", "Invalid parameter CSV file '%s': header row must contain only \"name\" and \"value\"" % url)
                    for c in r:
                        if r != "":
                            raise XBRLError("xbrlce:invalidParameterCSVFile", "Invalid parameter CSV file '%s': header row must contain only \"name\" and \"value\"" % url)

                    rownum = 1

                    for row in reader:
                        r = iter(row)
                        name = next(r, None)
                        if name is not None:
                            value = next(r, "")
                            if value == "":
                                raise XBRLError("xbrlce:invalidParameterCSVFile", "Invalid parameter CSV file '%s': value must be supplied for parameter (use '#empty' or '#none' for empty string or no-value)" % url)

                            if name in reportParameters:
                                raise XBRLError("xbrlce:illegalReportParameterRedefinition", "Parameter '%s' redefined in parameter CSV file '%s'" % (name, url))
                            reportParameters[name] = value


                        for c in r:
                            if r != "":
                                raise XBRLError("xbrlce:invalidParameterCSVFile", "Invalid parameter CSV file '%s': trailing content on row %d" % (url, rownum))

                        rownum += 1


            except urllib.error.URLError as e:
                if isinstance(e.reason, FileNotFoundError):
                    raise XBRLError("xbrlce:missingParametersFile", "Parameter CSV file '%s' does not exist" % url)
                raise e
            except csv.Error as e:
                raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))
            except UnicodeDecodeError as e:
                raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))
            
        return reportParameters
            


