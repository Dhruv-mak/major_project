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

def node_map(substrate, virtual, req_no):
    map = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x])
    vorder = sorted([a for a in range(virtual.nodes)], key = lambda x: virtual.node_weights[x])
    assigned_nodes = set()
    for vnode in vorder:
        for snode in sorder:
            if substrate.node_weights[snode] >= virtual.node_weights[vnode] and snode not in assigned_nodes:
                map.append(snode)
                substrate.node_weights[snode] -= virtual.node_weights[vnode]
                assigned_nodes.add(snode)
                break
            if snode == substrate.nodes:
                return None
    return map

def edge_map(substrate, virtual, req_no, req_map, vne_list):
    substrate_copy = copy.deepcopy(substrate)
    for edge in virtual.edges:
        if int(edge[0]) < int(edge[1]):
            weight = virtual.edge_weights[edge]
            left_node = sum(vne_list[i].nodes for i in range(0,req_no)) + int(edge[0])
            right_node = sum(vne_list[i].nodes for i in range(0,req_no)) + int(edge[1])
            path = substrate_copy.findShortestPath(str(left_node), str(right_node), weight)
            if path != []:
                req_map.edge_map[req_no, edge] = path
                for j in range(1, len(path)):
                    substrate_copy.edge_weights[(path[j - 1], path[j])] -= weight
                    substrate_copy.edge_weights[(path[j], path[j - 1])] -= weight
                    req_map.edge_cost += weight
            else:
                return False
    for edge, path in req_map.edge_map.items():
        edge = edge[1]
        for i in range(1,len(path)):
            substrate.edge_weights[(path[i - 1], path[i])] -= virtual.edge_weights[edge]
            substrate.edge_weights[(path[i], path[i-1])] -= virtual.edge_weights[edge]
    for node in req_map.nodes:
        substrate.node_weights[req_map.node_map[node]] -= virtual.node_weights[node]
    return True
    
def main():
    substrate, vne_list = helper.read_pickle()
    accepted = 0
    node_sum = 0
    edge_sum = 0

    for req_no in range(len(vne_list)):
        curr_map = dict()
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is  None:
            print(f"Node mapping not possible for req no {req_no}")
            break
        req_map = temp_map(vne_list, req_map)
        if not edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list):
            print(f"Edge mapping not possible for req no {req_no}")
        curr_map[req_no] = req_map

    curr_map = temp_map(vne_list, map)
    revenue = 0
    for i in vne_list:
        revenue += sum(i.node_weights.values()) + (sum(i.edge_weights.values())//2)
    print(f"The revenue is {revenue}")
    curr_map.total_cost = curr_map.edge_cost + curr_map.node_cost
    print(f"The selected map is {curr_map.node_map} with the cost of {curr_map.total_cost}")

if __name__ == '__main__':
    main()