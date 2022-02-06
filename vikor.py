from proposed_helper import get_ranks
import helper
import sys
import copy
from datetime import datetime, date
import logging

# global log1
log1 = logging.getLogger('log1')

class temp_map:
    def __init__(self, vne_list,req_no, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        self.node_cost += sum(vne_list[req_no].node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()

def node_map(substrate, virtual, req_no):
    map = [0 for x in range(virtual.nodes)]
    sorder = get_ranks(substrate) # ascending order
    vorder = get_ranks(virtual) 
    assigned_nodes = set()
    for vnode in vorder:
        for snode in sorder:
            if substrate.node_weights[snode] >= virtual.node_weights[vnode] and snode not in assigned_nodes:
                map[vnode] = snode
                substrate.node_weights[snode] -= virtual.node_weights[vnode]
                assigned_nodes.add(snode)
                break
            if snode == sorder[-1]:
                return None
    return map

def edge_map(substrate, virtual, req_no, req_map, vne_list):
    substrate_copy = copy.deepcopy(substrate)
    for edge in virtual.edges:
        if int(edge[0]) < int(edge[1]):
            weight = virtual.edge_weights[edge]
            left_node = req_map.node_map[int(edge[0])]
            right_node = req_map.node_map[int(edge[1])]
            path = substrate_copy.findShortestPath(str(left_node), str(right_node), weight) # modified bfs
            if path != []:
                req_map.edge_map[req_no, edge] = path
                for j in range(1, len(path)):
                    substrate_copy.edge_weights[(path[j - 1], path[j])] -= weight
                    substrate_copy.edge_weights[(path[j], path[j - 1])] -= weight
                    req_map.edge_cost += weight
            else:
                return False
    sub_wt = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x], reverse=True) # ascending order
    for node in sorder:
        sub_wt.append((node, substrate.node_weights[node]))
    #log1.info(f"\t\tSubstrate node before mapping VNR-{req_no} is {sub_wt}")
    sub_wt = []
    for edge in substrate.edges:
        sub_wt.append((edge, substrate.edge_weights[edge]))
    #log1.info(f"\t\tSubstrate edge before mapping VNR-{req_no} is {sub_wt}")
    #log1.info(f"\t\tNode map of VNR-{req_no} is {req_map.node_map}")
    #log1.info(f"\t\tEdge map of VNR-{req_no} is {req_map.edge_map}")
    for edge, path in req_map.edge_map.items():
        edge = edge[1]
        for i in range(1,len(path)):
            substrate.edge_weights[(path[i - 1], path[i])] -= virtual.edge_weights[edge]
            substrate.edge_weights[(path[i], path[i-1])] -= virtual.edge_weights[edge]
    for node in range(vne_list[req_no].nodes):
        substrate.node_weights[req_map.node_map[node]] -= virtual.node_weights[node]
    sub_wt = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x], reverse=True) # ascending order
    for node in sorder:
        sub_wt.append((node, substrate.node_weights[node]))
    #log1.info(f"\t\tSubstrate after mapping VNR-{req_no} is {sub_wt}")
    sub_wt = []
    for edge in substrate.edges:
        sub_wt.append((edge, substrate.edge_weights[edge]))
    #log1.info(f"\t\tSubstrate edge after mapping VNR-{req_no} is {sub_wt}")
    return True
    
def main():
    substrate, vne_list = helper.read_pickle()
    # logging.basicConfig(filename="vikor.log",filemode="w", level=#log1.info)

    #log1.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    #log1.info(f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    #log1.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge,substrate.edge_weights[edge]))
    #log1.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK")

    #log1.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    for vnr in range(len(vne_list)):
        #log1.info(f"\t\tTotal number of nodes and edges in VNR-{vnr} is : {vne_list[vnr].nodes} and {len(vne_list[vnr].edges)}")
        temp = []
        for node in range(vne_list[vnr].nodes):
            temp.append((node, vne_list[vnr].node_weights[node]))
        #log1.info(f"\t\tNodes of the VNR-{vnr} with weight are : {temp}")
        temp = []
        for edge in vne_list[vnr].edges:
            temp.append((edge, vne_list[vnr].edge_weights[edge]))
        # if vnr == len(vne_list)-1:
        #     #log1.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}\n\n")
        # else:
        #     #log1.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}")        

    start_time = datetime.now().time()
    accepted = 0
    revenue = 0
    curr_map = dict() # only contains the requests which are successfully mapped
    pre_resource_edgecost = sum(substrate.edge_weights.values())//2 # total available bandwidth of the physical network
    pre_resource_nodecost = sum(substrate.node_weights.values()) # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost
    revenue_list = [-1 for _ in range(len(vne_list))]
    for req in range(len(vne_list)):
        revenue_list[req] = sum(vne_list[req].node_weights.values()) + sum(vne_list[req].edge_weights.values())//2
    req_order = sorted(list(range(len(vne_list))), key=lambda x:revenue_list[x])

    for req_no in req_order:
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is  None:
            #log1.warning(f"\tNode mapping not possible for req no {req_no}\n")
            continue
        req_map = temp_map(vne_list, req_no, req_map)
        if not edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list):
            #log1.warning(f"\tEdge mapping not possible for req no {req_no}\n")
            continue
        accepted += 1
        req_map.total_cost = req_map.node_cost + req_map.edge_cost
        #log1.info(f"\t\tMapping for request {req_no} is done successfully!! {req_map.node_map} with revenue {sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2} and total cost {req_map.total_cost}\n")
        curr_map[req_no] = req_map
        revenue += sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2

    ed_cost  = 0
    no_cost = 0
    for request in curr_map.values():
        ed_cost += request.edge_cost # total bandwidth for all the mapped requests
        no_cost += request.node_cost # total crb for all the mapped requests

    tot_cost = ed_cost + no_cost
    post_resource = sum(substrate.node_weights.values()) + sum(substrate.edge_weights.values())//2
    
    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    
    print(f"\n\n\tVIKOR\nThe revenue is {revenue} and total cost is {tot_cost}")
    print(f"Total number of requests embedded is {accepted} out of {len(vne_list)}")
    print(f"Embedding ratio is {accepted/len(vne_list)}")
    print(f"Availabe substrate resources before mapping is {pre_resource}")
    print(f"Consumed substrate resources after mapping is {pre_resource - post_resource}")
    print(f"Average link utilization {ed_cost/pre_resource_edgecost}")
    print(f"Average node utilization {no_cost/pre_resource_nodecost}")
    print(f"Average execution time {duration/len(vne_list)}")

    #log1.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK AFTER MAPPING VNRs")
    #log1.info(f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    #log1.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge,substrate.edge_weights[edge]))
    #log1.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n")   
    
    # log1.info(f"\t\tThe revenue is {revenue} and total cost is {tot_cost}")
    if tot_cost == 0:
        # log1.error(f"\t\tCouldn't embedd any request")
        return None

    # log1.info(f"\t\tThe revenue to cost ratio is {(revenue/tot_cost)*100:.4f}%")
    # log1.info(f"\t\tTotal number of requests embedded is {accepted} out of {len(vne_list)}")
    # log1.info(f"\t\tEmbedding ratio is {(accepted/len(vne_list))*100:.4f}%")
    # log1.info(f"\t\tAvailabe substrate resources before mapping is {pre_resource}")
    # log1.info(f"\t\tConsumed substrate resources after mapping is {pre_resource - post_resource}")
    # log1.info(f"\t\tAverage link utilization {(ed_cost/pre_resource_edgecost)*100:.4f}%")
    # log1.info(f"\t\tAverage node utilization {(no_cost/pre_resource_nodecost)*100:.4f}%")
    # log1.info(f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n")
    # logging.shutdown()
    output_dict = {
        "revenue": revenue,
        "total_cost" : tot_cost,
        "accepted" : accepted,
        "total_request": len(vne_list),
        "pre_resource": pre_resource,
        "post_resource": post_resource,
        "avg_link": (ed_cost/pre_resource_edgecost)*100,
        "avg_node": (no_cost/pre_resource_nodecost)*100,
        "avg_exec": (duration),
    }
    return output_dict


if __name__ == '__main__':
    '''
    The output can be different for same input file also.
    Because there can be multiple shortest paths from source to destination.
    '''
    helper.setup_logger('log1','vikor.log')
    main()