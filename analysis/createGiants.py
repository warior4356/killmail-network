#!python3

"""
Create a gml of the giant component of the given graphs. Saved as the same path
with '-giant' suffixed.
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

# # check all paths exist
# for path in paths:
# 	if not os.path.exists(path):
# 		print(path + " does not exist")
# 		quit()


paths = ["../gml-out/killer_corp_network_2021-03-01.gml",
		# "../gml-out/killer_corp_network_2021-03-01-07.gml"
		"../gml-out/killer_corp_network_combined_2021-03-01.gml",
		# "../gml-out/killer_corp_network_combined_2021-03-01-07.gml",
		"../gml-out/killer_network_2021-03-01.gml",
		"../gml-out/killer_network_combined_2021-03-01.gml",
		# "../gml-out/killer_network_combined_2021-03-01-07.gml"
		]
# read graphs
graphs = [ig.Graph.Read(path) for path in paths]

print("All")
count = 0
for graph in graphs:
	count += 1
	print(count)
	for edge in graph.es:
		if edge['weight'] < 0:
			print(edge['weight'], graph.vs[edge.source]['name'], graph.vs[edge.target]['name'])

# get giant components
giants = [graph.clusters().giant() for graph in graphs]

print("Giant")
for graph in giants:
	for edge in graph.es:
		if edge['weight'] < 0:
			print(edge['weight'], graph.vs[edge.source]['name'],graph.vs[edge.target]['name'])


# write giants component graphs as gml
for giant, path in zip(giants, paths):
	giant.write_gml(path[:-4] + "-giant.gml")

