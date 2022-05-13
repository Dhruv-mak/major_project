import copy
import os
from time import sleep
import pandas as pd
from vikor import main as vikor
from greedy import main as greedy
from parser import main as parser
from vrmap import main as vrmap
from rethinking import main as rethinking
from topsis import main as topsis
from node_link_mapping import main as EAA
from vne import create_vne as vne
from vne_u import create_vne as vne_u
from vne_p import create_vne as vne_p
from vne_n import create_vne as vne_n
import graph_extraction
import graph_extraction_uniform
import graph_extraction_poisson
import graph_extraction_normal
import logging
import config
import pickle

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    # formatter = logging.Formatter('%(asctime)s %(levelname)s  : %(message)s')
    formatter = logging.Formatter('[%(levelname)s] : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler) 

output_dict = {
        "algorithm": [],
        "revenue": [],
        "total_cost" : [],
        "revenuetocostratio":[],
        "accepted" : [],
        "total_request": [],
        "embeddingratio":[],
        "pre_resource": [],
        "post_resource": [],
        "consumed":[],
        "avg_bw": [],
        "avg_crb": [],
        "avg_link": [],
        "avg_node": [],
        "avg_path": [],
        "avg_exec": [],
        "total_nodes": [],
        "total_links": [],
    }

def exec_algorithm(algorithm_name, algorithm, tot=1):
    sleep(tot)
    
    printToExcel(
        algorithm=algorithm_name,
        revenue=algorithm['revenue'],
        total_cost=algorithm['total_cost'],
        revenuetocostratio=(algorithm['revenue']/algorithm['total_cost'])*100,
        accepted=algorithm['accepted'],
        total_request=algorithm['total_request'],
        embeddingratio=(algorithm['accepted']/algorithm['total_request'])*100,
        pre_resource=algorithm['pre_resource'],
        post_resource=algorithm['post_resource'],
        consumed=algorithm['pre_resource']-algorithm['post_resource'],
        avg_bw=algorithm['avg_bw'],
        avg_crb=algorithm['avg_crb'],
        avg_link=algorithm['avg_link'],
        avg_node=algorithm['avg_node'],
        avg_path=algorithm['avg_path'],
        avg_exec=algorithm['avg_exec'].total_seconds()*1000/algorithm['total_request'],
        total_nodes=algorithm['total_nodes'],
        total_links=algorithm['total_links']
    )


def exec_greedy(tot=1):
    gred_out = greedy()
    sleep(tot*1)
    
    printToExcel(
        algorithm='GREEDY',
        revenue=gred_out['revenue'],
        total_cost=gred_out['total_cost'],
        revenuetocostratio=(gred_out['revenue']/gred_out['total_cost'])*100,
        accepted=gred_out['accepted'],
        total_request=gred_out['total_request'],
        embeddingratio=(gred_out['accepted']/gred_out['total_request'])*100,
        pre_resource=gred_out['pre_resource'],
        post_resource=gred_out['post_resource'],
        consumed=gred_out['pre_resource']-gred_out['post_resource'],
        avg_bw=gred_out['avg_bw'],
        avg_crb=gred_out['avg_crb'],
        avg_link=gred_out['avg_link'],
        avg_node=gred_out['avg_node'],
        avg_path=gred_out['avg_path'],
        avg_exec=gred_out['avg_exec'].total_seconds()*1000/gred_out['total_request'],
        total_nodes=gred_out['total_nodes'],
        total_links=gred_out['total_links']
    )


def exec_vikor(tot=1):
    vikor_out = vikor()
    sleep(tot*1)
    printToExcel(
        algorithm='VIKOR',
        revenue=vikor_out['revenue'],
        total_cost=vikor_out['total_cost'],
        revenuetocostratio=(vikor_out['revenue']/vikor_out['total_cost'])*100,
        accepted=vikor_out['accepted'],
        total_request=vikor_out['total_request'],
        embeddingratio=(vikor_out['accepted']/vikor_out['total_request'])*100,
        pre_resource=vikor_out['pre_resource'],
        post_resource=vikor_out['post_resource'],
        consumed=vikor_out['pre_resource']-vikor_out['post_resource'],
        avg_bw=vikor_out['avg_bw'],
        avg_crb=vikor_out['avg_crb'],
        avg_link=vikor_out['avg_link'],
        avg_node=vikor_out['avg_node'],
        avg_path=vikor_out['avg_path'],
        avg_exec=vikor_out['avg_exec'].total_seconds()*1000/vikor_out['total_request'],
        total_nodes=vikor_out['total_nodes'],
        total_links=vikor_out['total_links']
    )


def exec_topsis(tot=1):
    topsis_out = topsis()
    sleep(tot*1)
    
    printToExcel(
        algorithm='TOPSIS',
        revenue=topsis_out['revenue'],
        total_cost=topsis_out['total_cost'],
        revenuetocostratio=(topsis_out['revenue']/topsis_out['total_cost'])*100,
        accepted=topsis_out['accepted'],
        total_request=topsis_out['total_request'],
        embeddingratio=(topsis_out['accepted']/topsis_out['total_request'])*100,
        pre_resource=topsis_out['pre_resource'],
        post_resource=topsis_out['post_resource'],
        consumed=topsis_out['pre_resource']-topsis_out['post_resource'],
        avg_bw=topsis_out['avg_bw'],
        avg_crb=topsis_out['avg_crb'],
        avg_link=topsis_out['avg_link'],
        avg_node=topsis_out['avg_node'],
        avg_path=topsis_out['avg_path'],
        avg_exec=topsis_out['avg_exec'].total_seconds()*1000/topsis_out['total_request'],
        total_nodes=topsis_out['total_nodes'],
        total_links=topsis_out['total_links']
    )

def exec_EAA(tot=1):
    gred_out = EAA()
    sleep(tot*1)
    
    printToExcel(
        algorithm='EAA',
        revenue=gred_out['revenue'],
        total_cost=gred_out['total_cost'],
        revenuetocostratio=(gred_out['revenue']/gred_out['total_cost'])*100,
        accepted=gred_out['accepted'],
        total_request=gred_out['total_request'],
        embeddingratio=(gred_out['accepted']/gred_out['total_request'])*100,
        pre_resource=gred_out['pre_resource'],
        post_resource=gred_out['post_resource'],
        consumed=gred_out['pre_resource']-gred_out['post_resource'],
        avg_bw=gred_out['avg_bw'],
        avg_crb=gred_out['avg_crb'],
        avg_link=gred_out['avg_link'],
        avg_node=gred_out['avg_node'],
        avg_path=gred_out['avg_path'],
        avg_exec=gred_out['avg_exec'].total_seconds()*1000/gred_out['total_request'],
        total_nodes=gred_out['total_nodes'],
        total_links=gred_out['total_links']
    )
    

def exec_parser(tot=2):
    parser_out = parser()
    sleep(tot*2)
    
    printToExcel(
        algorithm='PAGERANK-STABLE',
        revenue=parser_out[0]['revenue'],
        total_cost=parser_out[0]['total_cost'],
        revenuetocostratio=(parser_out[0]['revenue']/parser_out[0]['total_cost'])*100,
        accepted=parser_out[0]['accepted'],
        total_request=parser_out[0]['total_request'],
        embeddingratio=(parser_out[0]['accepted']/parser_out[0]['total_request'])*100,
        pre_resource=parser_out[0]['pre_resource'],
        post_resource=parser_out[0]['post_resource'],
        consumed=parser_out[0]['pre_resource']-parser_out[0]['post_resource'],
        avg_bw=parser_out[0]['avg_bw'],
        avg_crb=parser_out[0]['avg_crb'],
        avg_link=parser_out[0]['avg_link'],
        avg_node=parser_out[0]['avg_node'],
        avg_path=parser_out[0]['avg_path'],
        avg_exec=parser_out[0]['avg_exec'].total_seconds()*1000/parser_out[0]['total_request'],
        total_nodes=parser_out[0]['total_nodes'],
        total_links=parser_out[0]['total_links']
    )
    
    printToExcel(
        algorithm='PAGERANK-DIRECT',
        revenue=parser_out[1]['revenue'],
        total_cost=parser_out[1]['total_cost'],
        revenuetocostratio=(parser_out[1]['revenue']/parser_out[1]['total_cost'])*100,
        accepted=parser_out[1]['accepted'],
        total_request=parser_out[1]['total_request'],
        embeddingratio=(parser_out[1]['accepted']/parser_out[1]['total_request'])*100,
        pre_resource=parser_out[1]['pre_resource'],
        post_resource=parser_out[1]['post_resource'],
        consumed=parser_out[1]['pre_resource']-parser_out[1]['post_resource'],
        avg_bw=parser_out[1]['avg_bw'],
        avg_crb=parser_out[1]['avg_crb'],
        avg_link=parser_out[1]['avg_link'],
        avg_node=parser_out[1]['avg_node'],
        avg_path=parser_out[1]['avg_path'],
        avg_exec=parser_out[1]['avg_exec'].total_seconds()*1000/parser_out[1]['total_request'],
        total_nodes=parser_out[1]['total_nodes'],
        total_links=parser_out[1]['total_links']
    )


def exec_vrmap(tot=7):
    vrmap_out = vrmap()
    sleep(tot*5)
    printToExcel(
        algorithm='VRMAP',
        revenue=vrmap_out['revenue'],
        total_cost=vrmap_out['total_cost'],
        revenuetocostratio=(vrmap_out['revenue']/vrmap_out['total_cost'])*100,
        accepted=vrmap_out['accepted'],
        total_request=vrmap_out['total_request'],
        embeddingratio=(vrmap_out['accepted']/vrmap_out['total_request'])*100,
        pre_resource=vrmap_out['pre_resource'],
        post_resource=vrmap_out['post_resource'],
        consumed=vrmap_out['pre_resource']-vrmap_out['post_resource'],
        avg_bw=vrmap_out['avg_bw'],
        avg_crb=vrmap_out['avg_crb'],
        avg_link=vrmap_out['avg_link'],
        avg_node=vrmap_out['avg_node'],
        avg_path=vrmap_out['avg_path'],
        avg_exec=vrmap_out['avg_exec'].total_seconds()*1000/vrmap_out['total_request'],
        total_nodes=vrmap_out['total_nodes'],
        total_links=vrmap_out['total_links']
    )


def exec_rethinking(tot=15):
    rethinking_out = rethinking()
    sleep(tot*4)

    printToExcel(
        algorithm='RETHINKING',
        revenue=rethinking_out['revenue'],
        total_cost=rethinking_out['total_cost'],
        revenuetocostratio=(rethinking_out['revenue']/rethinking_out['total_cost'])*100,
        accepted=rethinking_out['accepted'],
        total_request=rethinking_out['total_request'],
        embeddingratio=(rethinking_out['accepted']/rethinking_out['total_request'])*100,
        pre_resource=rethinking_out['pre_resource'],
        post_resource=rethinking_out['post_resource'],
        consumed=rethinking_out['pre_resource']-rethinking_out['post_resource'],
        avg_bw=rethinking_out['avg_bw'],
        avg_crb=rethinking_out['avg_crb'],
        avg_link=rethinking_out['avg_link'],
        avg_node=rethinking_out['avg_node'],
        avg_path=rethinking_out['avg_path'],
        avg_exec=rethinking_out['avg_exec'].total_seconds()*1000/rethinking_out['total_request'],
        total_nodes=rethinking_out['total_nodes'],
        total_links=rethinking_out['total_links']
    )


def printToExcel(algorithm='', revenue='', total_cost='', revenuetocostratio='', accepted='', total_request='', 
embeddingratio='', pre_resource='', post_resource='',consumed='',avg_bw='',avg_crb='',avg_link='',
avg_node='',avg_path='',avg_exec='', total_nodes='', total_links=''):

    output_dict["algorithm"].append(algorithm)
    output_dict["revenue"].append(revenue)
    output_dict["total_cost"].append(total_cost)
    output_dict["revenuetocostratio"].append(revenuetocostratio)
    output_dict["accepted"].append(accepted)
    output_dict["total_request"].append(total_request)
    output_dict["embeddingratio"].append(embeddingratio)
    output_dict["pre_resource"].append(pre_resource)
    output_dict["post_resource"].append(post_resource)
    output_dict["consumed"].append(consumed)
    output_dict["avg_bw"].append(avg_bw)
    output_dict["avg_crb"].append(avg_crb)
    output_dict["avg_link"].append(avg_link)
    output_dict["avg_node"].append(avg_node)
    output_dict["avg_path"].append(avg_path)
    output_dict["avg_exec"].append(avg_exec)
    output_dict["total_nodes"].append(total_nodes)
    output_dict["total_links"].append(total_links)

    addToExcel()

def addToExcel():
    geeky_file = open('geekyfile.pickle', 'wb')
    pickle.dump(output_dict, geeky_file)
    geeky_file.close()

def main(substrate, vne):
    tot=0
    ls = [3]
    for req_no in ls:
        tot += 1
        print(f"\n\treq_no: {req_no}\n")
        # setup_logger('log1','vikor.log')
        # setup_logger('log2','greedy.log')
        # try:
        #     iteration = int(input("Enter how many times to repeat (int only) : "))
        # except:
        #     iteration = 1
        iteration = 3
        iteration = max(iteration, 1)
        cnt=0
        while cnt<iteration:
            vne_list = vne(no_requests=req_no)
            config.substrate = copy.deepcopy(substrate)
            config.vne_list = copy.deepcopy(vne_list)

            # Uncomment those functions which to run, comment all other. for ex if want to run greedy algorithm only leave
            # exec_greedy() uncommented and comment all other (exec_vikor(), exec_topsis(), exec_parser(), exec_vrmap(), exec_rethinking())
            
            exec_algorithm('GREEDY', greedy(), tot*1)        #Runs GREEDY algorithm
            exec_algorithm('VIKOR', vikor(), tot*1)         #Runs VIKOR algorithm
            exec_algorithm('TOPSIS', topsis(), tot*1)        #Runs TOPSIS algorithm
            exec_algorithm('EAA', EAA(), tot*1)           #Runs EAA algorithm
            parser_out = parser()
            exec_algorithm('PAGERANK-STABLE', parser_out[0], tot*2)        #Runs PARSER-STABLE algorithm
            exec_algorithm('PAGERANK-DIRECT', parser_out[1], tot*2)        #Runs PARSER-DIRECT algorithm
            exec_algorithm('VRMAP', vrmap(), tot*5)         #Runs VRMAP algorithm
            exec_algorithm('RETHINKING', rethinking(), tot*7)    #Runs RETHINKING algorithm
            
            if((cnt+1)%2==0):
                print(f'\n\tFor REQUEST {req_no} ITERATION {cnt+1} COMPLETED\n\n')
            printToExcel()
            cnt += 1
    

#######################################################################################
#######################################################################################
##                                                                                   ##
##    IMPORTANT - CLOSE test.xlsx (excel file) IF OPEN BEFORE RUNNING THIS           ##
##                                                                                   ##
##    IMPORTANT - PLEASE CHOOSE THE PICKLE FILE, CRB & BW LIMITS FOR                 ##  
##                ALL(RANDOM, UNIFORM, POISSION) DISTRIBUTIONS BEFORE RUNNING THIS   ##
##                                                                                   ##
#######################################################################################
#######################################################################################
def generateSubstrate(for_automate, pickle_name):
    substrate, _ = for_automate(1)
    geeky_file = open(pickle_name, 'wb')
    pickle.dump(substrate, geeky_file)
    geeky_file.close()

def extractSubstrate(pickle_file):
    filehandler = open(pickle_file, 'rb')
    substrate = pickle.load(filehandler)
    return substrate

def runExtraction(pickle_name, pre_resource_name, vnr):
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource=pre_resource_name)
    printToExcel()
    if(pre_resource_name=='RANDOM'):
        print('\nRandom Extraction\n')
    elif(pre_resource_name=='NORMAL'):
        print('\nNormal Extraction\n')
    elif(pre_resource_name=='UNIFORM'):
        print('\nUniform Extraction\n')
    elif(pre_resource_name=='POISSION'):
        print('\nPoission Extraction\n')
    main(substrate, vnr)    

def runRandomExtraction(pickle_name):
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource='RANDOM')
    printToExcel()
    print("\nRandom Extraction\n")
    main(substrate, vne)

def runNormalExtraction(pickle_name):
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource='NORMAL')
    printToExcel()
    print("\nNormal Extraction\n")
    main(substrate, vne_n)

def runUniformExtraction(pickle_name):
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource='UNIFORM')
    printToExcel()
    print("\nUNIFORM Extraction\n")    
    main(substrate, vne_u)

def runPoissionExtraction(pickle_name):
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource='POISSION')
    printToExcel()
    print("\nPOISSON Extraction\n")
    main(substrate, vne_p)


if __name__ == "__main__":

    file_exists = os.path.exists('1_random.pickle') or os.path.exists('1_uniform.pickle') or os.path.exists('1_poission.pickle') or os.path.exists('1_normal.pickle')
    print(file_exists)
    file_exists = False       #Manually set, if want to update a substrate pickle
    if(file_exists==False):
        generateSubstrate(graph_extraction.for_automate, str(1)+'_random.pickle')        #Random Distribution
        generateSubstrate(graph_extraction_normal.for_automate, str(1)+'_normal.pickle')    #Normal Distribution
        generateSubstrate(graph_extraction_uniform.for_automate, str(1)+'_uniform.pickle')    #Uniform Distribution
        generateSubstrate(graph_extraction_poisson.for_automate, str(1)+'_poission.pickle')    #Poission Distribution

    runExtraction('1_random.pickle', 'RANDOM', vne)
    # runExtraction('1_normal.pickle', 'NORMAL', vne_n)
    # runExtraction('1_uniform.pickle', 'UNIFORM', vne_u)
    # runExtraction('1_poission.pickle', 'POISSION', vne_p)

    # runRandomExtraction('1_uniform.pickle')
    # runUniformExtraction('1_uniform.pickle')
    # runPoissionExtraction('1_poission.pickle')
    # runNormalExtraction('1_normal.pickle')
    
    excel = pd.DataFrame(output_dict)
    excel.to_excel("result.xlsx")
