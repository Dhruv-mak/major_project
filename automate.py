from time import sleep
import pandas as pd
from vikor import main as vikor
from greedy import main as greedy
from parser import main as parser
from vrmap import main as vrmap
from rethinking import main as rethinking
from topsis import main as topsis
import graph_extraction
import graph_extraction_uniform
import graph_extraction_poisson
import logging


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
    }

rev_cnt=0
rct_cnt=0
acc_cnt=0
exec_cnt=0
def main(for_automate):
    tot=0
    ls = [5]
    for req_no in ls:
        tot += 1
        print(f"\n\treq_no: {req_no}\n")
        for_automate(req_no)
        # setup_logger('log1','vikor.log')
        # setup_logger('log2','greedy.log')
        gred_out = greedy()
        sleep(tot*1)
        vikor_out = vikor()
        sleep(tot*1)
        topsis_out = topsis()
        sleep(tot*1)
        parser_out = parser()
        sleep(tot*2)
        vrmap_out = vrmap()
        sleep(tot*7)
        rethinking_out = rethinking()
        sleep(tot*15)
        
        output_dict["algorithm"].append('GREEDY')
        output_dict["revenue"].append(gred_out['revenue'])
        output_dict["total_cost"].append(gred_out['total_cost'])
        output_dict["revenuetocostratio"].append((gred_out['revenue']/gred_out['total_cost'])*100)
        output_dict["accepted"].append(gred_out['accepted'])
        output_dict["total_request"].append(gred_out['total_request'])
        output_dict["embeddingratio"].append((gred_out['accepted']/gred_out['total_request'])*100)
        output_dict["pre_resource"].append(gred_out['pre_resource'])
        output_dict["post_resource"].append(gred_out['post_resource'])
        output_dict["consumed"].append(gred_out['pre_resource']-gred_out['post_resource'])
        output_dict["avg_bw"].append(gred_out['avg_bw'])
        output_dict["avg_crb"].append(gred_out['avg_crb'])
        output_dict["avg_link"].append(gred_out['avg_link'])
        output_dict["avg_node"].append(gred_out['avg_node'])
        output_dict["avg_path"].append(gred_out['avg_path'])
        output_dict["avg_exec"].append(gred_out['avg_exec'].total_seconds()*1000/gred_out['total_request'])
        
        
        output_dict["algorithm"].append('VIKOR')
        output_dict["revenue"].append(vikor_out['revenue'])
        output_dict["total_cost"].append(vikor_out['total_cost'])
        output_dict["revenuetocostratio"].append((vikor_out['revenue']/vikor_out['total_cost'])*100)
        output_dict["accepted"].append(vikor_out['accepted'])
        output_dict["total_request"].append(vikor_out['total_request'])
        output_dict["embeddingratio"].append((vikor_out['accepted']/vikor_out['total_request'])*100)
        output_dict["pre_resource"].append(vikor_out['pre_resource'])
        output_dict["post_resource"].append(vikor_out['post_resource'])
        output_dict["consumed"].append(vikor_out['pre_resource']-vikor_out['post_resource'])
        output_dict["avg_bw"].append(vikor_out['avg_bw'])
        output_dict["avg_crb"].append(vikor_out['avg_crb'])
        output_dict["avg_link"].append(vikor_out['avg_link'])
        output_dict["avg_node"].append(vikor_out['avg_node'])
        output_dict["avg_path"].append(vikor_out['avg_path'])
        output_dict["avg_exec"].append(vikor_out['avg_exec'].total_seconds()*1000/vikor_out['total_request'])

        output_dict["algorithm"].append('TOPSIS')
        output_dict["revenue"].append(topsis_out['revenue'])
        output_dict["total_cost"].append(topsis_out['total_cost'])
        output_dict["revenuetocostratio"].append((topsis_out['revenue']/topsis_out['total_cost'])*100)
        output_dict["accepted"].append(topsis_out['accepted'])
        output_dict["total_request"].append(topsis_out['total_request'])
        output_dict["embeddingratio"].append((topsis_out['accepted']/topsis_out['total_request'])*100)
        output_dict["pre_resource"].append(topsis_out['pre_resource'])
        output_dict["post_resource"].append(topsis_out['post_resource'])
        output_dict["consumed"].append(topsis_out['pre_resource']-topsis_out['post_resource'])
        output_dict["avg_bw"].append(topsis_out['avg_bw'])
        output_dict["avg_crb"].append(topsis_out['avg_crb'])
        output_dict["avg_link"].append(topsis_out['avg_link'])
        output_dict["avg_node"].append(topsis_out['avg_node'])
        output_dict["avg_path"].append(topsis_out['avg_path'])
        output_dict["avg_exec"].append(topsis_out['avg_exec'].total_seconds()*1000/topsis_out['total_request'])
        
        output_dict["algorithm"].append('PAGERANK-STABLE')
        output_dict["revenue"].append(parser_out[0]['revenue'])
        output_dict["total_cost"].append(parser_out[0]['total_cost'])
        output_dict["revenuetocostratio"].append((parser_out[0]['revenue']/parser_out[0]['total_cost'])*100)
        output_dict["accepted"].append(parser_out[0]['accepted'])
        output_dict["total_request"].append(parser_out[0]['total_request'])
        output_dict["embeddingratio"].append((parser_out[0]['accepted']/parser_out[0]['total_request'])*100)
        output_dict["pre_resource"].append(parser_out[0]['pre_resource'])
        output_dict["post_resource"].append(parser_out[0]['post_resource'])
        output_dict["consumed"].append(parser_out[0]['pre_resource']-parser_out[0]['post_resource'])
        output_dict["avg_bw"].append(parser_out[0]['avg_bw'])
        output_dict["avg_crb"].append(parser_out[0]['avg_crb'])
        output_dict["avg_link"].append(parser_out[0]['avg_link'])
        output_dict["avg_node"].append(parser_out[0]['avg_node'])
        output_dict["avg_path"].append(parser_out[0]['avg_path'])
        output_dict["avg_exec"].append(parser_out[0]['avg_exec'].total_seconds()*1000/parser_out[0]['total_request'])

        output_dict["algorithm"].append('PAGERANK-DIRECT')
        output_dict["revenue"].append(parser_out[1]['revenue'])
        output_dict["total_cost"].append(parser_out[1]['total_cost'])
        output_dict["revenuetocostratio"].append((parser_out[1]['revenue']/parser_out[1]['total_cost'])*100)
        output_dict["accepted"].append(parser_out[1]['accepted'])
        output_dict["total_request"].append(parser_out[1]['total_request'])
        output_dict["embeddingratio"].append((parser_out[1]['accepted']/parser_out[1]['total_request'])*100)
        output_dict["pre_resource"].append(parser_out[1]['pre_resource'])
        output_dict["post_resource"].append(parser_out[1]['post_resource'])
        output_dict["consumed"].append(parser_out[1]['pre_resource']-parser_out[1]['post_resource'])
        output_dict["avg_bw"].append(parser_out[1]['avg_bw'])
        output_dict["avg_crb"].append(parser_out[1]['avg_crb'])
        output_dict["avg_link"].append(parser_out[1]['avg_link'])
        output_dict["avg_node"].append(parser_out[1]['avg_node'])
        output_dict["avg_path"].append(parser_out[1]['avg_path'])
        output_dict["avg_exec"].append(parser_out[1]['avg_exec'].total_seconds()*1000/parser_out[1]['total_request'])

        output_dict["algorithm"].append('VRMAP')
        output_dict["revenue"].append(vrmap_out['revenue'])
        output_dict["total_cost"].append(vrmap_out['total_cost'])
        output_dict["revenuetocostratio"].append((vrmap_out['revenue']/vrmap_out['total_cost'])*100)
        output_dict["accepted"].append(vrmap_out['accepted'])
        output_dict["total_request"].append(vrmap_out['total_request'])
        output_dict["embeddingratio"].append((vrmap_out['accepted']/vrmap_out['total_request'])*100)
        output_dict["pre_resource"].append(vrmap_out['pre_resource'])
        output_dict["post_resource"].append(vrmap_out['post_resource'])
        output_dict["consumed"].append(vrmap_out['pre_resource']-vrmap_out['post_resource'])
        output_dict["avg_bw"].append(vrmap_out['avg_bw'])
        output_dict["avg_crb"].append(vrmap_out['avg_crb'])
        output_dict["avg_link"].append(vrmap_out['avg_link'])
        output_dict["avg_node"].append(vrmap_out['avg_node'])
        output_dict["avg_path"].append(vrmap_out['avg_path'])
        output_dict["avg_exec"].append(vrmap_out['avg_exec'].total_seconds()*1000/vrmap_out['total_request'])

        output_dict["algorithm"].append('RETHINKING')
        output_dict["revenue"].append(rethinking_out['revenue'])
        output_dict["total_cost"].append(rethinking_out['total_cost'])
        output_dict["revenuetocostratio"].append((rethinking_out['revenue']/rethinking_out['total_cost'])*100)
        output_dict["accepted"].append(rethinking_out['accepted'])
        output_dict["total_request"].append(rethinking_out['total_request'])
        output_dict["embeddingratio"].append((rethinking_out['accepted']/rethinking_out['total_request'])*100)
        output_dict["pre_resource"].append(rethinking_out['pre_resource'])
        output_dict["post_resource"].append(rethinking_out['post_resource'])
        output_dict["consumed"].append(rethinking_out['pre_resource']-rethinking_out['post_resource'])
        output_dict["avg_bw"].append(rethinking_out['avg_bw'])
        output_dict["avg_crb"].append(rethinking_out['avg_crb'])
        output_dict["avg_link"].append(rethinking_out['avg_link'])
        output_dict["avg_node"].append(rethinking_out['avg_node'])
        output_dict["avg_path"].append(rethinking_out['avg_path'])
        output_dict["avg_exec"].append(rethinking_out['avg_exec'].total_seconds()*1000/rethinking_out['total_request'])

        output_dict["algorithm"].append('')
        output_dict["revenue"].append('')
        output_dict["total_cost"].append('')
        output_dict["revenuetocostratio"].append('')
        output_dict["accepted"].append('')
        output_dict["total_request"].append('')
        output_dict["embeddingratio"].append('')
        output_dict["pre_resource"].append('')
        output_dict["post_resource"].append('')
        output_dict["consumed"].append('')
        output_dict["avg_bw"].append('')
        output_dict["avg_crb"].append('')
        output_dict["avg_link"].append('')
        output_dict["avg_node"].append('')
        output_dict["avg_path"].append('')
        output_dict["avg_exec"].append('')
    

#######################################################################################
#######################################################################################
##                                                                                   ##
##       IMPORTANT - CLOSE test.xlsx (excel file) IF OPEN BEFORE RUNNING THIS        ##
##                                                                                   ##
#######################################################################################
#######################################################################################

if __name__ == "__main__":
    print("\nRandom Extraction\n")
    main(graph_extraction.for_automate)
    
    for _ in range(3):
        output_dict["algorithm"].append('UNIFORM')
        output_dict["revenue"].append('')
        output_dict["total_cost"].append('')
        output_dict["revenuetocostratio"].append('')
        output_dict["accepted"].append('')
        output_dict["total_request"].append('')
        output_dict["embeddingratio"].append('')
        output_dict["pre_resource"].append('')
        output_dict["post_resource"].append('')
        output_dict["consumed"].append('')
        output_dict["avg_bw"].append('')
        output_dict["avg_crb"].append('')
        output_dict["avg_link"].append('')
        output_dict["avg_node"].append('')
        output_dict["avg_path"].append('')
        output_dict["avg_exec"].append('')

    print("\nUNIFORM Extraction\n")    
    main(graph_extraction_uniform.for_automate)
    
    for _ in range(3):
        output_dict["algorithm"].append('POISSON')
        output_dict["revenue"].append('')
        output_dict["total_cost"].append('')
        output_dict["revenuetocostratio"].append('')
        output_dict["accepted"].append('')
        output_dict["total_request"].append('')
        output_dict["embeddingratio"].append('')
        output_dict["pre_resource"].append('')
        output_dict["post_resource"].append('')
        output_dict["consumed"].append('')
        output_dict["avg_bw"].append('')
        output_dict["avg_crb"].append('')
        output_dict["avg_link"].append('')
        output_dict["avg_node"].append('')
        output_dict["avg_path"].append('')
        output_dict["avg_exec"].append('')
    
    print("\nPOISSON Extraction\n")
    main(graph_extraction_poisson.for_automate)
    
    excel = pd.DataFrame(output_dict)
    excel.to_excel("test.xlsx")
