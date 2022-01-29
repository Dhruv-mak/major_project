import helper
import sys
import copy

class temp_map:
    def __init__(self, vne_list, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        for i in vne_list:
            self.node_cost += sum(i.node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()

def node_map(substrate, vne_list):
    map = []
    for i in range(len(vne_list)):
        assigned_nodes = set()
        for vnode in range(vne_list[i].nodes):
            for snode in range(substrate.nodes):
                if substrate.node_weights[snode] >= vne_list[i].node_weights[vnode] and snode not in assigned_nodes:
                    map.append(snode)
                    substrate.node_weights[snode] -= vne_list[i].node_weights[vnode]
                    assigned_nodes.add(snode)
                    break
            if snode == substrate.nodes:
                return None
    return map

def edge_map(substrate_copy, vne_list, tempo_map):
    index = 0
    for i in range(len(vne_list)):
        for edge in vne_list[i].edges:
            if int(edge[0]) < int(edge[1]):
                weight = vne_list[i].edge_weights[(edge[0], edge[1])]
                left_node = str(tempo_map.node_map[int(edge[0]) + index])
                right_node = str(tempo_map.node_map[int(edge[1]) + index])
                path = substrate_copy.findShortestPath(left_node, right_node, weight)
                if path != []:
                    tempo_map.edge_map[i, edge] = path
                    for j in range(1, len(path)):
                        substrate_copy.edge_weights[(path[j - 1], path[j])] -= weight
                        substrate_copy.edge_weights[(path[j], path[j - 1])] -= weight
                        tempo_map.edge_cost += weight
                else:
                    return False
        index += vne_list[i].nodes
    return True
    
def main():
    substrate, vne_list = helper.read_pickle()
    map = node_map(copy.deepcopy(substrate), vne_list)
    curr_map = temp_map(vne_list, map)
    if map is None:
        print("Could not find the map by first-fit greedy algo")
        return
    if not edge_map(copy.deepcopy(substrate), vne_list, curr_map):
        print("could not find the edge map for the current map")
        return
    revenue = 0
    for i in vne_list:
        revenue += sum(i.node_weights.values()) + (sum(i.edge_weights.values())//2)
    print(f"The revenue is {revenue}")
    curr_map.total_cost = curr_map.edge_cost + curr_map.node_cost
    print(f"The selected map is {curr_map.node_map} with the cost of {curr_map.total_cost}")

if __name__ == '__main__':
    main()