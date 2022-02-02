from re import sub
import networkx as nx
import math
import numpy as np
import sys


def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(edge[0], edge[1], weight=graph.edge_weights[edge])

    phi = (1 + math.sqrt(graph.nodes + 1000)) / 2.0  # largest eigenvalue of adj matrix
    centrality = nx.katz_centrality(G, 1 / phi - 0.01, max_iter=sys.maxsize)
    # for n,c in centrality.items():
    #     prfloat(f"{n} {c} {centrality[n]}")
    centrality = np.array([centrality[str(i)] for i in range(graph.nodes)])
    return centrality


# subtract the edge weights in the nodes.........
def compute_strength(graph):
    strength = [0 for _ in range(graph.nodes)]
    for u in range(graph.nodes):
        for v in graph.neighbours[u]:
            strength[u] += graph.edge_weights[(str(u), str(v))]
    return np.array(strength)


def get_ranks(graph):
    # 0: degree
    # 1: cetrality
    # 2: strength
    degree = np.array([len(graph.neighbours[i]) for i in range(graph.nodes)])
    centrality = compute_katz(graph)
    strength = compute_strength(graph)
    crb = np.array([graph.node_weights[i] for i in range(graph.nodes)])
    deg_max, deg_min = np.max(degree), np.min(degree)
    cen_max, cen_min = np.max(centrality), np.min(centrality)
    str_max, str_min = np.max(strength), np.min(strength)
    crb_max, crb_min = np.max(crb), np.min(crb)
    # deg_weight = 1/3
    # cen_weight = 1/3
    # str_weight = 1/3
    weight_mat = get_weights(np.column_stack((degree, centrality, strength, crb)), 4)
    deg_weight = weight_mat[0]
    cen_weight = weight_mat[1]
    str_weight = weight_mat[2]
    crb_weight = weight_mat[3]

    R = np.array(
        [
            ((deg_weight * (deg_max - int(degree[i]))) / (deg_max - deg_min))
            + ((cen_weight * (cen_max - float(centrality[i]))) / (cen_max - cen_min))
            + ((str_weight * (str_max - float(strength[i]))) / (str_max - str_min))
            + ((crb_weight * (crb_max - float(strength[i]))) / (crb_max - crb_min))
            for i in range(graph.nodes)
        ]
    )
    S = np.array(
        [
            max(
                ((deg_weight * (deg_max - int(degree[i]))) / (deg_max - deg_min)),
                ((cen_weight * (cen_max - float(centrality[i]))) / (cen_max - cen_min)),
                ((str_weight * (str_max - float(strength[i]))) / (str_max - str_min)),
                ((crb_weight * (crb_max - float(strength[i]))) / (crb_max - crb_min)),
            )
            for i in range(graph.nodes)
        ]
    )
    S_max, S_min = np.max(S), np.min(S)
    R_max, R_min = np.max(R), np.min(R)
    v = 0.5
    Q = np.array(
        [
            ((v * (float(S[j]) - S_max)) / (S_max - S_min))
            + (((1 - v) * (float(R[j]) - R_max)) / (R_min - R_max))
            for j in range(graph.nodes)
        ]
    )

    return sorted([i for i in range(graph.nodes)], key=lambda x: Q[x])


def get_weights(data, no_attr):
    column_sums = data.sum(axis=0)
    normalized = data / column_sums[:, np.newaxis].transpose()
    E_j = normalized * np.log(normalized)
    E_j_column = 1 - (E_j.sum(axis=0) * (1 / np.log(no_attr)))
    E_j_column_sum = sum(E_j_column)
    w_j = E_j_column / E_j_column_sum
    # print(np.sum(w_j))
    return w_j
