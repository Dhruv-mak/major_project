import re
import helper
import sys
import copy
from datetime import datetime, date

class temp_map:
    def __init__(self, vne_list,req_no, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        self.node_cost += sum(vne_list[req_no].node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()

def node_map(substrate, virtual, req_no):
    map = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x]) # ascending order
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
            path = substrate_copy.findShortestPath(str(left_node), str(right_node), weight) # modified bfs
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
    for node in range(vne_list[req_no].nodes):
        substrate.node_weights[req_map.node_map[node]] -= virtual.node_weights[node]
    return True
    
def main():
    substrate, vne_list = helper.read_pickle()
    start_time = datetime.now().time()
    accepted = 0
    curr_map = dict() # only contains the requests which are successfully mapped
    pre_resource_edgecost = sum(substrate.edge_weights.values())//2 # total available bandwidth of the physical network
    pre_resource_nodecost = sum(substrate.node_weights.values()) # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost
    
    for req_no in range(len(vne_list)):
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is  None:
            print(f"Node mapping not possible for req no {req_no}")
            continue
        req_map = temp_map(vne_list, req_no, req_map)
        if not edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list):
            print(f"Edge mapping not possible for req no {req_no}")
            continue
        accepted += 1
        req_map.total_cost = req_map.node_cost + req_map.edge_cost
        print(f"Mapping for request {req_no} is done successfully!! {req_map.node_map} with total cost {req_map.total_cost}")
        curr_map[req_no] = req_map

    ed_cost  = 0
    no_cost = 0
    revenue = 0
    for request in curr_map.values():
        ed_cost += request.edge_cost # total bandwidth for all the mapped requests
        no_cost += request.node_cost # total crb for all the mapped requests
        revenue += sum(request.node_weights.values()) + (sum(request.edge_weights.values())//2)

    tot_cost = ed_cost + no_cost
    post_resource = sum(substrate.node_weights.values()) + sum(substrate.edge_weights.values())//2
    

    
    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    
    print(f"\n\nThe revenue is {revenue} and total cost is {tot_cost}")
    print(f"Total number of requests embedded is {accepted}")
    print(f"Embedding ratio is {accepted/len(vne_list)}")
    print(f"Availabe substrate resources before mapping is {pre_resource}")
    print(f"Consumed substrate resources after mapping is {pre_resource - post_resource}")
    print(f"Average link utilization {ed_cost/pre_resource_edgecost}")
    print(f"Average node utilization {no_cost/pre_resource_nodecost}")
    print(f"Average execution time {duration/len(vne_list)}")

if __name__ == '__main__':
    main()