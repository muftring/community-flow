class Partitioner:
    def partition(self, value):
        return 0

class PsdPartitioner(Partitioner):
    def __init__(self, period=3600):
        self.group = 0
        self.start = 0
        self.end = 0
        self.period = period
        pass
    def partition(self, value):
        if value > self.end:
            self.group += 1
            self.begin = value
            self.end = self.begin + self.period
        return self.group

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(begin=0, end=0, group=0)
def psd_partition(value, period=3600):
    if value > psd_partition.end:
        psd_partition.group += 1
        psd_partition.begin = value
        psd_partition.end = psd_partition.begin + period
    return psd_partition.group

def partitioner_function(df, column, function):
    f = eval("lambda x: " + function)
    return df[column].apply(lambda x: int(f(x)))

def partition(df, column, partitioner):
    if isinstance(partitioner, Partitioner):
        df['__group__'] = df[column].apply(partitioner.partition)
    elif callable(partitioner):
        df['__group__'] = df[column].apply(partitioner)
    elif type(partitioner) is str:
        df['__group__'] = partitioner_function(df, column, partitioner)
    return [x.drop('__group__', axis=1) for x in [x for _, x in df.groupby('__group__')]]
