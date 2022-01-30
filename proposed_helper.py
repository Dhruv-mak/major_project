from re import sub
import networkx as nx
import math
import numpy as np
def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(edge[0],edge[1], weight=graph.edge_weights[edge])

    phi = (1+math.sqrt(graph.nodes+1))/2.0 # largest eigenvalue of adj matrix
    centrality = nx.katz_centrality(G,1/phi-0.01)
    # for n,c in centrality.items():
    #     print(f"{n} {c}")
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    return centrality

# subtract the edge weights in the nodes.........
def compute_strength(graph):  
    strength = [0 for _ in range(graph.nodes)]
    for u in range(graph.nodes):
        for v in graph.neighbours[u]:
            strength[u] += graph.edge_weights[(str(u),str(v))]
    return np.array(strength)

def get_ranks(graph):
    # 0: degree
    # 1: cetrality
    # 2: strength
    degree = np.arary([len(graph.neighbours[i]) for i in range(graph.nodes)])
    centrality = compute_katz(graph)
    strength = compute_strength(graph)
    deg_max, deg_min = np.max(degree), np.min(degree)
    cen_max, cen_min = np.max(centrality), np.min(centrality)
    str_max, str_min = np.max(strength), np.min(strength)
    deg_weight = 1/3
    cen_weight = 1/3
    str_weight = 1/3
    R_j = (deg_weight * (deg_max - degree))/(deg_max - deg_min)
    R_j += (cen_weight * (cen_max - degree))/(cen_max - cen_min)
    R_j = (str_weight * (str_max - degree))/(str_max - str_min)
    