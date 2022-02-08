import random
import sys
import copy
def get_index(vne_list):
    index_chromosome = list()
    for i in range(len(vne_list)):
        for j in range(vne_list[i].nodes):
            index_chromosome.append(Gene(i, j, vne_list))
    return index_chromosome

def tounament_selection(elite_population, vne_list):
    random.shuffle(elite_population)
    sz = len(elite_population)//2
    group1 = elite_population[:sz]
    group2 = elite_population[sz:]
    parent1 = temp_map(vne_list)
    for j in range(len(group1)):
        if parent1.total_cost > group1[j].total_cost:
            parent1 = group1[j]
    parent2 = temp_map(vne_list)
    for j in range(len(group2)):
        if parent2.total_cost > group2[j].total_cost:
            parent2 = group2[j]
    return parent1, parent2

def initialize_population(substrate, vne_list, index_chromosome):
    population_set = set()
    population = []
    itr = 0
    p = 0
    while p < 8:
        map = []
        for i in range(len(vne_list)):
            map += random.sample(range(0, substrate.nodes - 1), vne_list[i].nodes)
        map = temp_map(vne_list, map)
        itr += 1
        if check_node_map(copy.deepcopy(index_chromosome), map, copy.deepcopy(substrate)) and check_edge_map(map, copy.deepcopy(substrate), vne_list):
            p += 1
            print(f"{map.node_map}\n\n")
            map.total_cost = map.node_cost + map.edge_cost
            if tuple(map.node_map) not in population_set:
                population.append(map)
                population_set.add(tuple(map.node_map))
            else:
                some_map = find_map(map)
                if some_map.total_cost > map.total_cost:
                    some_map = map
        if itr>10000:
            print(f"Don't have enough populations required 8 got {p}")
            return
    return population, population_set


def check_node_map(index_chromosome, tempo_map, substrate_copy):
    for i in range(len(tempo_map.node_map)):
        if (substrate_copy.node_weights[tempo_map.node_map[i]]- index_chromosome[i].node_weight>= 0):
            substrate_copy.node_weights[tempo_map.node_map[i]] -= index_chromosome[i].node_weight
        else:
            return False
    return True


def check_edge_map(tempo_map, substrate_copy, vne_list):
    index = 0
    for i in range(len(vne_list)):
        for edge in vne_list[i].edges:
            if int(edge[0]) < int(edge[1]):
                weight = vne_list[i].edge_weights[(edge[0], edge[1])]
                left_node = str(tempo_map.node_map[int(edge[0]) + index])
                right_node = str(tempo_map.node_map[int(edge[1]) + index])
                path = substrate_copy.findPathFromSrcToDst(left_node, right_node, weight)
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

def check_edge_map2(tempo_map, substrate_copy, vne_list):
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

def check_compatibility(child1, child2, vne_list):
    left_pos = 0
    right_pos = 0
    for i in range(len(vne_list)):
        temp_set_1 = set()
        temp_set_2 = set()
        right_pos += vne_list[i].nodes
        for j in range(left_pos, right_pos):
            if (child1.node_map[j] not in temp_set_1 and child2.node_map[j] not in temp_set_2):
                temp_set_1.add(child1.node_map[j])
                temp_set_2.add(child2.node_map[j])
            else:
                return False
        left_pos = j
    return True


def improved_crossover(parent1, parent2, index_chromosome, substrate, vne_list):
    sim_index = []
    for i in range(len(parent1.node_map)):
        if parent1.node_map[i] == parent2.node_map[i]:
            sim_index.append(1)
        else:
            sim_index.append(0)
    hemming_distance = sum(sim_index)
    if hemming_distance > 2:
        ran_pos = random.randint(sim_index.index(1), len(sim_index) - sim_index[::-1].index(1) - 1)
        child1 = temp_map(vne_list, parent1.node_map[:ran_pos] + parent2.node_map[ran_pos:])
        child2 = temp_map(vne_list, parent2.node_map[:ran_pos] + parent1.node_map[ran_pos:])
        if check_compatibility(child1, child2, vne_list):
            if (
                    check_node_map(copy.deepcopy(index_chromosome), child1, copy.deepcopy(substrate))
                    and check_edge_map2(child1, copy.deepcopy(substrate), vne_list)
                    and check_node_map(copy.deepcopy(index_chromosome), child2, copy.deepcopy(substrate))
                    and check_edge_map2(child2, copy.deepcopy(substrate), vne_list)
                ):
                    return child1, child2
    return parent1, parent2


class temp_map:
    def __init__(self, vne_list, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        for i in vne_list:
            self.node_cost += sum(i.node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()


class Gene:
    def __init__(self, vne_index, node_no, vne_list) -> None:
        self.vne_index = vne_index
        self.node_no = node_no
        self.node_weight = vne_list[vne_index].node_weights[node_no]


def mutate(child1, child2, substrate, vne_list, index_chromosome):
    for _ in range(3):
        mutated_child1 = temp_map(vne_list)
        mutated_child2 = temp_map(vne_list)
        re_mutated_child1 = temp_map(vne_list)
        re_mutated_child2 = temp_map(vne_list)
        mutated_child1.node_map = child1.node_map
        mutated_child2.node_map = child2.node_map
        mutated_child1.node_map[random.randint(0, len(index_chromosome) - 1)] = random.randint(0, substrate.nodes - 1)
        mutated_child2.node_map[random.randint(0, len(index_chromosome) - 1)] = random.randint(0, substrate.nodes - 1)
        if check_compatibility(mutated_child1, mutated_child2, vne_list):
            if check_node_map(index_chromosome, mutated_child1, copy.deepcopy(substrate)) and check_edge_map2(mutated_child1, copy.deepcopy(substrate), vne_list):
                re_mutated_child1 = mutated_child1
            if check_node_map(index_chromosome, mutated_child2, copy.deepcopy(substrate)) and check_edge_map2(mutated_child2, copy.deepcopy(substrate), vne_list):
                re_mutated_child2 = mutated_child2
        else:
            continue
    if len(re_mutated_child2.node_map) != 0 and len(re_mutated_child1.node_map) != 0:
        return re_mutated_child1, re_mutated_child2
    else:
        return None, None


def import_elite(population):
    return sorted(population, key=lambda a: a.total_cost)


def find_map(random_map, population):
    for i in population:
        if random_map.node_map == i.node_map:
            return i

def print_vne(bracket,i):
    k = 0
    for j in range(len(i.node_map)) :
        if j==0:
            k += 1
            print("[ (", end="")
        elif j == bracket[k]:
            k += 1
            print("), (",end = "")
        if(j == bracket[k]-1):
            print(i.node_map[j],end="")
        else:
            string = str(i.node_map[j])
            print(i.node_map[j],end=", ")
    print(") ]",end = " ")