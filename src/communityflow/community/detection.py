from networkx.algorithms import community
from communityflow import Sequence

class CommunityDetector():
    '''
    run Community Detection on a graph

    return an array of dict, where each dictionary key is the community and the value is an array of members:

        {community1: [members],
         community2: [members],
         ...}

    '''
    def communities(self, graph):
        return {}
    
    def inspect(self, communities):
        for community in communities:
            print(f"community: {community} members: {sorted(communities[community])}")

class GreedyModularity(CommunityDetector):
    '''
    From NetworkX docs:
    
    Find communities in graph using Clauset-Newman-Moore greedy modularity maximization. 
    This method currently supports the Graph class and does not consider edge weights.

    Greedy modularity maximization begins with each node in its own community and joins 
    the pair of communities that most increases modularity until no such pair exists.
    '''
    def __init__(self):
        pass
    
    def communities(self, graph):
        sequence = Sequence(0)
        modularity = community.greedy_modularity_communities(graph)
        return {sequence(): list(group) for group in modularity}