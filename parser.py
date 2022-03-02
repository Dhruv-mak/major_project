# this module will parse the pickle file
import logging
import pickle, copy
#import embedder
import embedderDirect
import networkx as nx
import random


min_number_of_nodes=2# Note number of nodes in a VNR must be less than no nodes in a SN n
max_number_of_nodes=4
number_of_requests=5
probability=0.4
# print the out put in log file
FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
logging.basicConfig(filename=r'events.log',
                    format=FORMAT,
                    level=logging.DEBUG,
                    datefmt = '%Y-%m-%d %H:%M:%S %p')


# to make sure graph is connected and make virtual node number start with 1
random_node_list = [random.randint(min_number_of_nodes, max_number_of_nodes) for i in range(number_of_requests)]
new_vne_req=[]
for req in random_node_list:
    G=nx.erdos_renyi_graph(req,probability,directed=False)
    ng=nx.to_dict_of_lists(G)
    print("initial graph")
    print(ng)

    g = {}
    for i in ng:
        g[i + 1] = []
        for j in ng[i]:
            g[i + 1].append(j + 1)
    # c=nx.is_connected(G)
    # print(c)
    # def create_connectivity(g):
    if not nx.is_connected(G):
        null_node_list = [key for key, val in g.items() if not val]
        graph_node_count = {_key: len(_val) for _key, _val in g.items()}
        sorted_dict_list = sorted(graph_node_count.items(), key=lambda x: x[1],
                                  reverse=True)
        if len(null_node_list) != len(g):
            for index, empty_node in enumerate(null_node_list):
                g[sorted_dict_list[index][0]].append(empty_node)
                g[empty_node].append(sorted_dict_list[index][0])
        else:
            for i in range(len(g)):
                for j in range(len(g) - i - 1):
                    if null_node_list[j + 1] not in g[null_node_list[j]]:
                        g[null_node_list[j]].append(null_node_list[j + 1])
                    if null_node_list[j] not in g[null_node_list[j + 1]]:
                        g[null_node_list[j + 1]].append(null_node_list[j])
    new_vne_req.append(g)
    #print("Checking is G is connected",nx.is_connected(g))
print("new VNE REQ is",new_vne_req)



file = open('senario_RedBestel.pickle','rb')
pkl = pickle.load(file)
dataModel = pkl.scenario_list[0]
print("print data model")
print(dataModel)
print(dataModel.requests)



sn = dict()
vneRequests = list()


# this part will parse the substrate network

nodes = list(dataModel.substrate.nodes)
edges = list(dataModel.substrate.edges)
print("printing nodes/edges")
print(nodes)
print(edges)
for i in nodes:
    sn[int(i)+1] = list()

for i in edges:
    sn[int(i[0])+1].append(int(i[1])+1)
    
# this part will parse the vne requests

print("contents of list(i.nodes) amd list (i.edges)")
for i in dataModel.requests:
    vne = dict()
    node = list(i.nodes)
    print("contents of list(i.nodes) in side for loop")
    print()
    print(i.nodes)
    edge = list(i.edges)
    print("contents of list (i.edges) in side for loop")
    print(i.edges)
    for j in node:
        vne[int(j)] = set()
    for j in edge:
        vne[int(j[0])].add(int(j[1]))
        vne[int(j[1])].add(int(j[0]))
    for j in vne:
        vne[j] = list(vne[j])
    vneRequests.append(vne)

file.close()
logging.info("Printing SN") #KK
logging.info(sn)
logging.info("Printing vneRequests")
logging.info(new_vne_req)
# calling form embedderdirect will cal  page rank(Stable method) and them noderank(Directmethod)
temp = embedderDirect.calling(sn,new_vne_req)


print("***************************************************************************************************")
