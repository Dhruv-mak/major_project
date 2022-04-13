
import copy
from collections import OrderedDict, deque
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


def sort_vne_revenue(vne_list):# Assending order
  vne_crb_bd_list = []
  for _vne in vne_list:
    vne_node_attrib = NetworkAttribute(_vne, virtual=True)
    node_norm_bw = vne_node_attrib.normalized_node_bandwidth()
    node_norm_crb = vne_node_attrib.normalized_crb()
    node_bw = vne_node_attrib.get_network_bandwidth()
    node_crb = vne_node_attrib.get_network_crb()
    link_bw = vne_node_attrib.get_link_bandwidth()
    node_degree = vne_node_attrib.normalized_node_degree()
    vne_crb_bd_list.append([_vne, node_bw, node_crb, node_norm_bw,
                            node_norm_crb, link_bw, node_degree])
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


def node_link_mapping(sn, vneRequests):
  # sn_btw_cnt = BetweennessCentrality(sn).betweenness_centrality()
  # sn_eigned_vct = EigenvectorCentrality(sn).eigenvector_centrality()
  sn_btw_cnt = nx.betweenness_centrality(nx.DiGraph(sn))      #ADDED - inbuilt function for betweeness centrality
  sn_eigned_vct = nx.eigenvector_centrality(nx.DiGraph(sn))   #ADDED - inbuilt function for eigenvector centrality
  sorted_vne_req = sort_vne_revenue(vneRequests)
  count = 0
  sn_crb = {}
  sn_link_bw = {}
  unmapped_request = []
  mapped_request = []
  while count != len(sorted_vne_req):
    log.info("\n\n")
    log.info("-" * 30)
    log.info( "length of request: %s" % len(sorted_vne_req))
    log.info("Request number is %s" % count)

    _node_obj = NetworkAttribute(sn, crb=sn_crb, link_bandwidth=sn_link_bw)
    sn_node_bw = _node_obj.normalized_node_bandwidth()
    sn_node_crb = _node_obj.normalized_crb()
    sn_crb = _node_obj.get_network_crb()
    sn_link_bw = _node_obj.get_link_bandwidth()
    sn_node_degree=_node_obj.normalized_node_degree()
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
    # btw_cnt = BetweennessCentrality(_vnode[0]).betweenness_centrality()
    # eigned_vct = EigenvectorCentrality(_vnode[0]).eigenvector_centrality()
    btw_cnt = nx.betweenness_centrality(nx.DiGraph(_vnode[0]))
    eigned_vct = nx.eigenvector_centrality(nx.DiGraph(_vnode[0]))

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
      res, sn_band = link_mapping(sn, sn_link_bw,vne_req, vne_bwdth, node_map_dict)
      if res:
        sn_crb = copy.deepcopy(sn_crb)
        sn_link_bw = copy.deepcopy(sn_band)
        mapped_request.append(_vnode)
        log.info ("Request %s placed successfully" % repr(_vnode[0]))
      else:
        sn_crb = copy.deepcopy(tmp_sn_crb)
        sn_link_bw = copy.deepcopy(sn_band)
        unmapped_request.append(_vnode)
        log.info ("Request %s failed to placed" % repr(_vnode[0]))
        log.info("+" * 30)
    count += 1
  log.info ('\n')
  log.info("+" * 30)
  log.info ("Total request mapped successfully: %s\n\t\tMapped requests: %s" %(len(mapped_request), repr(mapped_request)))
  log.info("\n")
  log.info( "Total request left unmapped: %s\n\t\tUnmapped requests: %s" %(len(unmapped_request), repr(unmapped_request)))


# sn = {1: [2, 3], 2: [1, 3, 4], 3: [1, 2, 4, 5, 6], 4: [2, 3, 6, 7], 5: [3, 6], 6: [3, 4, 5, 7], 7: [4, 6]}
# vne = [{1: [2, 3], 2: [1, 3], 3: [2, 1]}]
 #vne = [{1:[2],2:[1]}]
f = open("input.pickle", "rb")
sn, vne_obj = helper.read_pickle()
orginal_substrate, original_vne_list = copy.deepcopy(sn), copy.deepcopy(vne_obj)
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

node_link_mapping(substrate, vne_list)

#node_link_mapping(sn, vne)
# ,{1:[2],2:[1,3],3:[2]},{1:[2],2:[1]},{1:[2,3],2:[1],3:[1]}