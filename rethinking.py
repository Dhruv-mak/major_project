import helper
import sys
import copy
from datetime import datetime, date
import logging
import random


class temp_map:
    def __init__(self, vne_list,req_no, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        self.node_cost += sum(vne_list[req_no].node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = []
        self.edges = []

# Also check for distance constraint(location)
def node_map(substrate, virtual, req_no):
    map = [0 for x in range(virtual.nodes)]
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x], reverse=True) # ascending order
    vorder = sorted([a for a in range(virtual.nodes)], key = lambda x: virtual.node_weights[x], reverse=True) 
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

def selectPaths(i, length, all_paths, chromosome, init_pop):

    if len(chromosome) == length:
        init_pop.append(copy.deepcopy(chromosome))
        if len(init_pop) == 8:
            return
    else:
        for gene in all_paths[i]:
            chromosome.append(gene)
            selectPaths(i+1, length, all_paths, chromosome, init_pop)
            chromosome.pop()


def edge_map(substrate, virtual, req_no, req_map, vne_list):
    substrate_copy = copy.deepcopy(substrate)
    all_paths = []
    for edge in virtual.edges:
        if int(edge[0]) < int(edge[1]):
            weight = virtual.edge_weights[edge]
            left_node = req_map.node_map[int(edge[0])]
            right_node = req_map.node_map[int(edge[1])]
            paths = substrate_copy.printAllPaths(str(left_node), str(right_node), weight)     #find all paths from src to dst 
            print(paths)
            if paths == None:
                return None
            all_paths.append(paths)
    logging.info(f"{all_paths}")
    initial_population = []
    chromosome = []
    selectPaths(0, len(virtual.edges)//2, all_paths, chromosome, initial_population)

    logging.info(f"{initial_population}")
    return initial_population
            
    
def main():
    substrate, vne_list = helper.read_pickle()
    logging.basicConfig(filename="rethinking.log",filemode="w", level=logging.INFO)
    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    logging.info(f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge,substrate.edge_weights[edge]))
    logging.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK")

    logging.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    for vnr in range(len(vne_list)):
        logging.info(f"\t\tTotal number of nodes and edges in VNR-{vnr} is : {vne_list[vnr].nodes} and {len(vne_list[vnr].edges)}")
        temp = []
        for node in range(vne_list[vnr].nodes):
            temp.append((node, vne_list[vnr].node_weights[node]))
        logging.info(f"\t\tNodes of the VNR-{vnr} with weight are : {temp}")
        temp = []
        for edge in vne_list[vnr].edges:
            temp.append((edge, vne_list[vnr].edge_weights[edge]))
        if vnr == len(vne_list)-1:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}\n\n")
        else:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}")        

    start_time = datetime.now().time()
    accepted = 0
    revenue = 0
    curr_map = dict() # only contains the requests which are successfully mapped
    pre_resource_edgecost = sum(substrate.edge_weights.values())//2 # total available bandwidth of the physical network
    pre_resource_nodecost = sum(substrate.node_weights.values()) # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost
    
    req_order = list(range(len(vne_list)))
    random.shuffle(req_order)
    for req_no in req_order:
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is  None:
            print(f"Node mapping not possible for req no {req_no}")
            logging.warning(f"\tNode mapping not possible for req no {req_no}\n")
            continue
        req_map = temp_map(vne_list, req_no, req_map)

        initial_population = edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list)
        if initial_population == None:
            print(f"\nEdge is successful\n")
        else:
            print(f"\nEdge is not successful\n")

        

if __name__ == '__main__':
    main()