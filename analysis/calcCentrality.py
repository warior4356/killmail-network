#!python3

"""
Calculate the centrality metrics for each node and add them as node attributes,
then save the gml graph with suffix 'centrality.gml'.
"""

import sys
import os.path
import pandas as pd
import igraph as ig

if __name__ == "__main__":
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

	for graph in graphs:
			graph.vs['degree'] = graph.degree()
			graph.vs['eccentricity'] = graph.eccentricity()
			graph.vs['closeness'] = graph.closeness()
			graph.vs['betweenness'] = graph.betweenness()
			graph.vs['pagerank'] = graph.pagerank()
			graph.vs['authority'] = graph.authority_score()
			graph.vs['hub'] = graph.hub_score()
			#giant.vs['katz'] = graph.eigenvector_centrality()


	# write giants component graphs as gml
	for graph, path in zip(graphs, paths):
		graph.write_gml(path[:-4] + "-centrality.gml")

