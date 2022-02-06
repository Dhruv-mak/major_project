from re import X
import helper
import copy
from datetime import datetime, date
import logging
import random
from rethinking_helper import *


def main():
    substrate, vne_list = helper.read_pickle()
    logging.basicConfig(filename="rethinking.log", filemode="w", level=logging.INFO)
    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    logging.info(
        f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} "
    )
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge, substrate.edge_weights[edge]))
    logging.info(
        f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK"
    )

    logging.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    for vnr in range(len(vne_list)):
        logging.info(
            f"\t\tTotal number of nodes and edges in VNR-{vnr} is : {vne_list[vnr].nodes} and {len(vne_list[vnr].edges)}"
        )
        temp = []
        for node in range(vne_list[vnr].nodes):
            temp.append((node, vne_list[vnr].node_weights[node]))
        logging.info(f"\t\tNodes of the VNR-{vnr} with weight are : {temp}")
        temp = []
        for edge in vne_list[vnr].edges:
            temp.append((edge, vne_list[vnr].edge_weights[edge]))
        if vnr == len(vne_list) - 1:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}\n\n")
        else:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}")

    start_time = datetime.now().time()
    accepted = 0
    revenue = 0
    curr_map = dict()  # only contains the requests which are successfully mapped
    pre_resource_edgecost = (
        sum(substrate.edge_weights.values()) // 2
    )  # total available bandwidth of the physical network
    pre_resource_nodecost = sum(
        substrate.node_weights.values()
    )  # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost

    req_order = list(range(len(vne_list)))
    random.shuffle(req_order)
    for req_no in req_order:
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is None:
            logging.warning(f"\tNode mapping not possible for req no {req_no}\n")
            continue
        req_map = temp_map(vne_list, req_no, req_map)
        # [[PATH for edge 1], [PATH for edge 2]]
        population = edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list)
        initial_population = []
        if population is None:
            logging.warning(f"\t\tinitial population can't be generated for {req_no}")
            continue
        population_set = set()
        for i in population:
            abhi_map = i
            abhi_map.edge_map = i.edge_map
            j = 0
            for edge in vne_list[req_no].edges:
                if int(edge[0]) > int(edge[1]):
                    abhi_map.edges.append(edge)
                    abhi_map.edge_weight.append(vne_list[req_no].edge_weights[edge])
                    abhi_map.path_cost.append(
                        vne_list[req_no].edge_weights[edge] * len(abhi_map.edge_map[j])
                    )
                    abhi_map.edge_cost += abhi_map.edge_weight[j] * len(
                        abhi_map.edge_map[j]
                    )
                    j += 1
            abhi_map.total_cost = abhi_map.node_cost + abhi_map.edge_cost
            abhi_map.fitness = get_fitness(abhi_map, vne_list[req_no])
            initial_population.append(abhi_map)
            population_set.add(get_hashable_map(abhi_map))
        logging.info(f"\t\tInitial_population for req no: {req_no}::::")
        for i in initial_population:
            logging.info(f"\t\t\t{i.edge_map}\tfitness: {i.fitness:.4f}\t tot_cost: {i.total_cost}")
        logging.info(f"\n\n")
        elite_population = copy.deepcopy(initial_population)
        for _ in range(8):
            logging.info(f"\t\t\t\t ITERATION {_}")
            i = 0
            while i < 8:
                i += 1
                parent1, parent2 = tournament_selection(
                    elite_population, vne_list, req_no
                )
                child1, child2 = elastic_crossover(
                    parent1, parent2, population_set, substrate, vne_list[req_no], i
                )   # last argument i is for identify which inside loop 
                if child1 is not None:
                    child1.edge_cost = sum(child1.path_cost)
                    child1.total_cost = child1.node_cost + child1.edge_cost
                    elite_population.append(child1)
                    population_set.add(get_hashable_map(child1))
                    child1.fitness = get_fitness(child1, vne_list[req_no])
                    logging.info(f"\t\t\t{i}-Added Crossovered Child1 {child1.edge_map}\tfitness: {child1.fitness:.4f}\ttot_cost: {child1.total_cost}")
                if child2 is not None:
                    child2.edge_cost = sum(child2.path_cost)
                    child2.total_cost = child2.node_cost + child2.edge_cost
                    elite_population.append(child2)
                    population_set.add(get_hashable_map(child2))
                    child2.fitness = get_fitness(child2, vne_list[req_no])
                    logging.info(f"\t\t\t{i}-Added Crossovered Child2: {child2.edge_map}\tfitness: {child2.fitness:.4f}\ttot_cost: {child2.total_cost}")
                if child1 is not None and child2 is not None:
                    mutated_child1, mutated_child2 = mutate(
                        child1, child2, substrate, population_set, vne_list[req_no], i
                    ) # last argument i is for identify which inside loop
                    if mutated_child1 is not None:
                        mutated_child1.edge_cost = sum(mutated_child1.path_cost)
                        mutated_child1.total_cost = (
                            mutated_child1.node_cost + mutated_child1.edge_cost
                        )
                        elite_population.append(mutated_child1)
                        population_set.add(get_hashable_map(mutated_child1))
                        mutated_child1.fitness = get_fitness(
                            mutated_child1, vne_list[req_no]
                        )
                        logging.info(f"\t\t\t{i}-Added Muted Child1 {mutated_child1.edge_map}\tfitness: {mutated_child1.fitness:.4f}\ttot_cost: {mutated_child1.total_cost}")
                    if mutated_child2 is not None:
                        mutated_child2.edge_cost = sum(mutated_child2.path_cost)
                        mutated_child2.total_cost = (
                            mutated_child2.node_cost + mutated_child2.edge_cost
                        )
                        elite_population.append(mutated_child2)
                        population_set.add(get_hashable_map(mutated_child2))
                        mutated_child2.fitness = get_fitness(
                            mutated_child2, vne_list[req_no]
                        )
                        logging.info(f"\t\t\t{i}-Added Muted Child2 {mutated_child2.edge_map}\tfitness: {mutated_child2.fitness:.4f}\ttot_cost: {mutated_child2.total_cost}")
            elite_population, population_set = import_elite(elite_population)
            logging.info(f"")
            logging.info(f"\t\t\telite population after iteration {_}")
            for i in initial_population:
                logging.info(f"\t\t\t{i.edge_map}\tfitness: {i.fitness:.4f}\ttot_cost: {i.total_cost}")
            logging.info(f"")
        selected_map = get_best_map(elite_population)
        
        logging.info(f"\n")
        ls = dict()
        c =0
        for ed in selected_map.edges:
            ls[ed] = selected_map.edge_map[c]
            c += 1
        logging.info(f"\t\tThe selected chromosome for VNR {req_no} is {selected_map.edge_map}\tfitness: {selected_map.fitness:.4f}\ttot_cost: {selected_map.total_cost}")
        logging.info(f"\t\tThe node map of VNR {req_no} is {selected_map.node_map}")
        logging.info(f"\t\tThe edge map of VNR {req_no} is {ls}")
        
        sub_wt = []
        for node in range(substrate.nodes):
            sub_wt.append((node, substrate.node_weights[node]))
        logging.info(f"\t\tSubstrate node before mapping VNR-{req_no} is {sub_wt}")
        sub_wt = []
        for edge in substrate.edges:
            sub_wt.append((edge, substrate.edge_weights[edge]))
        logging.info(f"\t\tSubstrate edge before mapping VNR-{req_no} is {sub_wt}")

        substract_from_substrate(substrate, vne_list[req_no], selected_map)
        
        sub_wt = []
        for node in range(substrate.nodes):
            sub_wt.append((node, substrate.node_weights[node]))
        logging.info(f"\t\tSubstrate after mapping VNR-{req_no} is {sub_wt}")
        sub_wt = []
        for edge in substrate.edges:
            sub_wt.append((edge, substrate.edge_weights[edge]))
        logging.info(f"\t\tSubstrate edge after mapping VNR-{req_no} is {sub_wt}")

        accepted += 1
        curr_map[req_no] = selected_map
        revenue += sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2
        logging.info(f"\n\n")

    ed_cost = 0
    no_cost = 0
    for request in curr_map.values():
        ed_cost += request.edge_cost  # total bandwidth for all the mapped requests
        no_cost += request.node_cost  # total crb for all the mapped requests

    tot_cost = ed_cost + no_cost
    post_resource = (
        sum(substrate.node_weights.values()) + sum(substrate.edge_weights.values()) // 2
    )

    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(
        date.min, start_time
    )

    print(f"\n\nThe revenue is {revenue} and total cost is {tot_cost}")
    print(f"Total number of requests embedded is {accepted}")
    print(f"Embedding ratio is {accepted/len(vne_list)}")
    print(f"Availabe substrate resources before mapping is {pre_resource}")
    print(
        f"Consumed substrate resources after mapping is {pre_resource - post_resource}"
    )
    print(f"Average link utilization {ed_cost/pre_resource_edgecost}")
    print(f"Average node utilization {no_cost/pre_resource_nodecost}")
    print(f"Average execution time {duration/len(vne_list)}")

    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK AFTER MAPPING VNRs")
    logging.info(
        f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} "
    )
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge, substrate.edge_weights[edge]))
    logging.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n")

    logging.info(f"\t\tThe revenue is {revenue} and total cost is {tot_cost}")
    if tot_cost == 0:
        logging.error(f"\t\tCouldn't embedd any request")
        return

    logging.info(f"\t\tThe revenue to cost ratio is {(revenue/tot_cost)*100:.4f}%")
    logging.info(
        f"\t\tTotal number of requests embedded is {accepted} out of {len(vne_list)}"
    )
    logging.info(f"\t\tEmbedding ratio is {(accepted/len(vne_list))*100:.4f}%")
    logging.info(f"\t\tAvailabe substrate resources before mapping is {pre_resource}")
    logging.info(
        f"\t\tConsumed substrate resources after mapping is {pre_resource - post_resource}"
    )
    logging.info(
        f"\t\tAverage link utilization {(ed_cost/pre_resource_edgecost)*100:.4f}%"
    )
    logging.info(
        f"\t\tAverage node utilization {(no_cost/pre_resource_nodecost)*100:.4f}%"
    )
    logging.info(
        f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n"
    )
    # logging.shutdown()
    output_dict = {
        "revenue": revenue,
        "total_cost": tot_cost,
        "accepted": accepted,
        "total_request": len(vne_list),
        "pre_resource": pre_resource,
        "post_resource": post_resource,
        "avg_link": (ed_cost / pre_resource_edgecost) * 100,
        "avg_node": (no_cost / pre_resource_nodecost) * 100,
        "avg_exec": (duration),
    }
    return output_dict


if __name__ == "__main__":
    main()
