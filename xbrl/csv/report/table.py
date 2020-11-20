import csv
from .csvdialect import XBRLCSVDialect
from .validators import isValidIdentifier
from .column import FactColumn
from .specialvalues import processSpecialValues
from .values import ParameterReference
from xbrl.xbrlerror import XBRLError
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

                for row in reader:
                    for fc in factColumns:
                        try:
                            rawValue = row[colMap[fc.name]]
                        except IndexError:
                            next
                        value = processSpecialValues(rawValue, allowNone = False)
                        dims = self.template.columns[fc.name].getEffectiveDimensions()
                        for k, v in dims.items():
                            if isinstance(v, ParameterReference):
                                param = v.name
                                if param not in self.template.columns and param not in self.parameters and param not in self.template.report.parameters:
                                    raise XBRLError("xbrlce:invalidParameterReference", "Could not resolve parameter '%s'" % param)

                        



        except urllib.error.URLError as e:
            if isinstance(e.reason, FileNotFoundError):
                if not self.optional:
                    raise XBRLError("xbrlce:missingRequiredCSVFile", "File '%s' does not exist" % self.url)
            raise e
        except csv.Error as e:
            raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))
        except UnicodeDecodeError as e:
            raise XBRLError("xbrlce:invalidCSVFileFormat", "Invalid CSV file '%s': %s" % (self.url, str(e)))



