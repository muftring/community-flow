import pandas as pd

class NodeMap():

    def __init__(self):
        self.df = pd.DataFrame(columns=['label'])
        pass
    
    def add(self, label):
        self.df = self.df.append({'label': label}, ignore_index=True) if label not in self.df.values else self.df
        return self.index(label)
    
    def index(self, label):
        try:
            return self.df.query("label == {}".format(label)).index[0]
        except IndexError:
            return None
    
    def label(self, index):
        try:
            return self.df.iloc[index].label
        except IndexError:
            return None
   
    def dataframe(self):
        return self.df.copy(deep=True)
