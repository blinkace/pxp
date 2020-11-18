import re

namestartchar = r'[:A-Z_a-z\xC0-\xD6\xD8-\xF6\xF8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
namechar = r'(?:' + namestartchar + r'|[-.0-9\xB7\u0300-\u036F\u203F-\u2040])'
ncnameRegex = re.compile(r'^' + namestartchar + namechar + r'*$')

def isValidIdentifier(i):
    return ncnameRegex.match(i) is not None and "." not in i


