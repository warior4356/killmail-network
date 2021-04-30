import igraph

def get_graph_attributes(graph, name):
    line = name + "\t"
    if(graph.is_directed()):
        line += "Directed\t"
    else:
        line += "Undirected\t"
    line += str(graph.vcount()).zfill(4) + "\t"
    line += str(graph.ecount()) + "\t"
    line += str(len(graph.components().subgraphs())) + "\t"
    line += str(graph.maxdegree()).zfill(4) + "\t"
    line += str(graph.average_path_length()) + "\t"
    line += str(graph.diameter()) + "\t"
    line += str(graph.transitivity_avglocal_undirected()).ljust(21, '0') + "\t"
    line += str(graph.transitivity_undirected()) + "\t"
    line += "\n"
    return line


def top_centrality(graph, top_x):
    graph.vs['in_degree'] = graph.indegree()
    graph.vs['out_degree'] = graph.outdegree()
    graph.vs['degree_ratio'] = [i / max(j, .9) for i, j in zip(graph.outdegree(), graph.indegree())]
    graph.vs['page_rank'] = graph.pagerank(weights='weight')
    graph.vs['authority'] = graph.authority_score(weights='weight')
    graph.vs['hub'] = graph.hub_score(weights='weight')
    # graph.vs['katz'] = graph.eigenvector_centrality(weights='weight')

    results = dict()

    results['in_degree'] = sorted(graph.vs, key=lambda v: v['in_degree'], reverse=True)
    results['out_degree'] = sorted(graph.vs, key=lambda v: v['out_degree'], reverse=True)
    results['page_rank'] = sorted(graph.vs, key=lambda v: v['page_rank'], reverse=True)
    results['authority'] = sorted(graph.vs, key=lambda v: v['authority'], reverse=True)
    results['hub'] = sorted(graph.vs, key=lambda v: v['hub'], reverse=True)
    results['degree_ratio'] = sorted(graph.vs, key=lambda v: v['degree_ratio'], reverse=True)

    results['in_degree'] = [v['name'] for v in results['in_degree'][:top_x]]
    results['out_degree'] = [v['name'] for v in results['out_degree'][:top_x]]
    results['page_rank'] = [v['name'] for v in results['page_rank'][:top_x]]
    results['authority'] = [v['name'] for v in results['authority'][:top_x]]
    results['hub'] = [v['name'] for v in results['hub'][:top_x]]
    results['degree_ratio'] = [v['name'] for v in results['degree_ratio'][:top_x]]

    return results
