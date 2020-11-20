import json
import os.path
from urllib.parse import urljoin
import io
import csv
import urllib

from xbrl.json.schema import json_validate
from xbrl.xbrlerror import XBRLError
from xbrl.xml import qname
from xbrl.const import NS, DocumentType
from xbrl.xml.taxonomy.document import SchemaRef

from .report import Report
from .tabletemplate import TableTemplate
from .table import Table
from .column import Column, FactColumn
from .values import ParameterReference
from .validators import isValidIdentifier
from .specialvalues import processSpecialValues
from .csvdialect import XBRLCSVDialect

class XBRLCSVReportParser:

    def __init__(self, processor):
        self.processor = processor


    def parse(self, url):

        metadata = self.loadMetaData(url)

        nsmap = metadata.get("documentInfo").get("namespaces", {})
        taxonomy = self.getTaxonomy(metadata, url)

        templates = dict()

        for name, template in metadata.get("tableTemplates",{}).items():
            if not(isValidIdentifier(name)):
                raise XBRLError("xbrlce:invalidIdentifier", "Table template name '%s' is not a valid identifier" % name)
            columns = dict()
            for colname, coldef in template.get("columns", {}).items():
                if not(isValidIdentifier(colname)):
                    raise XBRLError("xbrlce:invalidIdentifier", "Column name '%s' is not a valid identifier" % colname)
                if {"dimensions", "propertiesFrom"} & coldef.keys():
                    if "propertyGroups" in coldef:
                        raise XBRLError("xbrlce:conflictingColumnType", 'If "dimensions" or "propertiesFrom" is present on column definition, "propertyGroups" must be absent %s/%s' % (name, colname))
                    dims = self.parseDimensions(coldef.get("dimensions",{}), nsmap)
                    columns[colname] = FactColumn(colname, dims)
                else:
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
            tables.append(Table(name, template, urljoin(url, table.get("url")), dict(), optional = table.get("optional", False)))

        parameters = self.parseReportParameters(url, metadata)

        report = Report(
            templates = templates, 
            dimensions = self.parseDimensions(metadata.get("dimensions",{}),nsmap),
            parameters = parameters,
            nsmap = nsmap,
            tables = tables)

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
            err = json_validate(os.path.join(os.path.dirname(__file__), "xbrl-csv-metadata.json"), src)
        if err is not None:
            raise XBRLError("xbrlce:invalidJSONStructure", err)



        taxonomy = []
        for e in docInfo.get("extends", []):
            m = self.loadMetaData(urljoin(url, e))
            importedDocType = m["documentInfo"]["documentType"]
            if importedDocType != docType:
                raise XBRLError("xbrlce:multipleDocumentTypesInExtensionChain", "Document type for %s conflicts with document type for %s (%s vs %s)" % (e, url, importedDocType, docType))
            for path in (
                    ("documentInfo", "namespaces"),
                    ("documentInfo", "linkTypes"),
                    ("documentInfo", "linkGroups"),
                    ("documentInfo", "features"),
                    ("tableTemplates",),
                    ("tables",),
                    ("dimensions",),
                    ("final",),
                    ("parameters",),
                    ):
                self.mergeDict(path, j, m)
            taxonomy.extend(m.get("documentInfo").get("taxonomy",[]))
            taxonomy.extend(docInfo.get("taxonomy",[]))
            docInfo["taxonomy"] = taxonomy

        return j

    def mergeDict(self, path, a, b):
        for p in path:
            a = a.setdefault(p, {})
            b = b.get(p, {})
        for k, v in b.items():
            if k in a:
                if a[k] != v:
                    errorPath = "/" + "/".join(path + (k,))
                    raise XBRLError("xbrlce:conflictingMetadataValue", 'Conflicting value for %s ("%s" vs "%s")' % (errorPath, a[k], v))
            else:
                a[k] = v

    def parseDimensions(self, dimensions, nsmap):
        processedDims = dict()
        for name, value in dimensions.items():
            dimQName = qname(name, nsmap = { None: NS.xbrl, **nsmap })

            processedValue = processSpecialValues(value)
            if type(processedValue) == str:
                if processedValue.startswith("$"):
                    processedValue = processedValue[1:]
                    if not processedValue.startswith("$"):
                        if not isValidIdentifier(processedValue):
                            raise XBRLError("xbrlce:invalidReference", "'$%s' is not a valid row number reference or parameter reference" % processedValue)
                        processedValue = ParameterReference(processedValue)
            if dimQName == qname("xbrl:concept"):
                if processedValue is None:
                    raise XBRLError("xbrlce:invalidJSONStructure", "Concept dimension must not be nil")
                if type(processedValue) == str:
                    # XXX need proper QName validation
                    if ":" not in processedValue:
                        raise XBRLError("xbrlce:invalidJSONStructure", "Invalid QName for concept dimension (%s)" % processedValue)
                    try:
                        # XXX we should do this after resolving parameter references
                        processedValue = qname(processedValue, nsmap)
                    except KeyError:
                        raise XBRLError("oimce:unboundPrefix", "Missing namespace prefix (%s)" % processedValue)

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
            


