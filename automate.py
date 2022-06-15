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
            parser_out = parser()                         #Runs Parser algorithm
            exec_algorithm('PAGERANK-STABLE', parser_out[0], tot*2)        
            exec_algorithm('PAGERANK-DIRECT', parser_out[1], tot*2)        
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
    runExtraction('1_normal.pickle', 'NORMAL', vne_n)
    runExtraction('1_uniform.pickle', 'UNIFORM', vne_u)
    runExtraction('1_poission.pickle', 'POISSION', vne_p)
    
    excel = pd.DataFrame(output_dict)
    excel.to_excel("result.xlsx")
