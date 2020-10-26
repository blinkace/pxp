from .dimensions import CoreDimension

class PeriodCoreDimension(CoreDimension):
    def __init__(self):
        super().__init__("period")
        self.isDuration = False


class DurationPeriod(PeriodCoreDimension):

    def __init__(self, start = None, end = None):
        super().__init__()
        self.start = start
        self.end = end
        self.isDuration = True

    @property
    def stringValue(self):
        return "%s/%s" % (self.start.isoformat(), self.end.isoformat())

class InstantPeriod(PeriodCoreDimension):

    def __init__(self, instant):
        super().__init__()
        self.instant = instant

    @property
    def stringValue(self):
        return self.instant.isoformat()
