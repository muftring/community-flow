import networkx as nx
from .nodemap import NodeMap

class GraphCreator():
    def __call__(self, data):
        return self.create(data)
    
    def create(self, data):
        return nx.Graph()

class EdgeListDataFrame(GraphCreator):
    def __init__(self, descriptor, node_map = None):
        super().__init__()
        self.descriptor = descriptor
        self.node_map = node_map if node_map is not None else NodeMap()
    
    #def __init__(self, descriptor, df, node_map = None):
    #    super().__init__(descriptor, node_map)
    #    self.df = df
    #    self.descriptor = descriptor
    #    self.node_map = node_map if node_map is not None else NodeMap()
    #    self.graph = self.create(self.df)
        
    def __call__(self, df):
        return self.create(df)
    
    def directed(self):
        return self.descriptor.directed()
    
    def weighted(self):
        return self.descriptor.weighted()
    
    def _source_id(self):
        return self.descriptor.source_id()
    
    def _source_attributes(self):
        return self.descriptor.source_attributes()
    
    def _target_id(self):
        return self.descriptor.target_id()
    
    def _target_attributes(self):
        return self.descriptor.target_attributes()
    
    def _labels_for(self, attributes):
        return [self.descriptor.label(a) for a in attributes]
        
    def _source_labels(self):
        return self._labels_for([self.descriptor.source_id()] + self.descriptor.source_attributes())
    
    def _target_labels(self):
        return self._labels_for([self.descriptor.target_id()] + self.descriptor.target_attributes())
        
    def _map(self, data, labels):
        '''
        Maps an n-tuple of attributes to a dict of name-value-pairs. The length of 'data' and 'labels' should be
        equal, and the position of values in 'data' must correspond to the position of values in 'labels' for 
        correct mapping.

        e.g., (1, 'a', 'city') -> {'label': 1, 'type': 'a', 'location': 'city'}
        '''
        return {labels[i]:data[i] for i in range(len(data))}

    def _extract(self, df, index, attributes=[]):
        '''
        Returns a set of n-tuple values: first the index which is the origin data identifier (i.e., the label), 
        and then any desired attributes.

        This is achieved by selecting the columns from the DataFrame, grouping by the columns (to reduce duplicates),
        aggregating a count (which is unused), and finally getting the resulting index which produces the n-tuple.
        '''
        columns = [index] + attributes
        #for attribute in attributes: columns.append(attribute)
        return set(df[columns].groupby(columns).count().index)

    def _nodes_in(self, df, index, columns, labels):
        '''
        Produces a dictionary keyed by the node label -- the origin data identifier. Each dict entry 
        contains node attributes mapped to the desired attribute names.
        '''
        return {x[0]:self._map(x, labels) for x in self._extract(df, index, columns)}

    def _nodes(self, df):
        '''
        Returns the merge of two dictionaries (source and target) using the union operator.
        See: https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-taking-union-of-dictiona
        '''
        s1 = self._nodes_in(df, self._source_id(), self._source_attributes(), self._source_labels())
        s2 = self._nodes_in(df, self._target_id(), self._target_attributes(), self._target_labels())
        return {**s1, **s2}

    def nodes(self, df):
        return [(self.node_map.add(label), attributes) 
                for label, attributes in self._nodes(df).items()]

    def _edge_attributes(self, row):
        # TODO: implement this function
        # extract or compute weight
        # - computed by getting the count from the groupby operation: {'weight':row[0]} if weighted else {}
        return {}
    
    def _edges(self, df):
        '''
        Group the DataFrame by the source and target columns, and count the unique instances.
        Iterating over the rows, the index is a tuple of the grouped columns (source and target),
        which corresponds to what will be the node identifiers (node 0, 1, 2, ...). The count
        aggregation can be a proxy for edge weight, if so desired.
        '''
        weighted = self.weighted()
        e = df.groupby([self._source_id(), self._target_id()]).count()
        return {(index[0],index[1]):{'weight':row[0]} if weighted else {} for index,row in e.iterrows()}

    def edges(self, df):
        return [(self.node_map.add(edge[0]), self.node_map.add(edge[1]), attributes) 
                for edge, attributes in self._edges(df).items()]

    #def node_map(self):
    #    return self.node_map

    def create(self, df):
        graph = nx.Graph()
        graph.add_nodes_from(self.nodes(df))
        graph.add_edges_from(self.edges(df))
        return graph