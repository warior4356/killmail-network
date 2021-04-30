#!python3

"""
Prints a CSV with summary details of the provided graphs.
"""

import sys
import os.path
import pandas as pd
import igraph as ig

# check commandline args
# paths = sys.argv[1:]
# if len(sys.argv) == 1:
# 	print("Usage: metrics [path]")
# 	quit()
#
# # check all paths exist
# for path in paths:
# 	if not os.path.exists(path):
# 		print(path + " does not exist")
# 		quit()

paths = ["../gml-out/killer_corp_network_2021-03-giant.gml", "../gml-out/killer_corp_network_2021-03-01-07-giant.gml",
		 "../gml-out/killer_corp_network_combined_2021-03-giant.gml", "../gml-out/killer_corp_network_combined_2021-03-01-07-giant.gml",
		 "../gml-out/killer_network_2021-03-giant.gml", "../gml-out/killer_network_2021-03-giant.gml",
		 "../gml-out/killer_network_combined_2021-03-giant.gml", "../gml-out/killer_network_combined_2021-03-01-07-giant.gml"]

# read graphs
graphs = [ig.Graph.Read(path) for path in paths]

for graph in graphs:
	for edge in graph.es:
		if edge['weight'] < 0:
			print(edge['weight'], graph.vs[edge.source]['name'],graph.vs[edge.target]['name'])
	
