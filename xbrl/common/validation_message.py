from enum import IntEnum
import lxml.etree as etree
from xbrl.const import PREFIX

class ValidationSeverity(IntEnum):
    FATAL = 4
    ERROR = 3
    WARNING = 2
    QUALITY = 1

class ValidationMessage:

    def __init__(self, code: etree.QName, severity: ValidationSeverity, message: str):
        self.code = code
        self.severity = severity
        self.message = message


    @property
    def code_as_qname(self):
        return "%s:%s" % (PREFIX[self.code.namespace], self.code.localname)

    def __repr__(self):
        return "%s [%s] %s" % (self.severity.name, self.code_as_qname, self.message)



