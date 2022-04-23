
import copy
from collections import OrderedDict, deque
from datetime import datetime, date
import logging
from random import random
from betweenness_centrality import BetweennessCentrality
from eigenvector_centrality import EigenvectorCentrality
from entropy import WeightMatrix
from network_attributes import NetworkAttribute
# import pickle
import helper
import networkx as nx

log=logging
FORMAT = '%(levelname)s: %(message)s'
log.basicConfig(filename=r'EA_TOPSIS.log',
                    format=FORMAT,
                    filemode="w",
                    level=logging.DEBUG,
                    datefmt = '%Y-%m-%d %H:%M:%S %p')


def sort_node_rank(node_dict):
  d_sorted_by_value = OrderedDict(sorted(node_dict.items(), key=lambda x: x[1]))
  return d_sorted_by_value


def calculate_revenue(vne_list):
  vne_revenue_list = []
  bwd_unit_cost = 1  # cost of one unit bandwidth
  crb_unit_cost = 1  # cost of one unit CRB
  for vne_node in vne_list:
    bandWidth = vne_node[1]
    crb = vne_node[2]
    bandWidthSum = 0
    crbSum = 0
    for i in crb:
      crbSum += crb[i]
    for i in bandWidth:
      bandWidthSum += bandWidth[i]
    bandWidthSum = bandWidthSum // 2 # ALPHA=1  and BEETA=1 BALANCING FACTOR
    revenue = (bandWidthSum * 1 * bwd_unit_cost) + (crbSum * 1 *
                                                    crb_unit_cost)
    vne_node.append(int(revenue))
    vne_revenue_list.append(vne_node)
  return vne_revenue_list


def sort_vne_revenue(vne_list, original_vne_list):# Assending order
  vne_crb_bd_list = []
  index = 0
  for _vne in vne_list:
    vne_node_attrib = NetworkAttribute(_vne, virtual=True)
    node_norm_bw = vne_node_attrib.normalized_node_bandwidth(original_vne_list[index])
    node_norm_crb = vne_node_attrib.normalized_crb(original_vne_list[index])
    node_bw = vne_node_attrib.get_network_bandwidth()
    node_crb = vne_node_attrib.get_network_crb()
    link_bw = vne_node_attrib.get_link_bandwidth()
    node_degree = vne_node_attrib.normalized_node_degree()
    vne_crb_bd_list.append([_vne, node_bw, node_crb, node_norm_bw,
                            node_norm_crb, link_bw, node_degree])
    index += 1
  
  vne_rv = calculate_revenue(vne_crb_bd_list)
  for i in range(len(vne_rv)):
    for j in range(len(vne_rv) - 1):
      if (vne_rv[j][-1] > vne_rv[j + 1][-1]):
        temp = vne_rv[j]
        vne_rv[j] = vne_rv[j + 1]
        vne_rv[j + 1] = temp
  return vne_rv

# checking for preferences of each other
def is_node_belongs_to(vn_node, sn_pref_list, vne_pref_list):
  exp_sn_node = vne_pref_list[vn_node]['node_list'][0]
  exp_vn_node = sn_pref_list[exp_sn_node]['node_list'][0]
  return True if vn_node == exp_vn_node else False

# checking for the quota(by CRB) of SN before placing
def check_quota_available(sn, vn, sn_crb, vn_crb):
  return True if vn_crb[vn] <= sn_crb[sn] else False

# Find all possible paths for Source to destination
def find_all_paths(network, start, end, path=[]):
  path = path + [start]
  if start == end:
    return [path]
  paths = []
  for node in network[start]:
    if node not in path:
      newpaths = find_all_paths(network, node, end, path)
      for newpath in newpaths:
        paths.append(newpath)
  return paths


def map_virtual_link_on_substrate(paths, vne_bw, sn_link_bw):
  paths.sort(key=len)
  link_nodes = []
  for _path in paths:
    node_path = generate_link_paths(_path)
    for link in node_path:
      if vne_bw <= sn_link_bw[link]:
        link_nodes.append(link)
        sn_link_bw[link] -= vne_bw #
        sn_link_bw[link[::-1]] -= vne_bw #
    if link_nodes and (len(link_nodes) == len(node_path)):
      return OrderedDict(link_nodes), sn_link_bw
  return {}, sn_link_bw

# To get path from Source to destination
def generate_link_paths(path_list):
  node_path = []
  prev_n = path_list[0]
  for i in range(len(path_list) - 1):
    next_n = path_list[i + 1]
    node_path.append((prev_n, next_n))
    prev_n = next_n
  return node_path

def generate_paths(request):
  edgesToBeMapped = set()
  for i in request:
    for j in request[i]:
      if ((i, j) in edgesToBeMapped or (j, i) in edgesToBeMapped):
        continue
      edgesToBeMapped.add((i, j))
  return edgesToBeMapped

def BFS(vnr, src, dest, v, pred, dist, weight):
    queue = []
    visited = [False for i in range(v)]
    for i in range(v):
        dist[i] = 1000000
        pred[i] = -1
    visited[int(src)] = True
    dist[int(src)] = 0
    queue.append(src)
    while len(queue) != 0:
        u = queue[0]
        queue.pop(0)
        for i in vnr[int(u)]:
            if visited[int(i)] == False :
                visited[int(i)] = True
                dist[int(i)] = dist[int(u)] + 1
                pred[int(i)] = u
                queue.append(i)
                if int(i) == int(dest):
                    return True

    return False

def findShortestPath(vnr, s, dest, weight):
    v = len(vnr.keys())
    pred = [0 for i in range(v)]
    dist = [0 for i in range(v)]
    ls = []
    if BFS(vnr, s, dest, v, pred, dist, weight) == False:
        return ls
    path = []
    crawl = dest
    crawl = dest
    path.append(crawl)

    while pred[int(crawl)] != -1:
        path.append(pred[int(crawl)])
        crawl = pred[int(crawl)]

    for i in range(len(path) - 1, -1, -1):
        ls.append(path[i])

    return ls

def substract_sn(before_sn, after_sn):
  bw_diff = 0
  for edge in before_sn.keys():
    bw_diff += before_sn[edge] - after_sn[edge]
  # print(bw_diff//2)
  return bw_diff//2

def find_utilized_resources(original_sn_crb, original_sn_bw, sn_crb, sn_link_bw):
  utilized_nodes_cnt=0
  utilized_links_cnt = 0
  node_cost = 0
  edge_cost = 0
  pre_edge_cost = 0
  post_edge_cost = 0
  pre_node_cost = 0
  post_node_cost = 0
  for node in original_sn_crb.keys():
    if(original_sn_crb[node] != sn_crb[node]):
      utilized_nodes_cnt += 1
      node_cost += original_sn_crb[node] - sn_crb[node]
    pre_node_cost += original_sn_crb[node]
    post_node_cost += sn_crb[node]

  for edge in original_sn_bw.keys():
    if(original_sn_bw[edge] != sn_link_bw[edge]):
      utilized_links_cnt += 1
      edge_cost += original_sn_bw[edge]-sn_link_bw[edge]
    pre_edge_cost += original_sn_bw[edge]
    post_edge_cost += sn_link_bw[edge]
  return utilized_nodes_cnt, utilized_links_cnt, node_cost, edge_cost, pre_edge_cost, post_edge_cost, pre_node_cost, post_node_cost

def findAvgPathLength(vnr):
    cnt=0
    for node1 in vnr.keys():
        for node2 in vnr.keys():
            if(node1 != node2):
                path = findShortestPath(vnr, str(node1), str(node2), 0)
                cnt += len(path)-1
    total_nodes = len(vnr.keys())
    cnt /= (total_nodes)*(total_nodes-1)
    return cnt
  
def link_mapping(sn_request, sn_link_bandwidth,
                 vn_request, vne_link_bandwidth, node_map_dict):
  tmp_sn_link_bandwidth = copy.deepcopy(sn_link_bandwidth)
  vne_emb_path = generate_paths(vn_request)
  found = 0
  for vn_nodes in vne_emb_path:
    start_node = node_map_dict[vn_nodes[0]]
    end_node = node_map_dict[vn_nodes[1]]
    req_link_bandwidth = vne_link_bandwidth[vn_nodes]
    all_shortest_paths = find_all_paths(sn_request, start_node, end_node,
                                        path=[])
    shortest_paths, sn_bandw = map_virtual_link_on_substrate(all_shortest_paths,
                                            req_link_bandwidth,sn_link_bandwidth)
    sn_link_bandwidth = sn_bandw
    # log.info('\nVirtual node #{0} is mapped to Substrate node #{1}'.format(vn_nodes[0],start_node))
    # log.info("link between virtual node #{0} #{1}".format(vn_nodes[0], start_node))
    # log.info("the actual link Connection between substrate node #{0} #{1}".format(start_node, end_node))
    if shortest_paths:
      ky = list(shortest_paths.keys())
      while ky:
        start_n = ky[0]
        log.info("#{0} <-- #{1}".format(shortest_paths[start_n], start_n))
        ky.remove(start_n)
      found += 1
    else:
      log.info( "No shortest path found between substrate node #{0} #{1}".format(start_node, end_node))
      log.info( "Link mapping failed for nodes #{0} #{1}".format(start_node,end_node))
  if found == len(vne_emb_path):
    return True, sn_link_bandwidth
  else:
    return False, tmp_sn_link_bandwidth


def node_link_mapping(sn, vneRequests, original_substrate, original_vne_list):
  log.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
  log.info(f"\t\tTotal number of nodes and edges in substrate network is : {original_substrate.nodes} and {len(original_substrate.edges)} ")
  temp = []
  for node in range(original_substrate.nodes):
      temp.append((node, original_substrate.node_weights[node]))
  log.info(f"\t\tNodes of the substrate network with weight are : {temp}")
  temp = []
  for edge in original_substrate.edges:
      temp.append((edge,original_substrate.edge_weights[edge]))
  log.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n")
 

  start_time = datetime.now().time()
  # sn_btw_cnt = BetweennessCentrality(sn).betweenness_centrality()
  # sn_eigned_vct = EigenvectorCentrality(sn).eigenvector_centrality()
  sn_btw_cnt = nx.betweenness_centrality(nx.DiGraph(sn))      #ADDED - inbuilt function for betweeness centrality
  sn_eigned_vct = nx.eigenvector_centrality(nx.DiGraph(sn))   #ADDED - inbuilt function for eigenvector centrality
  sorted_vne_req = sort_vne_revenue(vneRequests, original_vne_list)
  count = 0
  revenue = 0
  total_cost = 0
  average_path_length = 0
  sn_crb = {}
  sn_link_bw = {}
  unmapped_request = []
  mapped_request = []
  while count != len(sorted_vne_req):
    log.info("\n\n")
    log.info("-" * 30)
    log.info("length of request: %s" % len(sorted_vne_req))
    log.info("Request number is %s" % count)

    _node_obj = NetworkAttribute(sn, crb=sn_crb, link_bandwidth=sn_link_bw)
    sn_node_bw = _node_obj.normalized_node_bandwidth(original_substrate)
    sn_node_crb = _node_obj.normalized_crb(original_substrate)
    sn_crb = _node_obj.get_network_crb()
    sn_link_bw = _node_obj.get_link_bandwidth()
    if (count==0):
      original_sn_crb = copy.deepcopy(sn_crb)
      original_sn_bw = copy.deepcopy(sn_link_bw)
    sn_node_degree=_node_obj.normalized_node_degree()
    print(f'\n\nComputing Substrate Resources for VNR {count}\n')
    log.info(f'Computing Substrate Resources for VNR {count}')
    sn_rank = WeightMatrix(sn, sn_node_crb, sn_node_bw, sn_btw_cnt,
                             sn_eigned_vct,sn_node_degree).compute_entropy_measure_matrix()
    sorted_node_dict = sort_node_rank(sn_rank)
    iteration_count = len(sn_rank) * 2
    _vnode = sorted_vne_req[count]
    node_mapping_list = []
    vne_crb = _vnode[2]
    vne_bwdth = _vnode[5]
    vne_req = _vnode[0]
    vne_degree=_vnode[6]
    log.info(f'\tnodes with weights {vne_crb}')
    log.info(f'\tedges with weights {vne_bwdth}')
    # btw_cnt = BetweennessCentrality(_vnode[0]).betweenness_centrality()
    # eigned_vct = EigenvectorCentrality(_vnode[0]).eigenvector_centrality()
    btw_cnt = nx.betweenness_centrality(nx.DiGraph(_vnode[0]))
    eigned_vct = nx.eigenvector_centrality(nx.DiGraph(_vnode[0]))

    print(f"\n\nComputing for VNR {count}\n")
    log.info(f"Computing for VNR {count}")
    node_rank = WeightMatrix(_vnode[0], _vnode[4], _vnode[3], btw_cnt,
                             eigned_vct, vne_degree).compute_entropy_measure_matrix() # Compute Weight of the attributes
    sorted_vnode_dict = sort_node_rank(node_rank)
    vne_nodes = list(sorted_vnode_dict.keys())
    rejection_set = vne_nodes[::]

    preffered_ranking_sn = {ky: {'node_list': list(sorted_vnode_dict.keys()),
                                 'node_crb': sn_crb[ky]} for ky in sn_rank}
    preffered_ranking_vne = {ky: {'node_list': list(sorted_node_dict.keys()),
                                  'node_crb': vne_crb[ky]} for ky in
                             _vnode[0]}

    tmp_vne_crb = copy.deepcopy(vne_crb)
    tmp_sn_crb = copy.deepcopy(sn_crb)
    idx_dict = {i:0 for i in rejection_set}
    node_map_dict = {}
    rejection_iteration = 0
    #log.info() # EAA for ampping
    while len(rejection_set) != 0:
      if rejection_iteration >= iteration_count:
        log.info ("Failed to map request %s" %_vnode)
        unmapped_request.append(_vnode)
        for node_map in node_mapping_list:
          # log.info("preffered_ranking_vne %s ", repr(preffered_ranking_vne))
          # log.info("preffered_ranking_sn %s ", repr(preffered_ranking_sn))
          sn_n, vn_n = node_map
          sn_crb[sn_n] += tmp_vne_crb[vn_n]
        break
      ask_list_vne = {bs: deque(preffered_ranking_vne[bs]['node_list']) for
                      bs in preffered_ranking_vne}

      for vn_node in rejection_set:
        sn_node = ask_list_vne[vn_node][idx_dict[vn_node]]
        if is_node_belongs_to(
            vn_node, preffered_ranking_sn, preffered_ranking_vne) and \
            check_quota_available(sn_node, vn_node, sn_crb, vne_crb):
          node_mapping_list.append((sn_node, vn_node))
          # log.info ('VN node %s mapped on SN node %s' %(vn_node,sn_node))
          sn_crb[sn_node] = sn_crb[sn_node] - vne_crb[vn_node]
          # if sn_crb[sn_node] == 0sn_crb:
          # log.info("sn_crb is after node mapping %s" %repr(sn_crb))
          node_map_dict[vn_node] = sn_node
          preffered_ranking_sn.pop(sn_node)
          _ = {preffered_ranking_vne[bs]['node_list'].remove(sn_node) for bs in \
              preffered_ranking_vne}
          rejection_set.remove(vn_node)
          _ = {preffered_ranking_sn[bs]['node_list'].remove(vn_node) for bs
               in preffered_ranking_sn}
          idx_dict = {i: 0 for i in rejection_set}
          break
          # log.info 'remove vn node from rejection list and preffered_ranking_sn'
        elif len(preffered_ranking_vne[vn_node]['node_list']) != 0:
            # log.info 'preferred node list of VN %s is not empty' % vn_node
            if idx_dict[vn_node] == (len(preffered_ranking_vne[vn_node][
                                          'node_list'])-1):
              idx_dict[vn_node] = 0
            else: idx_dict[vn_node] += 1
            rejection_iteration += 1
        # else:
        #   ## when node is unapped then fail the node mapping and reset the sn
        #   # crb values
        #   rejection_set.remove(vn_node)
        #   unmapped_list.add(vn_node)
    ## when node mapping failed for any node then do not proceed with link
    # embeeding
    if len(rejection_set) == 0:
      log.info ('call for link embedding')
      log.info (node_mapping_list)
      sn_link_bw_before_mapping = copy.deepcopy(sn_link_bw)
      res, sn_band = link_mapping(sn, sn_link_bw,vne_req, vne_bwdth, node_map_dict)
      if res:
        sn_crb = copy.deepcopy(sn_crb)
        sn_link_bw = copy.deepcopy(sn_band)
        mapped_request.append(_vnode)
        # revenue += sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2
        revenue += sum(vne_crb.values()) + sum(vne_bwdth.values())//2
        # print(revenue)
        total_cost += sum(vne_crb.values())+substract_sn(sn_link_bw_before_mapping,sn_link_bw)
        # print(total_cost)
        average_path_length += findAvgPathLength(sorted_vne_req[count][0]) 
        log.info ("Request %s placed successfully" % repr(_vnode[0]))
      else:
        sn_crb = copy.deepcopy(tmp_sn_crb)
        sn_link_bw = copy.deepcopy(sn_band)
        unmapped_request.append(_vnode)
        log.info ("Request %s failed to placed" % repr(_vnode[0]))
        log.info("+" * 30)
    count += 1

  utilized_node, utilized_links, node_cost, edge_cost, pre_edge_cost, post_edge_cost, pre_node_cost, post_node_cost = find_utilized_resources(original_sn_crb, original_sn_bw, sn_crb, sn_link_bw)  
  average_path_length /= len(mapped_request)
  end_time = datetime.now().time()
  duration = datetime.combine(date.min, end_time)-datetime.combine(date.min, start_time)

  log.info ('\n')
  log.info("+" * 100)
  log.info ("Total request mapped successfully: %s\n\t\tMapped requests: %s" %(len(mapped_request), repr(mapped_request)))
  log.info("\n")
  log.info( "Total request left unmapped: %s\n\t\tUnmapped requests: %s" %(len(unmapped_request), repr(unmapped_request)))
  log.info("\n\n")
  log.info(f"Total revenue is {revenue} and total cost is {total_cost}")
  log.info(f"The revenue to cost ratio is {(revenue/total_cost)*100:.4f}%")
  log.info(f"Total number of request embedded is {len(mapped_request)} out of {len(mapped_request)+len(unmapped_request)}")
  log.info(f"Embedding ratio is {(len(mapped_request)/(len(mapped_request)+len(unmapped_request)))*100:.4f}%")
  log.info(f"Total {utilized_node} nodes are used out of {len(sn_crb)}")
  log.info(f"Total {utilized_links//2} links are utilized out of {len(sn_link_bw)//2}")
  log.info(f"Average node utilization is {(utilized_node/len(sn_crb))*100:.4f}%")
  log.info(f"Average link utilization is {(utilized_links/len(sn_link_bw))*100:.4f}%")
  log.info(f"Available substrate before embedding CRB: {pre_node_cost} BW: {pre_edge_cost}")
  log.info(f"Avilable substrate after embeddin CRB: {post_node_cost} BW: {post_edge_cost}")
  log.info(f"Consumed Substrate CRB: {pre_node_cost-post_node_cost} BW: {pre_edge_cost-post_edge_cost}")
  log.info(f"Average Path length is {average_path_length:.4f}")
  log.info(f"Average BW utilization {(edge_cost/pre_edge_cost)*100:.4f}%")
  log.info(f"Average CRB utilization {(node_cost/pre_node_cost)*100:.4f}%")
  log.info(f"Average execution time {duration/len(mapped_request)} (HH:MM:SS)\n\n\n")
 
  print('\n')
  print("+" * 100)
  print("Total request mapped successfully: %s\n" %(len(mapped_request)))
  print( "Total request left unmapped: %s\n" %(len(unmapped_request)))
  print("\n")
  print(f"Total revenue is {revenue} and total cost is {total_cost}")
  print(f"The revenue to cost ratio is {(revenue/total_cost)*100:.4f}%")
  print(f"Total number of request embedded is {len(mapped_request)} out of {len(mapped_request)+len(unmapped_request)}")
  print(f"Embedding ratio is {(len(mapped_request)/(len(mapped_request)+len(unmapped_request)))*100:.4f}%")
  print(f"Total {utilized_node} nodes are used out of {len(sn_crb)}")
  print(f"Total {utilized_links//2} links are utilized out of {len(sn_link_bw)//2}")
  print(f"Average node utilization is {(utilized_node/len(sn_crb))*100:.4f}%")
  print(f"Average link utilization is {(utilized_links/len(sn_link_bw))*100:.4f}%")
  print(f"Available substrate before embedding CRB: {pre_node_cost} BW: {pre_edge_cost}")
  print(f"Avilable substrate after embeddin CRB: {post_node_cost} BW: {post_edge_cost}")
  print(f"Consumed Substrate CRB: {pre_node_cost-post_node_cost} BW: {pre_edge_cost-post_edge_cost}")
  print(f"Average Path length is {average_path_length:.4f}")
  print(f"Average BW utilization {(edge_cost/pre_edge_cost)*100:.4f}%")
  print(f"Average CRB utilization {(node_cost/pre_node_cost)*100:.4f}%")
  print(f"Average execution time {duration/len(mapped_request)} (HH:MM:SS)\n\n\n")
 

def main():
  # sn = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4, 5, 6], 4: [2, 3, 6, 7], 5: [3, 6], 6: [3, 4, 5, 7], 7: [4, 6]}
  # vne = [{1: [2, 3], 2: [1, 3], 3: [2, 1]}]
  #vne = [{1:[2],2:[1]}]
  sn, vne_obj = helper.read_pickle()
  original_substrate, original_vne_list = copy.deepcopy(sn), copy.deepcopy(vne_obj)
  sn = sn.neighbours
  substrate = {}
  vne_list = []
  vne_graph = {}
  vne = [vne_obj[i].neighbours for i in range(len(vne_obj))]
  for key, value in sn.items():
    substrate[key] = [int(i) for i in value]
  for i in range(len(vne)):
    vne_graph = {}
    for key, value in vne[i].items():
      for j in value:
        if key not in vne_graph:
          vne_graph[key] = [int(j)]
        else:
          vne_graph[key].append(int(j))
      # vne_graph[key] = [int(i) for i in value]
    vne_list.append(vne_graph)

  node_link_mapping(substrate, vne_list, original_substrate, original_vne_list)

  #node_link_mapping(sn, vne)
  # ,{1:[2],2:[1,3],3:[2]},{1:[2],2:[1]},{1:[2,3],2:[1],3:[1]}


if __name__ == '__main__':
  main()