#!python3

"""
Prints a CSV with summary details of the provided graphs.
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

# read graphs
graphs = [ig.Graph.Read(path) for path in paths]

# print graph summaries
graphSummary = {
	'vertices': [graph.vcount() for graph in graphs],
	'edges': [graph.ecount() for graph in graphs],
	'vertex attributes': [graph.vs.attributes() for graph in graphs],
	'edge Attributes': [graph.es.attributes() for graph in graphs],
	'is connected': [graph.is_connected() for graph in graphs],
	'scc': [g.clusters(mode='strong').cluster_graph().vcount() for g in graphs],
	'wcc': [g.clusters(mode='weak').cluster_graph().vcount() for g in graphs],
	'max degree': [max(g.degree()) for g in graphs],
	'avg path len': [g.average_path_length() for g in graphs],
	'diameter': [g.diameter() for g in graphs],
	'lcc': [g.transitivity_avglocal_undirected() for g in graphs],
	'gcc': [g.transitivity_undirected() for g in graphs],
}

df = pd.DataFrame(graphSummary, index=[os.path.basename(path) for path in paths])
df = df.rename_axis('graph')
print(df.to_csv())
