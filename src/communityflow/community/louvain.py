import community as louvain
from communityflow import Sequence
from communityflow.community.detection import CommunityDetector

class Louvain(CommunityDetector):
    '''
    References: https://python-louvain.readthedocs.io/en/latest/
    '''
    def __init__(self):
        pass
    
    # input: a dict, with key = node, value = community
    # result: a dict, with key = community, value = list of nodes
    def grouping(self, partitioning):
        communities = {}
        for node in partitioning:
            group = partitioning[node]
            communities.setdefault(group, []).append(int(node))
        # remove any duplicates in the groups by making each value a set
        for group in communities:
            communities[group] = set(communities[group])
        return communities
    
    def communities(self, graph):
        return self.grouping(louvain.best_partition(graph))
