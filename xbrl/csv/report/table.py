import csv
from .csvdialect import XBRLCSVDialect
from .validators import isValidIdentifier
from .column import FactColumn, PropertyGroupColumn
from .specialvalues import processSpecialValues
from .values import ParameterReference, RowNumberReference, ExplicitNoValue
from .period import parseCSVPeriodString
from xbrl.xml import qname
from xbrl.xbrlerror import XBRLError
from xbrl.common import parseUnitString
import urllib.error
import io

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

                rowNum = 0
                for row in reader:
                    rowNum += 1
                    for pgc in propertyGroupColumns:
                        # Ensure that illegalUseOfNone gets raised for PG columns
                        processSpecialValues(row[colMap[pgc.name]], allowNone = False)

                    for fc in factColumns:
                        try:
                            rawValue = row[colMap[fc.name]]
                        except IndexError:
                            next
                        if rawValue == "":
                            next
                        value = processSpecialValues(rawValue, allowNone = False)
                        dims = self.template.columns[fc.name].getEffectiveDimensions()
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

                        decimals = self.template.columns[fc.name].getEffectiveDecimals()
                        if isinstance(decimals, ParameterReference):
                            decimals = self.getParameterValue(decimals, row, colMap)
                        if type(decimals) == str:
                            try:
                                decimals = int(decimals)
                            except ValueError:
                                raise XBRLError("xbrlce:invalidDecimalsValue", "'%s' is not a valid decimals value" % decimals)


                        if qname("xbrl:concept") not in factDims:
                            raise XBRLError("oime:missingConceptDimension", "No concept dimension for fact in column %s" % fc.name)

                        unit = factDims.get(qname("xbrl:unit"))
                        if unit is not None:
                            (nums, denoms) = parseUnitString(unit, self.template.report.nsmap)
                            if nums == [ qname("xbrli:pure") ] and denoms == []:
                                raise XBRLError("oime:illegalPureUnit", "Pure units must not be specified explicitly")

                        if qname("xbrl:period") in factDims:
                            period = factDims.get(qname("xbrl:period"))

                            # #nil or JSON null
                            if period is None:
                                raise XBRLError("xbrlce:invalidPeriodRepresentation", "nil is not a valid period value")

                            if period is not None:
                                parseCSVPeriodString(period)



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



    def getParameterValue(self, p, row, colMap):
        param = p.name
        if param not in self.template.columns and param not in self.parameters and param not in self.template.report.parameters:
            raise XBRLError("xbrlce:invalidParameterReference", "Could not resolve parameter '%s'" % param)
        paramCol = colMap.get(param)
        if paramCol is not None and row[paramCol] != "":
            val = row[paramCol]
        else:
            val = self.parameters.get(param, self.template.report.parameters.get(param, ExplicitNoValue()))
        if type(val) == str:
            val = processSpecialValues(val)
        return val

