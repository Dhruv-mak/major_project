import networkx as nx
import math
import numpy as np
import pandas as pd
import helper
np.seterr(divide='ignore', invalid='ignore')    #ignores the division by zero (OR value tending to zero)

def divide(a, b):
    '''
    INPUT : two numbers a and b
    OUTPUT: a/b (a divided by b)
    
    divide two numbers using log because if the denominator is two
    low numpy will give warning of dividing by zero. converting to log then
    applying antilog will give same result (i.e. a/b ) with no warnings.

    divisions in the below code (eg-line number 84-87) can be done using this function
    instead of dividing directly.
    '''
    loga = np.log10(a)
    logb = np.log10(b)
    diff = loga-logb
    return 10**diff

def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:

        G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])

    # phi = (1+math.sqrt(graph.nodes+1000))/2.0 # largest eigenvalue of adj matrix
    # centrality = nx.katz_centrality(G,1/phi-0.01, max_iter=sys.maxsize, tol=1.0e-6)
    centrality = nx.katz_centrality(G)
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    # print(centrality)
    return centrality


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
    # 3: crb
    degree = np.array([len(graph.neighbours[i]) for i in range(graph.nodes)])
    centrality = compute_katz(graph)
    strength = compute_strength(graph)
    crb = np.array([graph.node_weights[i] for i in range(graph.nodes)])
    attr_no = 4
    data = np.column_stack((degree, centrality, strength, crb))
    # frame = pd.DataFrame(data, columns=["Degree", "Centrality", "Strength", "CRB"])
    # frame.to_excel('shanon.xlsx')
    weight_mat = get_weights(data, graph.nodes)  # attribute weights
    rank_mat = np.zeros((graph.nodes + 2, (attr_no * 2) + 3))
    rank_mat[: graph.nodes, :attr_no] = data[:, :]
    for i in range(attr_no):
        rank_mat[graph.nodes, i] = np.max(rank_mat[: graph.nodes, i])
        rank_mat[graph.nodes + 1, i] = np.min(rank_mat[: graph.nodes, i])
        rank_mat[: graph.nodes, attr_no + i] = weight_mat[i] * (
            (rank_mat[graph.nodes, i] - rank_mat[: graph.nodes, i])
            / (rank_mat[graph.nodes, i] - rank_mat[graph.nodes + 1, i])
        )
    v = 0.5  # alpha = 0.5 and (1- alpha) = 0.5
    rank_mat[: graph.nodes, (2 * attr_no)] = np.sum(  # Rj calculation
        rank_mat[: graph.nodes, attr_no : 2 * attr_no], axis=1
    )
    rank_mat[: graph.nodes, (2 * attr_no) + 1] = np.max(  # Sj calculation
        rank_mat[: graph.nodes, attr_no : 2 * attr_no], axis=1
    )
    rank_mat[graph.nodes, 2 * attr_no] = np.max(
        rank_mat[: graph.nodes, (2 * attr_no)]
    )  # Rjmax
    rank_mat[graph.nodes + 1, 2 * attr_no] = np.min(  # Rjmin
        rank_mat[: graph.nodes, (2 * attr_no)]
    )
    rank_mat[graph.nodes, 2 * attr_no + 1] = np.max(  # Sjmax
        rank_mat[: graph.nodes, (2 * attr_no) + 1]
    )
    rank_mat[graph.nodes + 1, 2 * attr_no + 1] = np.min(  # Sjmin
        rank_mat[: graph.nodes, (2 * attr_no) + 1]
    )
    rank_mat[: graph.nodes, 2 * attr_no + 2] = v * (  # Qj calculation
        rank_mat[: graph.nodes, 2 * attr_no] - rank_mat[graph.nodes + 1, 2 * attr_no]
    ) / (
        rank_mat[graph.nodes, 2 * attr_no] - rank_mat[graph.nodes + 1, 2 * attr_no]
    ) + (
        1 - v
    ) * (
        rank_mat[: graph.nodes, 2 * attr_no + 1]
        - rank_mat[graph.nodes + 1, 2 * attr_no + 1]
    ) / (
        rank_mat[graph.nodes, 2 * attr_no + 1]
        - rank_mat[graph.nodes + 1, 2 * attr_no + 1]
    )
    ranks = sorted(  # array containing weights
        [i for i in range(graph.nodes)], key=lambda x: rank_mat[x, 2 * attr_no + 2]
    )
    # print(ranks)
    return ranks


# weight calculation using shanon entropy method
def get_weights(data, nodes):
    column_sums = data.sum(axis=0)
    normalized = (
        data / column_sums[:, np.newaxis].transpose()
    )  # normalizing the attribute values
    E_j = normalized * np.log(normalized)
    column_sum = np.sum(E_j, axis=0)
    k = 1 / np.log(nodes)
    column_sum = -k * column_sum
    column_sum = 1 - column_sum
    E_j_column_sum = sum(column_sum)
    w_j = column_sum / E_j_column_sum  # calculated weight array
    return w_j


if __name__ == "__main__":
    substrate, vne_list = helper.read_pickle()
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(substrate.nodes))
    for edge in substrate.edges:
        G.add_edge(int(edge[0]), int(edge[1]), weight=substrate.edge_weights[edge])
    phi = (1 + math.sqrt(substrate.nodes + 1)) / 2.0  # largest eigenvalue of adj matrix
    print(nx.katz_centrality(G, max_iter=1000, tol=1.0e-6))
