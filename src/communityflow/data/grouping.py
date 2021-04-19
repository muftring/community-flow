class Grouper:
    def group(self, value):
        return 0

class PeriodGrouper(Grouper):
    '''
    To be used when partition values are monotonically increasing,
    and do not necessarily start at zero.
    '''
    def __init__(self, period=3600):
        self.segment = 0
        self.start = 0
        self.end = 0
        self.period = period
        pass
    def group(self, value):
        if value > self.end:
            self.segment += 1
            self.begin = value
            self.end = self.begin + self.period
        return self.segment

class ExpressionGrouper(Grouper):
    '''
    To be used when a simple expression can or should be used to determine
    the partition number. Example: 'x/3600' would divide a numeric value which
    represnets a value in seconds to determine partition assignment on an
    hour boundary.
    '''
    def __init__(self, expression):
        self.function = eval("lambda x: " + expression)
    
    def group(self, value):
        return int(self.function(value))
