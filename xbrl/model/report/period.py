class PeriodDimension:

    pass

class DurationPeriod(PeriodDimension):

    def __init__(self, start = None, end = None):
        self.start = start
        self.end = end

class InstantPeriod(PeriodDimension):

    def __init__(self, instant):
        self.instant = instant
