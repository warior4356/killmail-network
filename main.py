import make_network
import calculate_metrics
import pandas as pd


def make_base_dict():
    return {"in_degree": pd.DataFrame(), "out_degree": pd.DataFrame(), "page_rank": pd.DataFrame(),
                    "authority": pd.DataFrame(), "hub": pd.DataFrame(), "degree_ratio": pd.DataFrame()}


def main():
    top_x = 10
    results = {'killer_network': make_base_dict(), 'killer_corp_network': make_base_dict(),
               'victim_network': make_base_dict(), 'victim_corp_network': make_base_dict()}

    for day in range(1, 32):
        print('2021-03-' + str(day))
        graphs = make_network.make_graphs('2021-03-' + str(day), '2021-03-' + str(day))

        for graph_type in graphs:
            # print(calculate_metrics.get_graph_attributes(graphs[key], graph_type))
            centrality_metrics = calculate_metrics.top_centrality(graphs[graph_type], top_x)

            results[graph_type]['in_degree']['2021-03-' + str(day)] = centrality_metrics['in_degree']
            results[graph_type]['out_degree']['2021-03-' + str(day)] = centrality_metrics['out_degree']
            results[graph_type]['page_rank']['2021-03-' + str(day)] = centrality_metrics['page_rank']
            results[graph_type]['authority']['2021-03-' + str(day)] = centrality_metrics['authority']
            results[graph_type]['hub']['2021-03-' + str(day)] = centrality_metrics['hub']
            results[graph_type]['degree_ratio']['2021-03-' + str(day)] = centrality_metrics['degree_ratio']

    for graph_type in graphs:
        results[graph_type]['in_degree'] = pd.concat([results[graph_type]['in_degree'],
                                                      results[graph_type]['in_degree'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)
        results[graph_type]['out_degree'] = pd.concat([results[graph_type]['out_degree'],
                                                      results[graph_type]['out_degree'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)
        results[graph_type]['page_rank'] = pd.concat([results[graph_type]['page_rank'],
                                                      results[graph_type]['page_rank'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)
        results[graph_type]['authority'] = pd.concat([results[graph_type]['authority'],
                                                      results[graph_type]['authority'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)
        results[graph_type]['hub'] = pd.concat([results[graph_type]['hub'],
                                                results[graph_type]['hub'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)
        results[graph_type]['degree_ratio'] = pd.concat([results[graph_type]['degree_ratio'],
                                                         results[graph_type]['degree_ratio'].T.stack().reset_index(
                                                          name='aggregate')['aggregate']], axis=1)

    for graph_type in results:
        # print(graph_type)
        for df_type in results[graph_type]:
            # print(df_type)
            # print(results[graph_type][df_type])
            results[graph_type][df_type].to_csv("csv_out/2021-03_aggregate_" + graph_type + '_' + df_type + ".csv")


if __name__=="__main__":
    main()