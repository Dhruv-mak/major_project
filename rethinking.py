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
        self.edge_weight = []
        self.path_cost = []
        self.fitness = 0

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
            
def tournament_selection(elite_population):
    random.shuffle(elite_population)
    sz = len(elite_population)//2
    group1 = elite_population[:sz]
    group2 = elite_population[sz:]
    parent1 = temp_map()
    # confirm for fitness value
    for j in range(len(group1)):
        if parent1.fitness < group1[j].fitness:
            parent1 = group1[j]
    parent2 = temp_map()
    for j in range(len(group2)):
        if parent2.fitness < group2[j].fitness:
            parent2 = group2[j]
    return parent1, parent2

def elastic_crossover(parent1, parent2, population_set):
    maxx = len(parent1.node_map)
    parent2_copy = copy.deepcopy(parent2)
    parent1_copy = copy.deepcopy(parent1)
    parent1_pos = random.sample(range(len(parent1.edge_map)), random.randint(1,maxx-1))
    for i in range(len(parent1_pos)):
        parent1[parent1_pos[i]] = parent2_copy[parent1_pos[i]]
    parent2_pos = random.sample(range(len(parent1.edge_map)), random.randint(1,maxx-1))
    for i in range(len(parent2_pos)):
        parent2[parent2_pos[i]] = parent1_copy[parent2_pos[i]]
    if check_compatibility(parent1):
        parent1 = None
        print("could not add child1 due to incompatibility")
    if check_compatibility(parent2):
        parent2 = None
        print("could not add child2 due to incompatibility")
    if get_hashable_map(parent1) in population_set:
        print("Could not get distict child1")
        parent1 = None
    if get_hashable_map(parent2) in population_set:
        print("could not get distict child2")
        parent2 = None
    return parent1, parent2
    
def mutate(child1, child2, substrate, population_set):
    random_no = random.randint(0, len(child1.edge_map))
    sel_path = child1.edge_map[random_no]
    edge = (str(sel_path[0]), str(sel_path[1]))
    child1.edge_map[random_no] = substrate.findPathFromSrcToDst(edge[0], edge[1], child1.edge_weight[random_no])
    random_no = random.randint(0, len(child2.edge_map))
    sel_path = child2.edge_map[random_no]
    edge = (str(sel_path[0]), str(sel_path[1]))
    child2.edge_map[random_no] = substrate.findPathFromSrcToDst(edge[0], edge[1], child2.edge_weight[random_no])
    if check_compatibility(child1):
        child1 = None
        print("could not add child1 due to incompatibility")
    if check_compatibility(child2):
        child2 = None
        print("could not add child2 due to incompatibility")
    if get_hashable_map(child1) in population_set:
        print("Could not get distict child1")
        child1 = None
    if get_hashable_map(child2) in population_set:
        print("could not get distict child2")
        child2 = None
    return child1, child2

def get_hashable_map(chromosome):
    temp_list = []
    for path in chromosome.edge_map:
        temp_list.append(tuple(path))
    return tuple(temp_list)

def check_compatibility(chromosome, substrate_copy):
    for i, path in enumerate(chromosome.edge_map):
        for i in range(1, len(path)):
            edge = (str(path[i-1]), str(path[i]))
            if substrate_copy.edge_weights[edge] < chromosome.edge_weight[i]:
                return False
    return True

def import_elite(population):
    population = sorted(population, key=lambda x:population[x].fitness, reverse=True)[:8]
    population_set = set()
    for i in population:
        population_set.add(get_hashable_map[i])
    return population, population_set        

def get_best_map(population):
    return sorted(population, key= lambda x:population[x].fitness, reverse=True)[0]

def substract_from_substrate(substrate, virtual, selected_map):
    for i, node in enumerate(selected_map.node_map):
        substrate.node_weights[node] -= virtual.node_weights[i]
    for i, path in enumerate(selected_map.edge_map):
        for j in range(1, len(path)):
            substrate.edge_weights[(str(path[j-1]), str(path[j]))] -= selected_map.edge_weight[i]

def get_fitness(chromosome, substrate):
    pass

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
        # [[PATH for edge 1], [PATH for edge 2]]
        population = edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list)
        initial_population = []
        if population is None:
            print(f"initial population can't be generated for {req_no}")
            continue
        population_set = set()
        for i in population:
            abhi_map = temp_map(vne_list, req_no, req_map.node_map)
            abhi_map.edge_map.append(i)
            j = 0
            hop_count = 0
            delay_sum = 0
            for edge in vne_list[req_no].edges:
                abhi_map.edges.append(edge)
                abhi_map.edge_weight.append(vne_list[req_no].edge_weights[edge])
                abhi_map.path_cost.append(abhi_map.edge_weight[j]*len(abhi_map.edge_map[j]))
                abhi_map.edge_cost += abhi_map.edge_weight[j]*len(abhi_map.edge_map[j])
                hop_count += len(abhi_map.edge_map[j])
                delay_sum += hop_count - 1
                j+=1
            abhi_map.total_cost = abhi_map.node_cost + abhi_map.edge_cost
            abhi_map.fitness = (1/abhi_map.total_cost) + (1/hop_count) + 1
            initial_population.append(abhi_map)
            population_set.add(get_hashable_map(abhi_map))
        elite_population = copy.deepcopy(population)
        for _ in range(8):
            print("\n\n ITERATION", _)
            i=0
            while i<8:
                i += 1
                parent1, parent2 = tournament_selection(elite_population)
                child1, child2 = elastic_crossover(parent1, parent2, population_set)
                if child1 is not None:
                    child1.edge_cost = sum(child1.path_cost)
                    child1.total_cost = child1.node_cost + child1.edge_cost
                    elite_population.append(child1)
                    population_set.add(get_hashable_map(child1))
                if child2 is not None:
                    child2.edge_cost = sum(child2.path_cost)
                    child2.total_cost = child2.node_cost + child2.edge_cost
                    elite_population.append(child2)
                    population_set.add(get_hashable_map(child2))

                mutated_child1, mutated_child2 = mutate(child1, child2, substrate, population_set)
                if mutated_child1 is not None:
                    mutated_child1.edge_cost = sum(mutated_child1.path_cost)
                    mutated_child1.total_cost = mutated_child1.node_cost + mutated_child1.edge_cost
                    elite_population.append(mutated_child1)
                    population_set.add(get_hashable_map(mutated_child1))
                if child2 is not None:
                    mutated_child2.edge_cost = sum(mutated_child2.path_cost)
                    mutated_child2.total_cost = mutated_child2.node_cost + mutated_child2.edge_cost
                    elite_population.append(mutated_child2)
                    population_set.add(get_hashable_map(mutated_child2))

            elite_population, population_set = import_elite(elite_population)
        selected_map = get_best_map(elite_population)
        substract_from_substrate(substrate, vne_list[req_no], selected_map)
        accepted += 1
        curr_map[req_no] = selected_map

                


if __name__ == '__main__':
    main()