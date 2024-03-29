from .validation_message import ValidationMessage, ValidationSeverity
from xbrl.xml import qname

class ValidationResult:

    def __init__(self):
        self.messages = []

    def add(self, message: ValidationMessage):
        self.messages.append(message)

    def merge(self, other):
        for m in other.messages:
            self.add(m)

    def __repr__(self):
        s = ''
        for m in self.messages:
            s += repr(m) + "\n"
        return s

    def addException(self, e):
        self.messages.append(ValidationMessage(e.code, ValidationSeverity.FATAL, e.message))

    def addFatalError(self, code, message):
        self.messages.append(ValidationMessage(qname(code), ValidationSeverity.ERROR, message))

    def addError(self, code, message):
        self.messages.append(ValidationMessage(qname(code), ValidationSeverity.ERROR, message))

    def addWarning(self, code, message):
        self.messages.append(ValidationMessage(qname(code), ValidationSeverity.WARNING, message))

    def addQualityIssue(self, code, message):
        self.messages.append(ValidationMessage(qname(code), ValidationSeverity.QUALITY, message))
            
    def maxSeverity(self):
        if len(self.messages) > 0:
            return max(m.severity for m in self.messages)
        return 0

    @property
    def isValid(self):
        return self.maxSeverity() < ValidationSeverity.ERROR

