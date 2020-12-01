import csv
from .csvdialect import XBRLCSVDialect
from .validators import isValidIdentifier, isValidQName
from .column import FactColumn, PropertyGroupColumn
from .specialvalues import processSpecialValues
from .values import ParameterReference, RowNumberReference, ExplicitNoValue, parseNumericValue, NotPresent
from .properties import Properties
from .period import parseCSVPeriodString
from xbrl.xml import qname, qnameset
from xbrl.xbrlerror import XBRLError
from xbrl.common import parseUnitString, parseSQName, InvalidSQName
from xbrl.const import NS
from xbrl.model.taxonomy import NoteConcept
import urllib.error
import io
import datetime

class Table:

    def __init__(self, name, template, url, parameters, optional = False):
        self.name = name
        self.template = template
        self.url = url
        self.parameters = parameters
        self.optional = optional

    def loadData(self, resolver):
        try:
            with resolver.open(self.url) as fin:
                reader = csv.reader(io.TextIOWrapper(fin, "utf-8-sig"), XBRLCSVDialect)
                headerRow = next(reader, [])
                columns = dict()
                colMap = dict()
                factColumns = []
                propertyGroupColumns = []
                for (index, h) in enumerate(headerRow):
                    if h != "":
                        if not isValidIdentifier(h):
                            raise XBRLError("xbrlce:invalidHeaderValue", "'%s' is not a valid column header" % h)
                        column = self.template.columns.get(h)
                        if column is None:
                            raise XBRLError("xbrlce:unknownColumn", "Column '%s' in table '%s' is not defined" % (h, self.name))
                        if h in columns:
                            raise XBRLError("xbrlce:repeatedColumnIdentifier", "Column '%s' in table '%s' is repeated" % (h, self.name))
                        columns[h] = column
                        colMap[h] = index
                        
                        if isinstance(column, FactColumn):
                            factColumns.append(column)

                        if isinstance(column, PropertyGroupColumn):
                            propertyGroupColumns.append(column)

                rowIds = set()
                rowNum = 0
                for row in reader:
                    rowNum += 1
                    for pgc in propertyGroupColumns:
                        # Ensure that illegalUseOfNone gets raised for PG columns
                        processSpecialValues(row[colMap[pgc.name]], allowNone = False)

                    rowId = None
                    if self.template.rowIdColumn is not None:
                        rowIdCol = colMap.get(self.template.rowIdColumn.name)
                        if rowIdCol is not None:
                            rowId = row[rowIdCol]
                            # We deal with empty cells later, if the row has a value.
                            if rowId != "" and not isValidIdentifier(rowId):
                                raise XBRLError("xbrlce:invalidRowIdentifier", "'%s' is not a valid identifier" % rowId)
                    if rowId is None:
                        rowId = 'r%d' % rowNum
                    
                    if rowId in rowIds:
                        raise XBRLError("xbrlce:repeatedRowIdentifier", "Row identifier '%s' is repeated" % rowId)
                    rowIds.add(rowId)

                    for fc in factColumns:
                        try:
                            rawValue = row[colMap[fc.name]]
                        except IndexError:
                            continue
                        if rawValue == "":
                            continue


                        if rowId == "":
                            raise XBRLError("xbrlce:missingRowIdentifier", "Row does not have a row identifier")

                        factValue = processSpecialValues(rawValue, allowNone = False)

                        column = self.template.columns[fc.name]

                        propertyGroupProperties = Properties()

                        for pg in column.propertiesFrom:
                            if pg in colMap:
                                # Not an error for the column to not be present in the table (#457)
                                pgname = row[colMap[pg]]
                                if pgname != "":
                                    pgcoldef = self.template.columns[pg]
                                    properties = pgcoldef.propertyGroups.get(pgname)
                                    if properties is None:
                                        raise XBRLError("xbrlce:unknownPropertyGroup", "Could not find property group '%s' in property group column '%s'" % (pgname, pg))

                                    # Merge into propertyGroupProperties
                                    propertyGroupProperties.add(properties)



                        dims = column.getEffectiveDimensions(propertyGroupProperties)
                        factDims = {}
                        for k, v in dims.items():
                            if isinstance(v, ParameterReference):
                                val = self.getParameterValue(v, row, colMap)

                            elif isinstance(v, RowNumberReference):
                                val = str(rowNum)
                            else:
                                val = v

                            if not isinstance(val, ExplicitNoValue):
                                factDims[k] = val

                        decimals = self.template.columns[fc.name].getEffectiveDecimals(propertyGroupProperties)
                        if isinstance(decimals, ParameterReference):
                            decimals = self.getParameterValue(decimals, row, colMap)
                        if type(decimals) == str:
                            try:
                                decimals = int(decimals)
                            except ValueError:
                                raise XBRLError("xbrlce:invalidDecimalsValue", "'%s' is not a valid decimals value" % decimals)

                        concept = self.getConcept(factDims)
                        unit = self.getUnit(factDims)
                        period = self.getPeriod(factDims)
                        entity = self.getEntity(factDims)

                        if concept.isNumeric:
                            (factValue, decimals) = parseNumericValue(factValue, decimals)

                        # XXX This is should move to model-level validation
                        if concept == NoteConcept:
                            if set(factDims.keys()) & qnameset("xbrl", {"period", "entity"}):
                                raise XBRLError("oime:misplacedNoteFactDimension", "xbrl:note facts must not have the Period or Entity core dimensions")
                            if qname("xbrl:language") not in factDims.keys():
                                raise XBRLError("oime:missingLanguageForNoteFact", "xbrl:note facts must have the Language core dimensions")
                            for k in factDims.keys():
                                if k.namespace != NS.xbrl:
                                    raise XBRLError("oime:misplacedNoteFactDimension", "xbrl:note facts must not have any taxonomy defined dimensions (%s)" % str(k))


        except urllib.error.URLError as e:
            if isinstance(e.reason, FileNotFoundError):
                if not self.optional:
                    raise XBRLError("xbrlce:missingRequiredCSVFile", "File '%s' does not exist" % self.url)
            else:
                raise e
        except csv.Error as e:
            raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))
        except UnicodeDecodeError as e:
            raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))

    def getUnit(self, factDims):
        unit = factDims.get(qname("xbrl:unit"), NotPresent)
        if unit is NotPresent:
            unit = None
        else:
            (nums, denoms) = parseUnitString(unit, self.template.report.nsmap)
            if nums == [ qname("xbrli:pure") ] and denoms == []:
                raise XBRLError("oime:illegalPureUnit", "Pure units must not be specified explicitly")
        return unit

    def getConcept(self, factDims):
        conceptNameStr = factDims.get(qname("xbrl:concept"), NotPresent)
        if conceptNameStr is NotPresent:
            raise XBRLError("oime:missingConceptDimension", "No concept dimension for fact")
        if conceptNameStr is None:
            raise XBRLError("xbrlce:invalidJSONStructure", "Concept dimension must not be nil")
        if not isValidQName(conceptNameStr):
            raise XBRLError("xbrlce:invalidConceptQName", "'%s' is not a valid QName" % conceptNameStr)

        conceptName = qname(conceptNameStr, { "xbrl": NS.xbrl, **self.template.report.nsmap})

        concept = self.template.report.taxonomy.concepts.get(conceptName)
        if concept is None:
            raise XBRLError("oime:unknownConcept", "Concept %s not found in taxonomy" % str(conceptName))

        return concept

    def getPeriod(self, factDims):
        period = factDims.get(qname("xbrl:period"), NotPresent)
        if period is NotPresent:
            return None

        # #nil or JSON null
        if period is None:
            raise XBRLError("xbrlce:invalidPeriodRepresentation", "nil is not a valid period value")

        if isinstance(period, datetime.datetime):
            # Was obtained as the target of a parameter reference with period specifier, and has already been converted to datetime
            return period
        else:
            return parseCSVPeriodString(period)


    def getEntity(self, factDims):
        entityStr = factDims.get(qname("xbrl:entity"), NotPresent)
        if entityStr is NotPresent:
            return None

        if entityStr is None:
            raise XBRLError("xbrlce:invalidSQName", "Entity dimension must not be nil")

        try:
            (scheme, identifier) = parseSQName(entityStr, self.template.report.nsmap)
        except InvalidSQName as e:
            raise XBRLError("xbrlce:invalidSQName", str(e))




    def getParameterValue(self, p, row, colMap):
        param = p.name
        if param not in self.template.columns and param not in self.parameters and param not in self.template.report.parameters:
            raise XBRLError("xbrlce:invalidReferenceTarget", "Could not resolve parameter '%s'" % param)
        paramCol = colMap.get(param)
        if paramCol is not None and row[paramCol] != "":
            val = row[paramCol]
        else:
            val = self.parameters.get(param, self.template.report.parameters.get(param, ExplicitNoValue()))
        if type(val) == str:
            val = processSpecialValues(val)

        if p.periodSpecifier:
            period = parseCSVPeriodString(val)
            if None in period:
                raise XBRLError("xbrlce:referenceTargetNotDuration", "'%s' is referenced by parameter '%s' with a period specified of '%s' but does not denote a duration." % (val, param, p.periodSpecifier))

            if p.periodSpecifier == 'start':
                return period[0]
            else:
                return period[1]

        return val


