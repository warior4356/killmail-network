#!python3

"""
Calculate the max centrality measures from a graph with the measures already
calculated for each node.
"""

import sys
import os.path
import pandas as pd
import igraph as ig

# check commandline args
paths = sys.argv[1:]
if len(sys.argv) == 1:
	print("Usage: metrics [path]")
	quit()

# check all paths exist
for path in paths:
	if not os.path.exists(path):
		print(path + " does not exist")
		quit()

df = pd.DataFrame(index=[os.path.basename(path) for path in paths])

# read graphs
graphs = [ig.Graph.Read(path) for path in paths]

df['degree'] = [graph.vs.select(lambda v: v['degree'] == max(graph.vs['degree']))['name'] 
								for graph in graphs]

# find min eccentricity becuase centrality measure takes 1/e(u)
df['eccentricity'] = [graph.vs.select(lambda v: v['eccentricity'] == min(graph.vs['eccentricity']))['name']
											for graph in graphs]

df['closeness'] = [graph.vs.select(lambda v: v['closeness'] == max(graph.vs['closeness']))['name']
									 for graph in graphs]

df['betweenness'] = [graph.vs.select(lambda v: v['betweenness'] == max(graph.vs['betweenness']))['name']
									 for graph in graphs]

df['pagerank'] = [graph.vs.select(lambda v: v['pagerank'] == max(graph.vs['pagerank']))['name']
									for graph in graphs]

df['authority'] = [graph.vs.select(lambda v: v['authority'] == max(graph.vs['authority']))['name']
									 for graph in graphs]

df['hub'] = [graph.vs.select(lambda v: v['hub'] == max(graph.vs['hub']))['name']
						 for graph in graphs]


df = df.rename_axis('graph')
print(df.to_csv())
