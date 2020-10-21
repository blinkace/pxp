import re
from xbrl.xbrlerror import XBRLError
import dateutil.parser
import datetime

class IXTransformError(Exception):
    pass

class IXTransform:

    def __init__(self, name):
        self.name = name

    def validate(self, vin):
        try: 
            self.transform(vin)
        except IXTransformError:
            return False
        return True

    def transform(self, vin):
        vin = " ".join(vin.split())
        if re.fullmatch(type(self).INPUT_RE, vin) is None:
            raise IXTransformError("Input '%s' does not match input format for %s transform" % (vin, self.name))
        return self._transform(vin)


class DateTransform(IXTransform):

    JP_ERAS = {
            '明': 1868,
            '大': 1912,
            '昭': 1926,
            '平': 1989,
            '令': 2019
            }

    def _transform(self, vin):
        m = re.fullmatch(type(self).INPUT_RE, vin)
        if m is None:
            raise XBRLError("ixe:invalidTransform", "Transform input '%s' does not match pattern" % vin)

        if 'M' in m.groupdict():
            mi = int(m.groupdict().get('M'))
        else:
            # Look for match group with name "Mn" where n denotes match number
            mi = next((int(k[1:]) for k, v in m.groupdict().items() if k.startswith('M') and v is not None), None)

        year = m.groupdict().get('Y')
        if year is None:
            yi = 2000
            ystr = "-"
        else:
            # Japanese era
            if 'E' in m.groupdict():
                yi = int(year) if year != '元' else 1
                era = m.groupdict().get('E')
                yi = yi + DateTransform.JP_ERAS[era[0]] - 1

            elif len(year) <= 2:
                yi = int(year) + 2000
            else:
                yi = int(year)

            ystr = "%04d" % yi

        if 'D' in m.groupdict():
            di = int(m.groupdict().get('D'))
            dstr = "-%02d" % di
        else:
            di = 1
            dstr = ""

        out = "%s-%02d%s" % (ystr, mi, dstr)
        try:
            t = datetime.datetime(yi, mi, di)
        except ValueError:
            raise IXTransformError("'%s' is not a valid date for %s transform" % (vin, self.name))
        return out

class TRRegistry:

    def __init__(self):

        self.transforms = dict()
        for c in type(self).TRANSFORMS:
            name = c.__name__.lower()
            self.transforms[name] = c(name)

    @property
    def ns(self):
        return type(self).NAMESPACE

    def getTransform(self, name):
        if name.namespace != self.ns:
            return None

        return self.transforms.get(name.localname, None)

