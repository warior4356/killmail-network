import igraph
import database
import cfg
import pytz

utc = pytz.timezone('UTC')


connection = database.create_connection(
    "killmails", "postgres", cfg.db_password, "127.0.0.1", "5432"
)
connection.autocommit = True
cursor = connection.cursor()

def remove_ints(graph):
    for edge in graph.es:
        if edge['weight'].is_integer():
            edge['weight'] = edge['weight'] + .01


def has_node(graph, name):
    try:
        graph.vs.find(name=name)
    except:
        return False
    return True


def make_graphs(start_date, end_date):
    fetch_query = (
        "SELECT * FROM killmails where killmails.date::date >= %s AND killmails.date::date <= %s"
    )

    cursor.execute(fetch_query, [start_date, end_date])
    rows = cursor.fetchall()

    graphs = dict()

    killer_list = []
    killer_corp_list = []
    victim_list = []
    victim_corp_list = []

    count = 0
    for row in rows:
        # count = count + 1
        # if count % 100 == 0:
        #     print(count)

        if 'character_id' not in row[3]['victim'].keys():
            continue

        victim_id = str(row[3]['victim']['character_id'])
        victim_id_corp = str(row[3]['victim']['corporation_id'])
        damage = max(row[3]['victim']['damage_taken'], 1)

        for killer in row[3]['attackers']:
            if not 'character_id' in killer.keys():
                continue
            attacker_id = str(killer['character_id'])
            attacker_id_corp = str(killer['corporation_id'])
            attacker_damage = max(killer['damage_done'], 1)

            killer_list.append((victim_id, attacker_id, (float(row[4]) * float(attacker_damage)/float(damage))))
            killer_corp_list.append((victim_id_corp, attacker_id_corp,
                                     (float(row[4]) * float(attacker_damage)/float(damage))))
            victim_list.append((attacker_id, victim_id, (float(row[4]) * float(attacker_damage)/float(damage))))
            victim_corp_list.append((attacker_id_corp, victim_id_corp,
                                     (float(row[4]) * float(attacker_damage)/float(damage))))

    # print("Killer Players")
    graphs["killer_network"] = igraph.Graph.TupleList(killer_list, directed=True, weights=True)
    remove_ints(graphs["killer_network"])
    # killer_network.write_gml("gml-out/killer_network_2021-03-01.gml")
    # killer_network = killer_network.simplify(loops=False, combine_edges='sum')
    # remove_ints(killer_network)
    # killer_network.write_gml("gml-out/killer_network_combined_2021-03-01.gml")

    # print("Killer Corps")
    graphs["killer_corp_network"] = igraph.Graph.TupleList(killer_corp_list, directed=True, weights=True)
    remove_ints(graphs["killer_corp_network"])
    # killer_corp_network.write_gml("gml-out/killer_corp_network_2021-03-01.gml")
    # killer_corp_network = killer_corp_network.simplify(loops=False, combine_edges='sum')
    # remove_ints(killer_corp_network)
    # killer_corp_network.write_gml("gml-out/killer_corp_network_combined_2021-03-01.gml")

    # print("Victim Players")
    graphs["victim_network"] = igraph.Graph.TupleList(victim_list, directed=True, weights=True)
    remove_ints(graphs["victim_network"])

    # print("Killer Corps")
    graphs["victim_corp_network"] = igraph.Graph.TupleList(victim_corp_list, directed=True, weights=True)
    remove_ints(graphs["victim_corp_network"])

    # killer_df = pd.DataFrame(killer_list)
    # killer_network = igraph.Graph.DataFrame(killer_df, directed=True)
    # print(killer_network.clusters().giant().vcount())
    # killer_network.write_gml("gml-out/killer_network_2021-03.gml")
    # killer_corp_df = pd.DataFrame(killer_corp_list)
    # killer_corp_network = igraph.Graph.DataFrame(killer_corp_df, directed=True)
    # print(killer_corp_network.clusters().giant().vcount())
    # killer_corp_network.write_gml("gml-out/killer_corp_network_2021-03.gml")

    # print("Network\t\t\tType\t\tn\t\tm\t\tc\td\t\tl\t\t\t\t\tL\tcci\t\t\t\t\t\tccg\n")
    # print(get_graph_attributes(killer_network, "Killer Network"))
    # print(get_graph_attributes(killer_corp_network, "Killer Corp Network"))

    return graphs
