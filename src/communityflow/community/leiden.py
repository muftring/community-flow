import leidenalg as leiden
import pyintergraph
from communityflow import Sequence
from communityflow.community.detection import CommunityDetector

class Leiden(CommunityDetector):
    '''
    References: https://leidenalg.readthedocs.io/en/stable/index.html
                https://gitlab.com/luerhard/pyintergraph
    '''
    def __init__(self):
        pass
    
    def grouping(self, partitioning):
        s = Sequence(0)
        return {s(): community for community in partitioning}
    
    def communities(self, graph):
        return self.grouping(leiden.find_partition(pyintergraph.nx2igraph(graph), leiden.ModularityVertexPartition))
