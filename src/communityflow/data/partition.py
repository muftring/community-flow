class Partitioner():
    def __init__(self):
        pass
    def partition(self, data):
        return None

class DataFramePartitioner(Partitioner):
    def __init__(self, column, grouper):
        self.column = column
        self.grouper = grouper
    
    def __call__(self, df):
        return self.partition(df)
    
    def partition(self, df):
        # set the `__group__` column to the group value, provided by the Grouper object
        df['__group__'] = df[self.column].apply(self.grouper.group)
        # group the DataFrame by the `__group__` column value
        # fetch the results from the DataFrameGroupBy object: an index and a DataFrame
        # drop the `__group__` column from the resulting DataFrames
        # and return a list of DataFrames, where each item in the list represents one partition
        return [x.drop('__group__', axis=1) for x in [x for _, x in df.groupby('__group__')]]
