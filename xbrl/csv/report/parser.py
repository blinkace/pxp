import json
import os.path
from urllib.parse import urljoin
import io
import csv
import urllib
import logging

from xbrl.json.schema import json_validate, DuplicateKeyError
from xbrl.xbrlerror import XBRLError
from xbrl.xml import qname
from xbrl.const import NS, DocumentType
from xbrl.xml.taxonomy.document import SchemaRef
from xbrl.model.report import Report

from .report import CSVReport
from .tabletemplate import TableTemplate
from .table import Table
from .column import Column, FactColumn, PropertyGroupColumn
from .values import ParameterReference, parseReference, ExplicitNoValue
from .properties import Properties, PropertyGroupMergeDimensionsConflict, PropertyGroupMergeDecimalsConflict
from .validators import isValidIdentifier, validateURIMap
from .specialvalues import processSpecialValues
from .csvdialect import XBRLCSVDialect
from .parameters import Parameters

logger = logging.getLogger(__name__)

finalValues = {
    "/documentInfo/namespaces": "namespaces",
    "/documentInfo/taxonomy": "taxonomy",
    "/documentInfo/linkTypes": "linkTypes",
    "/documentInfo/linkGroups": "linkGroups",
    "/documentInfo/features": "features",
    "/tableTemplates": "tableTemplates",
    "/tables": "tables",
    "/dimensions": "dimensions",
    "/parameters": "parameters"
}

class XBRLCSVReportParser:

    def __init__(self, processor):
        self.processor = processor

    def parse(self, url):

        metadata = self.loadMetaData(url)

        docInfo = metadata.get("documentInfo")

        nsmap = docInfo.get("namespaces", {})
        validateURIMap(nsmap)

        self.parameterReferences = set()

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
                    properties = self.parseProperties(coldef, nsmap)
                    pfs = coldef.get("propertiesFrom", [])
                    for pf in pfs:
                        if pf not in columnDefs:
                            raise XBRLError("xbrlce:invalidPropertyGroupColumnReference", "Property Group column '%s' referenced from column '%s' does not exist" %  (pf, colname))
                    columns[colname] = FactColumn(colname, properties, pfs)
                else:
                    if "decimals" in coldef:
                        raise XBRLError("xbrlce:misplacedDecimalsOnNonFactColumn", "Decimals property may not appear on non-fact column '%s'" % colname)
                    if "propertyGroups" in coldef:
                        pgs = dict()
                        for pgName, pg in coldef["propertyGroups"].items():
                            pgs[pgName] = self.parseProperties(pg, nsmap)

                        columns[colname] = PropertyGroupColumn(colname, pgs)
                    else:
                        columns[colname] = Column(colname)

            rowIdColumnName = template.get("rowIdColumn")
            if rowIdColumnName is not None:
                rowIdColumn = columns.get(rowIdColumnName)
                if rowIdColumn is None:
                    raise XBRLError("xbrlce:undefinedRowIdColumn", "Column '%s' (specified as row ID column) does not exist." % rowIdColumnName)
            else:
                rowIdColumn = None

            self.validatePropertyGroups(columns)

            templates[name] = TableTemplate(name, columns, self.parseProperties(template, nsmap), rowIdColumn)

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
            tables.append(Table(name, template, urljoin(url, table.get("url")), parameters=self.parseParameters(table), optional = table.get("optional", False)))

        reportProperties = self.parseProperties(metadata, nsmap)

        parameters = self.parseReportParameters(url, metadata)
        for p in parameters:
            if p not in self.parameterReferences:
                raise XBRLError("xbrlce:unreferencedParameter", "The report parameter '%s' is not referenced" % (p))

        csvReport = CSVReport(
            templates = templates, 
            properties = reportProperties,
            parameters = parameters,
            nsmap = nsmap,
            tables = tables,
            taxonomy = taxonomy,
            allowedDuplicates = metadata["documentInfo"].get("features", {}).get("xbrl:allowedDuplicates", "all")
        )

        modelReport = Report(taxonomy)
        facts = csvReport.loadTables(self.processor.resolver)
        for f in facts:
            modelReport.addFact(f)

        self.parseLinks(metadata, modelReport)

        modelReport.validate()

        for t in tables:
            for p in t.parameters:
                if p not in self.parameterReferences:
                    raise XBRLError("xbrlce:unreferencedParameter", "The table parameter '%s' is not referenced" % (p))
        
        self.validateDuplicates(modelReport, csvReport.allowedDuplicates)


    def validateDuplicates(self, modelReport, mode):
        if mode == 'none':
            modelReport.validateDuplicatesAllowNone()
        elif mode == 'complete':
            modelReport.validateDuplicatesAllowComplete()
        elif mode == 'consistent':
            modelReport.validateDuplicatesAllowConsistent()


    def getTaxonomy(self, metadata, url):
        taxonomy = metadata.get("documentInfo").get("taxonomy", [])
        if len(taxonomy) == 0:
            raise XBRLError("oime:noTaxonomy", "No taxonomy specified in metadata")

        schemaRefs = list(SchemaRef(urljoin(url, t)) for t in taxonomy)
        return self.processor.loadTaxonomy(schemaRefs)


    def loadMetaData(self, url):

        logger.debug("Loading xBRL-CSV metadata file from %s" % url)
        
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
                "documentType": None,
                "extends": None,
                "final": dict,
            },
            "tableTemplates": dict,
            "tables": dict,
            "dimensions": dict,
            "parameters": dict,
        }

        taxonomy = []
        for e in docInfo.get("extends", []):
            m = self.loadMetaData(urljoin(url, e))
            importedDocType = m["documentInfo"]["documentType"]
            if importedDocType != docType:
                raise XBRLError("xbrlce:multipleDocumentTypesInExtensionChain", "Document type for %s conflicts with document type for %s (%s vs %s)" % (e, url, importedDocType, docType))

            self.mergeDict(j, m, extensible, m["documentInfo"].get("final",{}).keys())

        final = docInfo.get("final", {})
        if "parameters" in final and j.get("parameterURL", None) is not None:
            raise XBRLError("xbrlce:unusableParameterURL", "Effective metadata of %s has parameterURL but final contains 'parameters'.  Importing metadata files will not be able to use parameterURL." % (url))

        return j

    def mergeDict(self, a, b, extensible, final, path = ""):
        for k, bv in b.items():
            keyPath = path + "/" + k
            isFinal = finalValues.get(keyPath, None) in final
            if k in extensible:
                ext = extensible[k]
                if type(ext) == dict:
                    # This object has children that are extensible, so recurse
                    self.mergeDict(a.setdefault(k, {}), b[k], ext, final, keyPath)

                elif ext == dict:
                    # This is an extensible dict, if a child appears in both, it must have the same value
                    if k in a:
                        # If it's final then it must be deep equal if present in both.
                        if isFinal and not deep_eq(a[k], bv):
                            raise XBRLError("xbrlce:illegalExtensionOfFinalProperty", "'%s' is final, but '%s' redefined with a different value." % (finalValues[keyPath], keyPath))
                        
                        for subKey in bv:
                            if subKey in a[k]:
                                if not deep_eq(a[k][subKey], bv[subKey]):
                                    raise XBRLError("xbrlce:conflictingMetadataValue", 'Conflicting value for %s ("%s" vs "%s")' % (k, json.dumps(a[k]), json.dumps(bv)))
                            else:
                                a[k][subKey] = bv[subKey]

                    else:
                        a[k] = bv

                elif ext == list:
                    # This is an extensible array, if it appears in both we concatenate, unless final, in which case require same value
                    if k in a:
                        # If it's final then it must be deep equal if present in both.
                        if isFinal and not deep_eq(a[k], bv):
                            raise XBRLError("xbrlce:illegalExtensionOfFinalProperty", "'%s' is final, but '%s' redefined with a different value." % (finalValues[keyPath], keyPath))

                    a[k] = bv + a.get(k, [])
                elif ext is not None:
                    raise ValueError("Unexpected value in extensible dict: %s" % bv)

            # Non-extensible property, require equality if present in both.
            elif k in a and not deep_eq(a[k], bv):
                raise XBRLError("xbrlce:illegalRedefinitionOfNonExtensibleProperty", "'%s' appears in multiple metadata files with different values" % k)
            else:
                a[k] = bv


    def parseProperties(self, propertyHolder, nsmap):
        properties = Properties(
                decimals = self.parseDecimals(propertyHolder),
                dimensions = self.parseDimensions(propertyHolder.get("dimensions",{}), nsmap)
                )
        return properties

    def parseDecimals(self, propertyHolder):
        if "decimals" not in propertyHolder:
            return None

        val = propertyHolder.get("decimals")
        if val is None:
            # JSON null
            raise XBRLError("xbrlce:invalidDecimalsValue", "'null' is not a valid decimals value")

        if type(val) == int:
            return val
        if type(val) == float:
            raise XBRLError("xbrlce:invalidDecimalsValue", "'%s' is not a valid decimals value: must be an integer" % str(val))

        processedValue = processSpecialValues(val)

        if processedValue in (None, ""):
            raise XBRLError("xbrlce:invalidDecimalsValue", "'%s' is not a valid decimals value" % val)

        if isinstance(processedValue, ExplicitNoValue):
            return ExplicitNoValue

        assert type(processedValue) == str

        if processedValue.startswith("$"):
            processedValue = self.parseReference(processedValue)
        else:
            raise XBRLError("xbrlce:invalidDecimalsValue", "'%s' is not a valid decimals value" % val)

        return processedValue



    def parseDimensions(self, dimensions, nsmap):
        processedDims = dict()
        for name, value in dimensions.items():
            if name.startswith("xbrl:"):
                raise XBRLError("xbrlce:invalidJSONStructure", "Invalid dimension QName '%s'.  Dimension QNames must not use the 'xbrl' namespace (%s)" % (name, NS.xbrl))

            dimQName = qname(name, nsmap = { None: NS.xbrl, **nsmap })

            processedValue = processSpecialValues(value)
            if type(processedValue) == str:
                if processedValue.startswith("$"):
                    if processedValue.startswith("$$"):
                        processedValue = processedValue[1:]
                    else:
                        processedValue = self.parseReference(processedValue)

            processedDims[dimQName] = processedValue


        return processedDims
         

    def parseParameters(self, src):
        return Parameters(src.get("parameters", {}))


    def parseReportParameters(self, primaryURL, metadata):
        reportParameters = self.parseParameters(metadata)
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
            

    def validatePropertyGroups(self, columns):
        # Build a map of the properties used by each PropertyGroupColumn
        usedProperties = dict()
        for pgcol in (c for c in columns.values() if isinstance(c, PropertyGroupColumn)):
            pp = Properties()
            for p in pgcol.propertyGroups.values():
                pp.add(p)
            usedProperties[pgcol.name] = pp
        
        for col in (c for c in columns.values() if isinstance(c, FactColumn)):
            pp = Properties()
            for pf in col.propertiesFrom:
                try:
                    pp.add(usedProperties[pf], raiseOnConflict = True)
                except PropertyGroupMergeDecimalsConflict:
                    raise XBRLError("xbrlce:repeatedPropertyGroupDecimalsProperty", "The decimals property is specified by multiple property groups columns referenced from %s (%s)" % (col.name, ", ".join(col.propertiesFrom)))
                except PropertyGroupMergeDimensionsConflict as e:
                    raise XBRLError("xbrlce:repeatedPropertyGroupDimension", "The '%s' dimension is specified by multiple property groups columns referenced from %s (%s)" % (str(e.dimension), col.name, ", ".join(col.propertiesFrom)))

    def parseLinks(self, metadata, modelReport):

        docInfo = metadata.get("documentInfo")
        
        linkGroups = docInfo.get("linkGroups",{})
        validateURIMap(linkGroups)

        linkTypes = docInfo.get("linkTypes",{})
        validateURIMap(linkTypes)

        links = metadata.get("links", {})
        #print(list(modelReport.facts.keys()))
        for linkType, groups in links.items():
            linkTypeURI = linkTypes.get(linkType)
            if linkTypeURI is None:
                raise XBRLError("xbrlce:unknownLinkType", "The link type '%s' is not defined" % linkType)
            for group, srcFactIds in groups.items():
                linkGroupURI = linkGroups.get(group)
                if linkGroupURI is None:
                    raise XBRLError("xbrlce:unknownLinkGroup", "The link group '%s' is not defined" % group)

                for srcId, targetIds in srcFactIds.items():
                    src = modelReport.facts.get(srcId)
                    if src is None:
                        raise XBRLError("xbrlce:unknownLinkSource", "No fact with id '%s' exists in the report." % srcId)

                    for targetId in targetIds:
                        target = modelReport.facts.get(targetId)
                        if target is None:
                            raise XBRLError("xbrlce:unknownLinkTarget", "No fact with id '%s' exists in the report." % targetId)
                        src.links.setdefault(linkTypeURI, {}).setdefault(linkGroupURI, []).append(target)

    def parseReference(self, value):
        processedValue = parseReference(value)
        if isinstance(processedValue, ParameterReference):
            self.parameterReferences.add(processedValue.name)
        return processedValue

def deep_eq(a, b):
    if type(a) != type(b):
        return False

    if type(a) in {str, float, int}:
        return a == b

    if type(a) == list:
        if len(a) != len(b):
            return False
        for i, v in enumerate(a):
            if not deep_eq(v,b[i]):
                return False
        return True

    if type(a) == dict:
        if a.keys() != b.keys():
            return False
        for k in a.keys():
            if not deep_eq(a[k] ,b[k]):
                return False
        return True

    if a == None:
        # Should always be true if they're both NoneType
        return b == None

    raise ValueError("Unexpected type %s" % type(a))


