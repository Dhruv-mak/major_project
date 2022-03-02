# direct method

import nodeRankCal
import euclideanDistanceCal
import random
import pageRank
import math
import copy
import logging
log = logging.getLogger(__name__)

# This function will sort the node of network according to their rank
# and returns the list containing the node in ascending order
# each index of list will contain node name ( which is actually the number assigned to the node)
def nodeSort(nodeRank):
    ans = list()
    for i in nodeRank:
        ans.append(i)
    # I am using bubbleSort but will use mergeSort while Optimizing
    for i in range(len(ans)):
        for j in range(len(ans)-1):
            if(nodeRank[ans[j]]['rank']>nodeRank[ans[j+1]]['rank']):
                temp = ans[j]
                ans[j] = ans[j+1]
                ans[j+1] = temp
    return ans

def generateLR(vneRequest):
    lr = dict()
    for i in vneRequest:
        lr[i] = random.randint(3,8)
    return lr

def eucDis(subLoc, vneLoc):
    x1 = subLoc[0]
    x2 = vneLoc[0]
    y1 = subLoc[1]
    y2 = vneLoc[1]
    return math.sqrt((((x1-x2)**2)+((y1-y2)**2)))


# this is a utility function to copy dictionary
# warning do not use nested dictionary in this function
def _copy(CRB):
    ans = dict()
    for i in CRB:
        ans[i] = CRB[i]
    return ans

# this is the utility function for findShortestPath
def minDistance(arr,dist):
    mn = 0
    for i in range(len(arr)):
        if(dist[arr[i]]<dist[arr[mn]]):
            mn = i
    return mn

# this is the utility function for findShortestPath
def remove(arr,temp):
    ans = list()
    for i in range(len(arr)):
        if(i == temp):
            continue
        ans.append(arr[i])
    return ans

# this function will update linkBandWidth
def updateLinkBandWidth(linkBandWidth, parent, reqLinkBandWidth, node1, node2):
    i = node2
    while(parent[i] != -1):
        linkBandWidth[(i,parent[i])] -= reqLinkBandWidth
        linkBandWidth[(parent[i],i)] -= reqLinkBandWidth
        i = parent[i]

def countIntermidateLinks(parent,node1,node2):
    i = node2
    ans = 0
    while(parent[i] != -1):
        ans += 1
        i = parent[i]
    return ans

# this function find the shortest path between two nodes which satisfy the bandwidth constraint
def findShortestPath(node1,node2,graph,linkBandWidth,reqLinkBandWidth,
                     subsRank,nodeLoc,linkEmbedding, maxVneDelay):
    log.info("KK Find shrotest path graph")
    print(node1,node2,graph,linkBandWidth,reqLinkBandWidth,
                     subsRank,nodeLoc,linkEmbedding, maxVneDelay)
    s = set()
    arr = list()
    parent = dict()
    dist = dict()
    for i in graph:
        arr.append(i)
        parent[i] = -1
        dist[i] = float('inf')
    dist[node1] = 0
    linkBandWidthTemp = _copy(linkBandWidth)
    while(arr):
        mn = minDistance(arr,dist)
        temp = arr[mn]
        arr = remove(arr,mn)
        for i in graph[temp]:
            if((dist[temp]+euclideanDistanceCal.getDistanceBetweenTwoNodes(temp,i,nodeLoc)<dist[i]) and (i not in s) and (linkBandWidthTemp[(i,temp)] >= reqLinkBandWidth)):
                dist[i] = dist[temp]+euclideanDistanceCal.getDistanceBetweenTwoNodes(temp,i,nodeLoc)
                parent[i] = temp
    if(parent[node2] != -1):
        if (parent[node2] != -1 and (countIntermidateLinks(parent, node1,
                                                           node2) <=
                                     maxVneDelay or True)):
            # updateLinkBandWidth(linkBandWidth, parent, reqLinkBandWidth, node1,
            #                     node2)
            linkEmbedding.append([parent, node1, node2])
            return True
    return False


def printEmbedding(vneEmbedding):
    '''
        @param : vneEmbedding is the dictionary containing the mapping of each Virtual node to the Substrate node
    '''
    if(vneEmbedding == -1):
        return
    for i in vneEmbedding:
        log.info('Virtual node #{0} is mapped to Substrate node #{1}'.format(i,vneEmbedding[i]))



def printRank(rank):
    '''
        @param : rank is the dictionary returned by calling nodeRankCal.calRank
    '''
    for i in rank:
        log.info('The rank of node #{0} is #{1}'.format(i,rank[i]['rank']))

def printLinkEmbedding(linkEmbedding):
    if(linkEmbedding == -1):
        return
    vne_link_dict = {}
    for i in linkEmbedding:
        log.info("link between virtual node #{0} #{1}".format(i[-2],i[-1]))
        log.info("the actual link Connection between substrate node #{0} #{1}".format(i[-4],i[-3]))
        alink = (i[-2],i[-1])
        node2 = i[-3]
        parent = i[0]
        vne_emb_link = []
        while(parent[node2] != -1):
            log.info("#{0} <-- #{1}".format(parent[node2],node2))
            vne_emb_link.append((parent[node2],node2))
            node2 = parent[node2]
        vne_link_dict[alink] = vne_emb_link
    return vne_link_dict

def calculate_vne_crb(vne_crb, vne_bandwidth, map_dict): # used for cost calculation ###
    cost = 0
    for node in map_dict:
        for v_node in node:
            cost += vne_crb[v_node]
        sub_cost = vne_bandwidth[node]
        cost += sub_cost * len(map_dict[node])
    return cost

def update_sn_crb(node_crb, vne_crb, map_dict):
    try:
        for node in map_dict:
            node_crb[map_dict[node]] -= vne_crb[node]
    except Exception as err:
        print (err)

def update_sn_bandwidth(node_bandwidth, vne_bandwidth, map_dict):

    try:
        for vn_link in map_dict:
            for n_link in map_dict[vn_link]:
                node_bandwidth[n_link] -= vne_bandwidth[vn_link]
                node_bandwidth[n_link[::-1]] -= vne_bandwidth[vn_link]
    except Exception as err:
        print (err)

def rankingMapping(graph, nodeLoc, linkBandWidth, nodeCRB,vneRequest,vneLoc,
                   vneLinkBandWidth, vneCRB, vneLR, vneDelay, page_rank):
    log.info("this is substrate network",graph)
    log.info("this is substrate network location",nodeLoc)
    log.info("this is substrate network linkBandWidth",linkBandWidth)
    log.info("this is substrate network CRB",nodeCRB)
    # subsRank = pageRank.calRank(graph, nodeLoc, linkBandWidth, nodeCRB)
    # log.info("this is substrate network rank")
    # printRank(subsRank)
    log.info("this is vne",vneRequest)
    log.info("this is vne location",vneLoc)
    log.info("this is vne linkBandWidth",vneLinkBandWidth)
    log.info("this is vneCRB",vneCRB)
    log.info("this is vneLR", vneLR)
    log.info("this is vneDelay", vneDelay)
    if page_rank:
        return page_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay)
    else:
        return node_rank_mapping(graph, nodeLoc, linkBandWidth,
                                nodeCRB,vneRequest, vneLoc, vneLinkBandWidth,
                                 vneCRB, vneLR, vneDelay)

def page_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay):
    log.info("\nGoogle PageRank used to calculate Ranking")
    log.info("-" * 30)
    subsRank = pageRank.calRank(graph, nodeLoc, linkBandWidth, nodeCRB, delay=1)
    vneRank = pageRank.calRank(vneRequest, vneLoc, vneLinkBandWidth, vneCRB,
                               delay=vneDelay)
    # printRank(vneRank)
    subsSort = nodeSort(subsRank)
    vneSort = nodeSort(vneRank)
    vneEmbedding = dict()
    for i in vneRequest:
        vneEmbedding[i] = -1
    # log.info("\nthis is substrate(Physical) network rank after Virtual "
    #       "network embedding")
    log.info("\nthis is substrate network rank")
    log.info("-" * 30)
    printRank(subsRank)
    log.info("\nthis is vne Rank")
    log.info("-" * 30)
    printRank(vneRank)
    flag = True
    nodeCRBTemp = _copy(nodeCRB)
    vneCRBTemp = _copy(vneCRB)
    j = len(vneSort) - 1
    # this part will map the nodes
    while (j > -1):
        i = len(subsSort) - 1
        while (True):
            if ((nodeCRBTemp[subsSort[i]] >= vneCRBTemp[vneSort[j]]) and (
                eucDis(nodeLoc[subsSort[i]], vneLoc[vneSort[j]]) <= vneLR[
                vneSort[j]] or True)):
                vneEmbedding[vneSort[j]] = subsSort[i]
                nodeCRBTemp[subsSort[i]] -= vneCRBTemp[vneSort[j]]
                subsSort = remove(subsSort, i)
                break
            i -= 1
            if (i == -1):
                flag = False
                break
        j -= 1
        if ((not flag) or (len(subsSort) == 0 and j > -1)):
            break

    # this part will map the edges
    if (flag):
        edgesToBeMapped = set()
        for i in vneRequest:
            for j in vneRequest[i]:
                if ((i, j) in edgesToBeMapped or (j, i) in edgesToBeMapped):
                    continue
                edgesToBeMapped.add((i, j))
        linkEmbedding = list()
        for i in edgesToBeMapped:
            node1 = vneEmbedding[i[0]]
            node2 = vneEmbedding[i[1]]
            reqLinkBandWidth = vneLinkBandWidth[i]
            if (not findShortestPath(node1, node2, graph, linkBandWidth,
                                     reqLinkBandWidth, subsRank, nodeLoc,
                                     linkEmbedding, vneDelay[i])):
                return [-1, -1]
            linkEmbedding[-1].append(i[0])
            linkEmbedding[-1].append(i[1])
        nodeCRB = nodeCRBTemp
        # i also need to return link embedding
        return [vneEmbedding, linkEmbedding]
    return -1

def node_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay):
    log.info("\nNodeRank used to calculate Ranking")
    log.info("-"*30)
    subsRank = nodeRankCal.calRank(graph, nodeLoc, linkBandWidth, nodeCRB,
                                   delay=1)
    vneRank = nodeRankCal.calRank(vneRequest,vneLoc, vneLinkBandWidth, vneCRB, delay=vneDelay)
    # printRank(vneRank)
    subsSort = nodeSort(subsRank)
    vneSort = nodeSort(vneRank)
    vneEmbedding = dict()
    for i in vneRequest:
        vneEmbedding[i] = -1
    # log.info("\nthis is substrate(Physical) network rank after Virtual "
    #       "network embedding")
    log.info("\nthis is substrate network rank")
    log.info("-" * 30)
    printRank(subsRank)
    log.info("\nthis is vne Rank")
    log.info("-" * 30)
    printRank(vneRank)
    flag = True
    nodeCRBTemp = _copy(nodeCRB)
    vneCRBTemp = _copy(vneCRB)
    j = len(vneSort) - 1
    # this part will map the nodes######################################################################33
    while (j > -1):
        i = len(subsSort) - 1
        while (True):
            if ((nodeCRBTemp[subsSort[i]] >= vneCRBTemp[vneSort[j]]) and (
                eucDis(nodeLoc[subsSort[i]], vneLoc[vneSort[j]]) <= vneLR[
                vneSort[j]] or True)):
                vneEmbedding[vneSort[j]] = subsSort[i]
                nodeCRBTemp[subsSort[i]] -= vneCRBTemp[vneSort[j]]
                subsSort = remove(subsSort, i)
                break
            i -= 1
            if (i == -1):
                flag = False
                break
        j -= 1
        if ((not flag) or (len(subsSort) == 0 and j > -1)):
            break

    # this part will map the edges
    if (flag):
        edgesToBeMapped = set()
        for i in vneRequest:
            for j in vneRequest[i]:
                if ((i, j) in edgesToBeMapped or (j, i) in edgesToBeMapped):
                    continue
                edgesToBeMapped.add((i, j))
        linkEmbedding = list()
        for i in edgesToBeMapped:
            node1 = vneEmbedding[i[0]]
            node2 = vneEmbedding[i[1]]
            reqLinkBandWidth = vneLinkBandWidth[i]
            if (not findShortestPath(node1, node2, graph, linkBandWidth,
                                     reqLinkBandWidth, subsRank, nodeLoc,
                                     linkEmbedding, vneDelay[i])):
                return [-1, -1]
            linkEmbedding[-1].append(i[0])
            linkEmbedding[-1].append(i[1])
        nodeCRB = nodeCRBTemp
        # i also need to return link embedding
        return [vneEmbedding, linkEmbedding]
    return -1

# function to generate node location
def generatenodeLoc(network):
    networkLoc = dict()
    for i in network:
        networkLoc[i] = (random.randint(0,100),random.randint(0,100))
    return networkLoc

#function to generate linkBandWidth
def generatelinkBandWidth(network,flag):
    linkBandWidth = dict()
    for i in network:
        for j in network[i]:
            if((j,i) in linkBandWidth):
                linkBandWidth[(i,j)] = linkBandWidth[(j,i)]
            else:
                if(not flag):
                    linkBandWidth[(i,j)] = random.randint(10000,500000) # for SN
                else:
                    linkBandWidth[(i,j)] = random.randint(1,10) # for VNR
    return linkBandWidth

# function to generate CRB
def generateCRB(network,flag):
    networkCRB = dict()
    for i in network:
        if(not flag):
            networkCRB[i] = random.randint(10000,500000) # for SN
        else:
            networkCRB[i] = random.randint(1,10) # for VNR
    return networkCRB


# this function will calculate the revenue of vne
def calculateRevenue(vneList, crb_unit_cost, bwd_unit_cost):
    for vneContainer in vneList:
        bandWidth = vneContainer[2]
        crb = vneContainer[3]
        bandWidthSum = 0
        crbSum = 0
        for i in crb:
            crbSum += crb[i]
        for i in bandWidth:
            bandWidthSum += bandWidth[i]
        bandWidthSum = bandWidthSum//2
        revenue = (bandWidthSum * 1 * bwd_unit_cost) + (crbSum * 1 *
                                                        crb_unit_cost)   # maintaing constant factor as 1 but as per paper it is 05
        # revenue = (bandWidthSum * 0.5) + crbSum
        vneContainer.append(int(revenue))


# this function will sort the vneList according to revenue in ascending order
def sortAccordingToRevenue(vneList):
    for i in range(len(vneList)):
        for j in range(len(vneList)-1):
            if(vneList[j][-1]>vneList[j+1][-1]):
                temp = vneList[j]
                vneList[j] = vneList[j+1]
                vneList[j+1] = temp

def generateDelay(vneRequest):
    delay = dict()
    for i in vneRequest:
        for j in vneRequest[i]:
            if((j,i) in delay):
                delay[(i,j)] = delay[(j,i)]
            else:
                delay[(i,j)] = random.randint(1,4)
    return delay

def embed_rank_mapping(sn, snLoc, snLinkBandWidth, snCRB, vneList,
                       page_rank=True):
    total_vne_cost = 0
    total_vne_revenue = 0
    total_vne = len(vneList)
    failed_vne = 0
    for vneContainer in vneList:
        vneRequest = vneContainer[0]
        vneLoc = vneContainer[1]
        vnelinkBandWidth = vneContainer[2]
        vneCRB = vneContainer[3]
        vneLR = vneContainer[4]
        vneDelay = vneContainer[5]
        total_vne_revenue += vneContainer[-2]
        log.info("\nEmbedding for virtual network request: %s of revenue: %s$"%
              (vneContainer[ -1], vneContainer[-2]))
        log.info("-" * 60)
        embeding_out = [vneContainer[-1],
                        rankingMapping(sn, snLoc, snLinkBandWidth, snCRB, vneRequest, vneLoc,
                        vnelinkBandWidth, vneCRB, vneLR, vneDelay, page_rank)]
        log.info('\nEmbedding details of vne %s' % embeding_out[0])
        log.info("-" * 30)
        # print snLinkBandWidth
        # print vnelinkBandWidth
        if embeding_out[1][0] == -1:
            failed_vne += 1
            log.info('Error - Embedding is skipped as No shortest path found')
        else:
            printEmbedding(embeding_out[1][0])
            update_sn_crb(snCRB, vneCRB, embeding_out[1][0])

            link_map_dict = printLinkEmbedding(embeding_out[1][1])
            update_sn_bandwidth(snLinkBandWidth, vnelinkBandWidth,
                                link_map_dict)
            _ncost = calculate_vne_crb(vneCRB, vnelinkBandWidth, link_map_dict)
            total_vne_cost += _ncost
            log.info("\ncost incurred for embedding vne %s is %s$" % (vneContainer[
                                                                    -1], _ncost))
            log.info("-" * 30)
    embedding_ratio = (float(total_vne - failed_vne) / float(total_vne)) * 100
    if page_rank:
        log.info("\nSummary (Stble google PageRank):")
    else:
        log.info("\nSummary (Direct Method NodeRank):")
    log.info("-" * 30)
    log.info("\nTotal number of nodes in substrate network - %s nodes" % len(sn))
    log.info('\nTotal number of VNE request - %d request' % total_vne)
    log.info('Total number VNE request successfully embedded - %d' % (total_vne - failed_vne))
    log.info('\nEmbedding ratio is ' + str(int(embedding_ratio)) + '%')
    log.info('\nTotal revenue for all VNEs is %s$' % total_vne_revenue)
    log.info('\nTotal cost incurred for embedding all VNE requests is %s$' % str(
        total_vne_cost))
    log.info("#"*30)


def generateReqDelay(requests):
    for request in requests:
        delay = dict()
        for i in request:
            for j in request[i]:
                if((j,i) in delay):
                    delay[(i,j)] = delay[(j,i)]
                else:
                    delay[(i,j)] = random.randint(1,4)
        return delay

# This is the main function to be called to get the embedding
def calling(sn, vneRequests):
    '''
        @param : sn -> this is the substrate graph {must be in the from of dictionary}
        @param : vneRequests -> this is the list of vneRequest where each vneRequest is the vne graph {must be in the form of dictionary}
    '''
    cost_per_unit_crb = 1
    cost_per_unit_bandwidth = 1
    log.info("this is all the inputs and their values\n")
    snLoc = generatenodeLoc(sn)
    snLinkBandWidth = generatelinkBandWidth(sn,False)
    snCRB = generateCRB(sn,False)

    # snLinkBandWidth = {(1,2):5,(2,1):5,(2,5):6,(5,2):6,(5,4):10,(4,5):10,(4,3):4,(3,4):4,(1,3):4,(3,1):4,(3,5):10,(5,3):10}
    # snCRB = {1:5,2:5,3:15,4:16,5:15}
    vneEmbeddings = list()
    vneList = list()
    for vneRequest in vneRequests:
        vneLoc = generatenodeLoc(vneRequest)
        vnelinkBandWidth = generatelinkBandWidth(vneRequest,True)
        vneCRB = generateCRB(vneRequest,True)
        # vnelinkBandWidth = {(1,2):10,(2,1):10}
        # vneCRB = {1:15,2:16}
        vneLR = generateLR(vneRequest)
        vneDelay = generateDelay(vneRequest)
        vneList.append([vneRequest,vneLoc,vnelinkBandWidth,vneCRB,vneLR,vneDelay])
    calculateRevenue(vneList, cost_per_unit_crb, cost_per_unit_bandwidth)
    for i in range(len(vneList)):
        vneList[i].append(i)
    sortAccordingToRevenue(vneList)
    _sn = copy.deepcopy(sn)
    _snLoc = copy.deepcopy(snLoc)
    _snLinkBandWidth = copy.deepcopy(snLinkBandWidth)
    _snCRB = copy.deepcopy(snCRB)
    _vneList = copy.deepcopy(vneList)
    embed_rank_mapping(sn, snLoc, snLinkBandWidth, snCRB, vneList,
                       page_rank=True)
    embed_rank_mapping(_sn, _snLoc, _snLinkBandWidth, _snCRB, _vneList,
                       page_rank=False)


def generate_sn_rank(sn):
    snLoc = generatenodeLoc(sn)
    snLinkBandWidth = generatelinkBandWidth(sn, False)
    snCRB = generateCRB(sn, False)



def embedded_map(sn, vneRequests):
    log.info("this is all the inputs and their values\n")


if __name__=="__main__":
    # sn = {1:[2,3],2:[1,5],3:[1,4,5],4:[3,5],5:[2,3,4]}
    # vne = [{1:[2], 2:[1]}]
    sn = {2: [4, 1], 4: [2, 1, 5], 5: [4, 3], 3: [5, 1], 1: [2, 3, 4]}
    vne = [{1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3], 3: [1, 2], 2: [1, 3]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]}
           ,{1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]}]

    temp = calling(sn,vne)
    # log.info("Here is all the embedding if found any")
    # for i in temp:
    #     log.info('embedding for vne',i[0])
    #     if(i[1] == -1):
    #         log.info("No embedding found")
    #         continue
    #     printEmbedding(i[1][0])
    #     printLinkEmbedding(i[1][1])



















