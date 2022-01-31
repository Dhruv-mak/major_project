from re import sub
import networkx as nx
import math
import numpy as np
import sys

def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(edge[0],edge[1], weight=graph.edge_weights[edge])

    phi = (1+math.sqrt(graph.nodes+1))/2.0 # largest eigenvalue of adj matrix
    centrality = nx.katz_centrality(G,1/phi-0.01, max_iter=sys.maxsize)
    # for n,c in centrality.items():
    #     prfloat(f"{n} {c} {centrality[n]}")
    centrality = np.array([centrality[str(i)] for i in range(graph.nodes)])
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
    degree = np.array([len(graph.neighbours[i]) for i in range(graph.nodes)])
    centrality = compute_katz(graph)
    strength = compute_strength(graph)
    deg_max, deg_min = np.max(degree), np.min(degree)
    cen_max, cen_min = np.max(centrality), np.min(centrality)
    str_max, str_min = np.max(strength), np.min(strength)
    deg_weight = 1/3
    cen_weight = 1/3
    str_weight = 1/3
    
    R = np.array([((deg_weight * (deg_max - int(degree[i])))/(deg_max - deg_min)) +
                    ((cen_weight * (cen_max - float(centrality[i])))/(cen_max - cen_min)) +
                    ((str_weight * (str_max - float(strength[i])))/(str_max - str_min)) for i in range(graph.nodes)])
    S = np.array([max( ((deg_weight * (deg_max - int(degree[i])))/(deg_max - deg_min)) ,
                    ((cen_weight * (cen_max - float(centrality[i])))/(cen_max - cen_min)) ,
                    ((str_weight * (str_max - float(strength[i])))/(str_max - str_min)) ) for i in range(graph.nodes)])
    S_max, S_min = np.max(S), np.min(S)
    R_max, R_min = np.max(R), np.min(R)
    v = 0.5
    Q = np.array([((v * (float(S[j]) - S_max))/(S_max - S_min)) +
                    (((1-v) * (float(R[j]) - R_max))/(R_min - R_max)) for j in range(graph.nodes)])

    return sorted([i for i in range(graph.nodes)], key = lambda x: Q[x])
    