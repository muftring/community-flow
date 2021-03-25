import networkx as nx
import pandas as pd
from .nodemap import NodeMap

def nodes_in_partition(partition, source='Source', target='Target'):
    return set(partition[source].unique()).union(partition[target].unique())

def map_node_attributes(data, labels):
    return {labels[i]:data[i] for i in range(len(data))}

def extract_node_attributes(partition, index, attributes=[]):
    columns = [index]
    for attribute in attributes: columns.append(attribute)
    return set(partition[columns].groupby(columns).count().index)

def node_attributes_in_partition(partition, index, columns, labels):
    return {x[0]:map_node_attributes(x, labels) for x in extract_node_attributes(partition, index, columns)}

def node_attributes(partition):
    s1 = node_attributes_in_partition(partition, 'Source', ['SourceRoom'], ['label','room'])
    s2 = node_attributes_in_partition(partition, 'Target', ['TargetRoom'], ['label','room'])
    return {**s1, **s2}

def edges_in_partition(partition, source='Source', target='Target', weighted=False):
    e = partition.groupby([source, target]).count()
    edges = {(index[0],index[1]):{'weight':row[0]} if weighted else {} for index,row in e.iterrows()}
    return edges

def create_graph_faster(partition, node_map):
    graph = nx.Graph()
    nodes = [(node_map.add(label), attributes) for label, attributes in node_attributes(partition).items()]
    graph.add_nodes_from(nodes)
    edges = [(node_map.add(edge[0]), node_map.add(edge[1]), attributes) for edge, attributes in edges_in_partition(partition).items()]
    graph.add_edges_from(edges)
    return graph

def create_graphs_faster(partitions):
    node_map = NodeMap()
    graphs = [create_graph_faster(partition, node_map) for partition in partitions]
    return (graphs, node_map)
