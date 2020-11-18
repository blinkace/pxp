import csv

class XBRLCSVDialect(csv.Dialect):
    doublequote = True
    escapechar = None
    delimiter = ","
    quotechar = '"'
    strict = True
    quoting = csv.QUOTE_MINIMAL
    lineterminator = "\r\n"
