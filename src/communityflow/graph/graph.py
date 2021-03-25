import networkx as nx
from .nodemap import NodeMap

# TODO: implement generator function which returns an iterator

def create_node(index, label, **kwargs):
    node = (index, {'label': label})
    for key, value in kwargs.items():
        node[1][key] = value
    #print(">>>DEBUG>>>","create_node()","node:",node)
    return node

def nodes_from(row, node_map):
    nodes = []
    nodes.append(create_node(node_map.add(row.Source), row.Source, room=row.SourceRoom))
    nodes.append(create_node(node_map.add(row.Target), row.Target, room=row.TargetRoom))
    #print(">>>DEBUG>>>","nodes_from()","nodes:",nodes)
    return nodes

def add_nodes(graph, node_map, row):
    nodes = nodes_from(row, node_map)
    #print(">>>DEBUG>>>","add_nodes()","nodes:",nodes)
    graph.add_nodes_from(nodes)

def edges_from(row, node_map):
    edges = []
    edges.append((node_map.index(row.Source), node_map.index(row.Target)))
    return edges

def add_edges(graph, node_map, row):
    edges = edges_from(row, node_map)
    graph.add_edges_from(edges)

def create_graph(partition, node_map):
    graph = nx.Graph()
    for index,row in partition.iterrows():
        add_nodes(graph, node_map, row)
        add_edges(graph, node_map, row)
    return graph

# input: a list of graph partitons
# output: a list of graph objects

def create_graphs(partitions):
    node_map = NodeMap()
    graphs = [create_graph(partition, node_map) for partition in partitions]
    return (graphs, node_map)