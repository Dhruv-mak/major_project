import helper
from vrmap_helper import *
import random
import copy
from datetime import datetime, date
import pickle

def main():
    start_time = datetime.now().time()
    bracket = []
    substrate, vne_list = helper.read_pickle()

    index_chromosome = get_index(vne_list)
    population = set()
    population, population_set = initialize_population(substrate, vne_list, index_chromosome)
     
    
    # print("The node mappings are:")
    # for i in population:
    #     print_vne(bracket,i)

    elite_population = copy.deepcopy(population)
    for _ in range(8):
        print("\n\n ITERATION", _)
        i=0
        while i<8:
            i += 1
            parent1, parent2 = tounament_selection(elite_population, vne_list)
            for _ in range(300):
                offspring1, offspring2 = improved_crossover(parent1, parent2, index_chromosome, substrate, vne_list)
                if offspring1.node_map != parent1.node_map and offspring2.node_map != parent2.node_map:
                    break
            offspring1.total_cost = offspring1.node_cost + offspring1.edge_cost
            offspring2.total_cost = offspring2.node_cost + offspring2.edge_cost
            random_no = random.random()
            mutation_rate = 0.15
            if random_no < mutation_rate:
                for l in range(300):
                    mutated_child1, mutated_child2 = mutate(copy.deepcopy(offspring1), copy.deepcopy(offspring2), substrate, vne_list, index_chromosome)
                    if mutated_child1 is not None and mutated_child2 is not None:
                        break
                if mutated_child2 is not None and mutated_child1 is not None:
                    if tuple(mutated_child1.node_map) not in population_set:
                        mutated_child1.total_cost = (mutated_child1.node_cost + mutated_child1.edge_cost)
                        print(" mutated  child: ",end = "")
                        # print_vne(bracket,mutated_child1)
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
                        # print_vne(bracket,mutated_child2)
                        population.append(mutated_child2)
                        elite_population.append(mutated_child2)
                        population_set.add(tuple(mutated_child2.node_map))
                    else:
                        some_map = find_map(mutated_child2)
                        if some_map.total_cost > mutated_child2.total_cost:
                            some_map = mutated_child2
            elif offspring1 != parent1 and offspring2 != parent2:
                if tuple(offspring1.node_map) not in population_set:
                    print("croosover child: ",end = "")
                    # print_vne(bracket,offspring1)
                    population.append(offspring1)
                    elite_population.append(offspring1)
                    population_set.add(tuple(offspring1.node_map))
                else:
                    some_map = find_map(offspring1, population)
                    if some_map.total_cost > offspring1.total_cost:
                        some_map = offspring1
                if tuple(offspring2.node_map) not in population_set:
                    print("croosover child: ",end = "")
                    # print_vne(bracket,offspring2)
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

    print("\n\nELITE POPULATION")
    # for i in elite_population:
    #     print_vne(bracket,i)
    print(f"\nThe selected map is ",end="")
    # print_vne(bracket,selected_map)
    print("Embedding ratio is 100%\n")

    print("\nLog file is also generated in the current directory with file name logfile.txt\n")


    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    print(duration)

    output = {"substrate": substrate, "vne_list" : vne_list, "index_chromosome": index_chromosome, "selected_map": selected_map}
    pickle_file = open("mapping.pickle", "wb")
    pickle.dump(output, pickle_file)

if __name__ == "__main__":
    main()
