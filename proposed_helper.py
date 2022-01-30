from re import sub
import networkx as nx
import math
def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(edge[0],edge[1], weight=graph.edge_weights[edge])

    phi = (1+math.sqrt(graph.nodes+1))/2.0 # largest eigenvalue of adj matrix
    centrality = nx.katz_centrality(G,1/phi-0.01)
    # for n,c in centrality.items():
    #     print(f"{n} {c}")
    #   
    return centrality

def compute_strength(graph):  
    strength = dict()
    for u in range(graph.nodes):
        strength[u] = 0
        for v in graph.neighbours[u]:
            strength[u] += graph.edge_weights[(str(u),str(v))]
    return strength

