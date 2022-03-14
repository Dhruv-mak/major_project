import helper
from vrmap_helper import *
import random
import copy
from datetime import datetime, date
import pickle
import logging

def main():
    start_time = datetime.now().time()
    bracket = []
    revenue = 0
    substrate, vne_list = helper.read_pickle()
    copy_sub = copy.deepcopy(substrate)
    logging.basicConfig(filename="vrmap.log",filemode="w", level=logging.INFO)

    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    log_substrate(substrate)
    log_vnr(vne_list)

    index_chromosome, bracket, revenue = get_index(vne_list)
    population = set()
    population, population_set = initialize_population(substrate, vne_list, index_chromosome)
    if population is None or len(population) == 0:
        return  
    
    print("The node mappings are:")
    logging.info("\t\tThe initial node mappings are:")
    for i in population:
        print_vne(bracket,i)
        logging.info(f"\t\t{i.node_map}\ttotal cost: {i.total_cost}")

    elite_population = copy.deepcopy(population)
    if len(elite_population) > 1:
        for _ in range(2):
            print("\n\n ITERATION", _)
            logging.info(f"\n\n")
            logging.info(f"\t\tITERATION {_}")
            i=0
            while i<2:
                i += 1
                parent1, parent2 = tounament_selection(elite_population, vne_list)
                for _ in range(2):
                    offspring1, offspring2 = improved_crossover(parent1, parent2, index_chromosome, substrate, vne_list)
                    if offspring1.node_map != parent1.node_map and offspring2.node_map != parent2.node_map:
                        break
                offspring1.total_cost = offspring1.node_cost + offspring1.edge_cost
                offspring2.total_cost = offspring2.node_cost + offspring2.edge_cost
                random_no = random.random()
                mutation_rate = 0.15
                if random_no < mutation_rate:
                    for l in range(2):
                        mutated_child1, mutated_child2 = mutate(copy.deepcopy(offspring1), copy.deepcopy(offspring2), substrate, vne_list, index_chromosome)
                        if mutated_child1 is not None and mutated_child2 is not None:
                            break
                    if mutated_child2 is not None and mutated_child1 is not None:
                        if tuple(mutated_child1.node_map) not in population_set:
                            mutated_child1.total_cost = (mutated_child1.node_cost + mutated_child1.edge_cost)
                            print(" mutated  child: ",end = "")
                            logging.info(f"\t\tmutated  child1: {mutated_child1.node_map}\ttotal cost: {mutated_child1.total_cost}")
                            print_vne(bracket,mutated_child1)
                            population.append(mutated_child1)
                            elite_population.append(mutated_child1)
                            population_set.add(tuple(mutated_child1.node_map))
                        else:
                            some_map = find_map(mutated_child1, population)
                            if some_map.total_cost > mutated_child1.total_cost:
                                some_map = mutated_child1
                        if tuple(mutated_child2.node_map) not in population_set:
                            mutated_child2.total_cost = (mutated_child2.node_cost + mutated_child2.edge_cost)
                            print(" mutated  child: ",end = "")
                            logging.info(f"\t\tmutated  child2: {mutated_child2.node_map}\ttotal cost: {mutated_child2.total_cost}")
                            print_vne(bracket,mutated_child2)
                            population.append(mutated_child2)
                            elite_population.append(mutated_child2)
                            population_set.add(tuple(mutated_child2.node_map))
                        else:
                            some_map = find_map(mutated_child2, population)
                            if some_map.total_cost > mutated_child2.total_cost:
                                some_map = mutated_child2
                elif offspring1 != parent1 and offspring2 != parent2:
                    if tuple(offspring1.node_map) not in population_set:
                        print("croosover child: ",end = "")
                        logging.info(f"\t\tcrossovered  child1: {offspring1.node_map}\ttotal cost: {offspring1.total_cost}")
                        print_vne(bracket,offspring1)
                        population.append(offspring1)
                        elite_population.append(offspring1)
                        population_set.add(tuple(offspring1.node_map))
                    else:
                        some_map = find_map(offspring1, population)
                        if some_map.total_cost > offspring1.total_cost:
                            some_map = offspring1
                    if tuple(offspring2.node_map) not in population_set:
                        print("croosover child: ",end = "")
                        logging.info(f"\t\tcrossovered  child2: {offspring2.node_map}\ttotal cost: {offspring2.total_cost}")
                        print_vne(bracket,offspring2)
                        population.append(offspring2)
                        elite_population.append(offspring2)
                        population_set.add(tuple(offspring2.node_map))
                    else:
                        some_map = find_map(offspring2, population)
                        if some_map.total_cost > offspring2.total_cost:
                            some_map = offspring2
            elite_population = import_elite(population)[:8]

    selected_map = temp_map(vne_list)
    for i in range(len(population)):
        if population[i].total_cost < selected_map.total_cost:
            selected_map = population[i]

    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    print(duration)

    print("\n\nELITE POPULATION")
    logging.info(f"\n\n")
    logging.info(f"\t\tELITE POPULATION")
    for i in elite_population:
        print_vne(bracket,i)
        logging.info(f"\t\t{i.node_map}\ttotal cost: {i.total_cost}")

    logging.info(f"\n\n")
    logging.info(f"\t\tThe selected map is {selected_map.node_map}\ttotal cost: {selected_map.total_cost}")
    logging.info(f"\t\tedge map: {selected_map.edge_map}")
   
    path_cnt=0
    for ed in selected_map.edge_map:
        path_cnt += len(selected_map.edge_map[ed])
    path_cnt //=2
    pre_resource_edgecost = sum(substrate.edge_weights.values())//2
    pre_resource_nodecost = sum(substrate.node_weights.values())
    pre_resource = pre_resource_edgecost + pre_resource_nodecost

    substract_from_substrate(substrate, selected_map, index_chromosome, vne_list)

    post_resource_edgecost =0
    post_resource_nodecost=0
    utilized_nodes=0
    utilized_links=0
    for edge in substrate.edge_weights:
        post_resource_edgecost += substrate.edge_weights[edge]
        if substrate.edge_weights[edge]!=copy_sub.edge_weights[edge]:
            utilized_links += 1
    post_resource_edgecost //= 2
    for node in substrate.node_weights:
        post_resource_nodecost += substrate.node_weights[node]
        if substrate.node_weights[node] != copy_sub.node_weights[node]:
            utilized_nodes += 1

    post_resource = post_resource_edgecost + post_resource_nodecost
    log_substrate(substrate)    

    
    tot_cost = selected_map.total_cost
    logging.info(f"\t\tThe revenue is {revenue}\tTotal cost is {tot_cost}")
    logging.info(f"\t\tThe revenue to cost ratio is {(revenue/tot_cost)*100:.4f}%")
    logging.info(f"\t\tTotal number of requests embedded is {len(vne_list)} out of {len(vne_list)}")
    logging.info(f"\t\tEmbedding ratio is {(len(vne_list)/len(vne_list))*100:.4f}%\n")
    logging.info(f"\t\tTotal {utilized_nodes} nodes are utilized out of {len(substrate.node_weights)}")
    logging.info(f"\t\tTotal {utilized_links//2} links are utilized out of {len(substrate.edge_weights)//2}")
    logging.info(f"\t\tAverage node utilization is {(utilized_nodes/len(substrate.node_weights))*100:.4f}")
    logging.info(f"\t\tAverage link utilization is {(utilized_links/len(substrate.node_weights))*100:.4f}\n")
    logging.info(f"\t\tAvailabe substrate before embedding CRB: {pre_resource_nodecost} BW: {pre_resource_edgecost} total: {pre_resource}")
    logging.info(f"\t\tAvailabe substrate after embedding CRB: {post_resource_nodecost} BW: {post_resource_edgecost} total: {post_resource}")
    logging.info(f"\t\tConsumed substrate CRB: {pre_resource_nodecost-post_resource_nodecost} BW: {pre_resource_edgecost-post_resource_edgecost} total: {pre_resource - post_resource}\n")
    logging.info(f"\t\tAverage Path length is {(path_cnt/len(vne_list)):.4f}\n")    
    logging.info(f"\t\tAverage BW utilization {(selected_map.edge_cost/pre_resource_edgecost)*100:.4f}%")
    logging.info(f"\t\tAverage CRB utilization {(selected_map.node_cost/pre_resource_nodecost)*100:.4f}%")
    logging.info(f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n")
  
    print(f"\nThe selected map is ",end="")
    print_vne(bracket,selected_map)
    print(f"\n\t\tThe revenue is {revenue}\tTotal cost is {tot_cost}")
    print(f"\t\tThe revenue to cost ratio is {(revenue/tot_cost)*100:.4f}%")
    print(f"\t\tTotal number of requests embedded is {len(vne_list)} out of {len(vne_list)}")
    print(f"\t\tEmbedding ratio is {(len(vne_list)/len(vne_list))*100:.4f}%")
    print(f"\t\tAvailabe substrate resources before mapping is {pre_resource}")
    print(f"\t\tConsumed substrate resources after mapping is {pre_resource - post_resource}")
    print(f"\t\tAverage link utilization {(selected_map.edge_cost/pre_resource_edgecost)*100:.4f}%")
    print(f"\t\tAverage node utilization {(selected_map.node_cost/pre_resource_nodecost)*100:.4f}%")
    print(f"\t\tTotal Duration {duration} (HH:MM:SS)")
    print(f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n")
    print("\nLog file is also generated in the current directory with file name vrmap.log\n")

    # output = {"substrate": substrate, "vne_list" : vne_list, "index_chromosome": index_chromosome, "selected_map": selected_map}
    # pickle_file = open("mapping.pickle", "wb")
    # pickle.dump(output, pickle_file)

if __name__ == "__main__":
    main()
