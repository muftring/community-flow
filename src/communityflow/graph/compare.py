def extract(graph):
    '''
    Generate a dictionary from a NetworkX Graph.
    
    The key is the index (primary node identifier) of the node in the graph.
    The value is a dict with index, label (original node identifier), room (a node attribute from
    the source data), and a list of neighbors (by graph index value). 
    '''
    result = {}
    for node in graph.nodes:
        result[node] = {'index': node, 
                        'label': graph.nodes[node]['label'], 
                        'room':  graph.nodes[node]['room'], 
                        'neighbors': [edge[1] for edge in graph.edges(nbunch=node)]}
    return result

def transform(extract):
    '''
    Transforms the Graph extract, replacing all Graph index values with original dource data labels.
    
    The result is a dictionary, where the key is a node label and the value is a dict with room and a sored
    list of neighbors (labels, the original node identifiers).
    '''
    result = {}
    for index in extract.keys():
        result[extract[index]['label']] = {'room': extract[index]['room'],
                                           'neighbors': sorted([extract[n]['label'] for n in extract[index]['neighbors']])}
    return result

def dotted(numbers):
    '''
    Transform a space-separated list of numbers into a string with dots separating the numbers.
    '''
    return ".".join([str(n) for n in numbers])
    
def flatten(transform):
    '''
    Convert the transformed Graph extract dict into a list of lists. Each list entry contains three elements:
    the node label, the room, and dotted string of neighbors.
    '''
    result = []
    for label in transform.keys():
        #result.append(f"{label},{transform[label]['room']},{dotted(transform[label]['neighbors'])}")
        result.append([label,f"{transform[label]['room']}",f"{dotted(transform[label]['neighbors'])}"])
    return result

def equal(graph1, graph2):
    '''
    Compare two graphs, at a basic level: a sort of extended node-edge list
    '''
    return (sorted(flatten(transform(extract(graph1)))) == sorted(flatten(transform(extract(graph2)))))

def compare(graphs1, graphs2):
    '''
    Compare two lists of Graphs.
    '''
    for i in range(len(graphs1)): print(i,equal(graphs1[i], graphs2[i]))
