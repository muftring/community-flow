# community-flow
analyze temporal networks to discover the flow of community structures

# Execution
```
import pandas as pd
import communityflow as cf
from communityflow import PsdPartitioner

# load data from CSV into a DataFrame
psd = pd.read_csv("primaryschool.with-header.csv")

# partition the data into temporal slices
partitions = cf.partition(psd, 'Time', PsdPartitioner())

# create graphs for each temporal slice
graphs, nodemap = cf.create_graphs(partitions)

# perform community detection
modularities = cf.communities(graphs)

# tabulate modularities into a DataFrame
df = cf.tabulate(nodemap, modularities)

# align the community assignments
df_aligned = cf.align_community_assignments(df)

# compute the community flow
flow = cf.community_flow(df_aligned)

# visualze the community flow
cf.visualize_flow(flow, ColorGrid('tab20'))
```
