from networkx.algorithms import community
from .sequence import Sequence
'''
run Community Detection on all graphs

return an array of dict, where each dictionary key is the community and the value is an array of members:

    {community1: [members],
     community2: [members],
     ...}

'''
def communities(graphs):
    # TODO: provide ability to execute different community detection algorithms
    #       The parameter could specify by name: 'networkx', 'louvain', 'leiden'
    #       for which we will provide an implementation.
    #       Or, the parameter could specify a function or class of type '???' with method ???
    #       which returns a dictionary formed like described above.
    
    modularities = []
    for graph in graphs:
        modularity = community.greedy_modularity_communities(graph)
        sequence = Sequence(0)
        modularities.append({sequence(): list(group) for group in modularity})
    return modularities

'''
generate a table of community memberships across the span of time (each temporal snapshot)

the table is a Pandas DataFrame

'''
def tabulate(nodemap, modularities):
    # TODO: make this more functional with pure functions
    # TODO: make a function which takes a modularity and returns the Series
    # TODO: iterate over the modularities, call the function, and append to the DataFrame

    df = nodemap.dataframe()
    df['Node'] = df.index

    sequence = Sequence(0)

    for modularity in modularities:
        timestamp = "T{}".format(sequence())
        #print("timestamp:",timestamp)
        df[timestamp] = -1
        series = df[timestamp]
        for group in range(len(modularity)):
            #print("  group:",group)
            series.update(pd.Series([group for r in range(len(modularity[group]))], index=modularity[group]))
            
    return df

_debug_ = True
def debug(s):
    if _debug_: print(s)

def plurality(n,s,p):
    if n == 1:
        return "is",s
    else:
        return "are",p

def computeGrouping(df):
    '''
    computeGrouping(df)
    
    Computes group membership at a specific time. Returns a collection of the groups with their members.

    Inputs:
      df : a DataFrame with two columns: 'Node' and a time column named 'Tn' where 'n' is the numbered time-slice

    Returns:
      a dict: {group1: {member1, member2, ...}, group2: {member1, member2, ...}, ...}
    '''
    grouping = {}
    
    time = list(filter(lambda x: x.startswith("T"), df.columns))[0]
    debug("computeGrouping() {} => {}".format(time, df[time].values))
    for group in set(df[time].values):
        grouping[group] = set(df[df[time]==group].Node.values)
    
    number = len(grouping)
    verb,label = plurality(number,"group","groups")
    debug("- there {} {} {}".format(verb,number,label))
    for group in grouping:
        debug("- {}: {}".format(group,grouping[group]))

    return grouping

def computeSimilarity(grouping1, grouping2):
    '''
    computeSimilarity(grouping1, grouping2)
    
    Computes the similarity between each group in the two provided groupings. The two groupings represent
    the group membership at two consecutive temporal points.
    
    The group similarity measure is based on Python set type operations. It determine how much of group1 
    is in group2 by using the set intersection operation, achieved with the & operator.
    
    Inputs:
      grouping1, grouping2: two dicts (output from `computeGrouping`)
    
    Returns:
      a dict with two entries
        contribution is the amount of the first group that is in the second group
        proportion is the amount of the second group made up from the first group's contribution
    '''
    similarity = {}

    # for each group in time1, compare with each group in time2 (skip groups == -1)
    for g1 in grouping1.keys():
        if g1 == -1: continue
        similarity[g1] = {}
        for g2 in grouping2.keys():
            if g2 == -1: continue
            group1 = grouping1[g1]
            group2 = grouping2[g2]
            debug("computeSimilarity() {} -> {}".format(g1,g2))
            debug("  {}: {}".format(g1,group1))
            debug("  {}: {}".format(g2,group2))
            contribution = len(group1 & group2) / len(group1)
            proportion = (len(group1) * contribution) / len(group2) if contribution > 0.0 else 0.0
            # `contribution` is the percent of group 1 that is now in group 2
            # `proportion` is the percent of group 2 that is made up from group 1
            similarity[g1][g2] = {
                'contribution': contribution,
                'proportion': proportion
            }
            debug("  g1: {} g2 {} => {}".format(g1, g2, similarity[g1][g2]))
                
    return similarity

def findContributors(similarity):
    debug("findContributors()")
    contributors = {}
    
    for dst in similarity[list(similarity.keys())[0]].keys():
        contributors[dst] = {}
        print(" >> ","{}: ".format(dst),end="")
        for src in similarity.keys():
            proportion = similarity[src][dst]['proportion']
            if similarity[src][dst]['proportion'] > 0.0:
                contributors[dst][src] = similarity[src][dst]
                item = " {} = {} ({})".format(src,
                                              round(contributors[dst][src]['proportion'],3),
                                              round(contributors[dst][src]['contribution'],3))
                print("{0:18s}".format(item),end="")
        print("")
        
    return contributors

import operator

def findOrigins(contributors):
    debug("findOrigins()")
    
    origins = {}
    originators = []

    sole_matching_contributors = {}
    sole_different_contributors = {}
    mult_contributors = {}
    for group in contributors:
        if len(contributors[group]) == 1:
            if group == list(contributors[group].keys())[0]:
                sole_matching_contributors[group] = contributors[group]
            else:
                sole_different_contributors[group] = contributors[group]
        else:
            mult_contributors[group] = contributors[group]

    print("  sole matching contributions:")
    for group in sole_matching_contributors:
        print("    {}: {}".format(group,sole_matching_contributors[group]))
        for contrib in sole_matching_contributors[group]:
            print("    + origin:",group,"<-",contrib,"[sole matching contributor]",sole_matching_contributors[group][contrib])
            origins[group] = {
                'origin': contrib,
                'contribution': sole_matching_contributors[group][contrib]['contribution'],
                'proportion': sole_matching_contributors[group][contrib]['proportion']
            }
            originators.append(contrib)

    print("  sole different contributions:")
    for group in sole_different_contributors:
        print("    {}: {}".format(group,sole_different_contributors[group]))
        for contrib in sole_different_contributors[group]:
            if contrib in originators:
                #print("  this group originates from a group which supplied another sole contributor")
                #print("  which means this group is the result of a split of a previous group and a group already")
                #print("  processed has claimed the contributing group as its origin, so this group will keep its")
                #print("  own (current) identity and forego any claim to its contributor as its origin")
                print("    + origin:",group,"<-",group,"[sole contributor: group split]","(",contrib,":",sole_different_contributors[group],")")
                origins[group] = {
                    'origin': group,
                    'contribution': -1.0,
                    'proportion': -1.0
                }
                originators.append(group)
            else:
                print("    + origin:",group,"<-",contrib,"[sole different contributor]",sole_different_contributors[group])
                origins[group] = {
                    'origin': contrib,
                    'contribution': sole_different_contributors[group][contrib]['contribution'],
                    'proportion': sole_different_contributors[group][contrib]['proportion']
                }
                originators.append(contrib)
    
    print("  multiple contributions:")
    for group in mult_contributors:
        ordered_contributors = sorted(mult_contributors[group].items(), 
                                      key=lambda e: e[1]['proportion'], 
                                      reverse=True)
        print("    {}: {}".format(group,ordered_contributors))
        found = False
        for contributor in ordered_contributors:
            contrib = contributor[0]
            portion = contributor[1]
            print("    - for group",group,"check",contrib,"(",portion,")")
            if contrib not in originators:
                found = True
                print("    + origin:",group,"<-",contrib,"[multiple contributors]",portion)
                origins[group] = {
                    'origin': contrib,
                    'contribution': portion['contribution'],
                    'proportion': portion['proportion']
                }
                originators.append(contrib)
            else:
                print("    - contrib",contrib,"in originators",originators)
            if found: 
                break
        
        if not found:
            # a new group forms, from indeterminable origin
            print("    + origin:",group,"<-",group,"[indeterminable origin]")
            origins[group] = {
                'origin': group,
                'contribution': -1.0,
                'proportion': -1.0
            }
    
    return origins

'''
renameCommunities(df,origins)
Inputs:
  before : an array of community assignments
  origins : dict

Returns:
  after : a vector with renamed community assignments

'''
def renameCommunities(before,origins):
    debug("renameCommunities()")
    print("- before:",before)
    after = []
    for i in range(len(before)):
        v1 = before[i]
        v2 = origins[v1]['origin'] if v1 >= 0 else v1
        print(" - change [",i,"] v1:",v1,"->","v2:",v2)
        after.append(v2)
    print(" - after:",after)
    return after

import pandas as pd

# get columns from DataFrame which contain time-slice community membership
# the DataFrame columns will have names 'Tn' where 'n' is a sequential number 1..t

def timeColumns(df):
    return list(filter(lambda x: x.startswith("T"), df.columns))

def align_community_assignments(df1):
    df2 = pd.DataFrame(columns=df1.columns)
    df2.label = df1.label
    df2.Node = df1.Node
    df2.T0 = df1.T0
    
    # iterate over pairs of sequential time-slices
    timecols = timeColumns(df1)

    for i in range(len(timecols) - 1):
        t1 = timecols[i]
        t2 = timecols[i+1]
        debug("process() {} -> {}".format(t1,t2))

        grouping1 = computeGrouping(df2[['Node',t1]])
        grouping2 = computeGrouping(df1[['Node',t2]])

        similarity = computeSimilarity(grouping1, grouping2)

        contributors = findContributors(similarity)
        
        origins = findOrigins(contributors)
        renamed = renameCommunities(df1[t2].values, origins)
        df2[t2] = renamed
    
    return df2

# TODO: optionally return a qgrid object

# import qgrid
#
# qgrid_df = qgrid.show_grid(df, show_toolbar=True)
# qgrid_df
#
# qgrid_df_aligned = qgrid.show_grid(df_aligned, show_toolbar=True)
# qgrid_df_aligned

def inspect_alignment(df1, df2, query, result="dataframe"):
    qr1 = df1.query(query).iloc[0]
    qr2 = df2.query(query).iloc[0]
    df = pd.DataFrame(columns=['tags'])
    df.tags = qr1.index.values
    df['a'] = qr1.values
    df['b'] = qr2.values
    return df

'''
compute_flows()

  Compute the flow of community membership. This is a directed acyclic graph (DAG) with weighted edges.

  Parameters
    d1: array of community assignments at time previous
    d2: array of community assignments at time current
    flow: a dict which keeps track of 'everything'
    index: a Sequence

  Result
'''
def compute_flows(d1, d2, flow, index):
    debug("compute_flows()")
    
    # TODO: ensure `d1` and `d2` are the same length
    
    # `flow` is the result, and is computed each time this function is called
    # if `flow` has values in [targets], then [targets] become the [sources].
    # this is necessary state propagation so the nodes in the DAG can be connected.
    if len(flow['targets']) > 0:
        flow['sources'] = flow['targets']
        flow['targets'] = {}
        flow['labels'] = []
        flow['flows'] = {}
    
    # iterate over each entry in the input community assignment arrays
    # these represent the community assignments for each node at two distinct times
    for i in range(len(d1)):
        source = d1[i]
        target = d2[i]

        # skip -1's (they are non-existent at this time-slice)
        if source < 0 or target < 0:
            debug("[{0:6d}] skip {1} -> {2}".format(i,source,target))
            continue

        # if we have seen this `source` or `target` community before,
        # then fetch its node index from the appropriate section of `flow[]`
        # else assign a new node index to it and start tracking it in `flow[]`
        
        # source_index is a number which will be a node index in the DAG
        # `label` is the community identifier (name/number)
        if source in flow['sources']:
            source_index = flow['sources'][source]['index']
        else:
            source_index = index()
            flow['sources'][source] = {'index': source_index, 'label': source}
            flow['labels'].append(source)

        # target_index is a number which will be a node index in the DAG
        # `label` is the community identifier (name/number)
        if target in flow['targets']:
            target_index = flow['targets'][target]['index']
        else:
            target_index = index()
            flow['targets'][target] = {'index': target_index, 'label': target}
            flow['labels'].append(target)

        # generate the flow label: this indicates the flow of community membership across the
        # two time slices we are processing, it is represented as "source_index -> target_index"
        # and it represents an edge between nodes in the DAG
        label = "{} -> {}".format(source_index, target_index)
        debug("[{0:6d}] flow: {1:3d} -> {2:3d}   ( {3:12s} )".format(i, source, target, label))

        # compute the weight of the flow (edge)
        if label in flow['flows']:
            flow['flows'][label] += 1
        else:
            flow['flows'][label] = 1
    
    debug(" sources: {}".format(flow['sources']))
    debug(" targets: {}".format(flow['targets']))
    debug(" labels: {}".format(flow['labels']))
    debug(" flows: {}".format(flow['flows']))
    
    debug("sources {} to {} targets {} to {}".format(min([flow['sources'][f]['index'] for f in flow['sources']]),
                                                     max([flow['sources'][f]['index'] for f in flow['sources']]),
                                                     min([flow['targets'][f]['index'] for f in flow['targets']]),
                                                     max([flow['targets'][f]['index'] for f in flow['targets']])))
    debug("nodes in this time-slice: {} to {}".format(min([flow['sources'][f]['index'] for f in flow['sources']]+
                                                          [flow['targets'][f]['index'] for f in flow['targets']]),
                                                      max([flow['sources'][f]['index'] for f in flow['sources']]+
                                                          [flow['targets'][f]['index'] for f in flow['targets']])))

'''
analyze_flows()

  generate DAG edge data (u = source, v = target, w = weight)

  Parameters
    flow: 
    colorgrid: 
    
  Result
    labels: a list of nodes, the length of this list represents how many nodes there are
            the values in this list are the 
    sources: 
    targets: 
    values:  edge weight
'''
def analyze_flows(flow):
    debug("analyze_flows()")
    labels = flow['labels']
    sources = []
    targets = []
    values = []
    for f in flow['flows']:
        src = f.split()[0]
        dst = f.split()[2]
        sources.append(src)
        targets.append(dst)
        values.append(flow['flows'][f])
    debug("labels: {}".format(labels))
    debug("sources: {}".format(sources))
    debug("targets: {}".format(targets))
    debug("values: {}".format(values))
    return labels, sources, targets, values

def community_flow(df_aligned):
    flow = {
        'sources': {},
        'targets': {},
        'labels': [],
        'flows': {}
    }

    index = Sequence(0)

    labels = []
    sources = []
    targets = []
    values = []

    timecols = timeColumns(df_aligned)

    for i in range(len(timecols) - 1):
        t1 = timecols[i]
        t2 = timecols[i+1]
        d1 = df_aligned[t1].values
        d2 = df_aligned[t2].values
        debug("Processing flows: {} -> {}".format(t1,t2))
        debug("  {} : {}".format(t1,d1))
        debug("  {} : {}".format(t2,d2))
        compute_flows(d1, d2, flow, index)

        l,s,t,v = analyze_flows(flow)
        labels += l
        sources += s
        targets += t
        values += v

    print("labels:", len(labels))

    print("sources:", len(sources))
    print("targets:", len(targets))
    print("values:", len(values))

    print("\n labels:", labels)
    print("\n sources:", sources)
    print("\n targets:", targets)
    print("\n values:", values)


    # create nodes
    # the index/name is the position in the list (the `i` list comprehension value)
    # the value in `labels` is the community number, which becomes the node label attribute 
    # each node's color attribute comes from a ColorMap
    dag = nx.DiGraph()

    dag.add_nodes_from([(i,dict(name=i, label=labels[i], community=labels[i])) 
                        for i in range(len(labels))])

    # create edges
    # `sources` is a list of node identifiers index/name
    # `targets` is a list of node identifiers index/name
    # `values` is a list of edge weights
    dag.add_edges_from([(int(sources[i]),int(targets[i]),dict(weight=values[i])) 
                        for i in range(len(sources))])
    
    return dag

import matplotlib.pyplot as plt
import networkx as nx

#%matplotlib inline

def visualize_flow(cf, colorgrid):
    plt.figure(1,figsize=(20,20)) 

    layout = nx.nx_agraph.graphviz_layout(cf, prog='dot', args="-Grankdir=LR")

    elp = nx.draw_networkx_edge_labels(cf, 
                                       pos=layout,
                                       edge_labels={(u,v):cf.edges[u,v]['weight'] for u,v in cf.edges()})

    nx.draw(cf,
            pos=layout,
            node_color=[colorgrid.colorFor(cf.nodes[n]['community']) for n in cf.nodes()],
            node_size=400,
            labels={n:cf.nodes[n]['label'] for n in cf.nodes()},
            font_color='white',
            font_weight='normal',
            font_size=12,
            alpha=0.90)

    plt.show()
