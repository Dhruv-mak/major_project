import pandas as pd
from topsis import main as vikor
from greedy import main as greedy
from graph_extraction import for_automate
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
        "avg_link": [],
        "avg_node": [],
        "avg_exec": [],
    }

rev_cnt=0
rct_cnt=0
acc_cnt=0
exec_cnt=0
tot=0
for req_no in range(5, 11, 5):
    tot += 1
    for_automate(req_no)
    setup_logger('log1','vikor.log')
    setup_logger('log2','greedy.log')
    gred_out = greedy()
    vikor_out = vikor()
    
    # for key, value in gred_out.items():
    #     output_dict[key].append(value)
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
    output_dict["avg_link"].append(gred_out['avg_link'])
    output_dict["avg_node"].append(gred_out['avg_node'])
    output_dict["avg_exec"].append(gred_out['avg_exec'].total_seconds()*1000/gred_out['total_request'])
    
    # for key, value in vikor_out.items():
    #     output_dict[key].append(value)
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
    output_dict["avg_link"].append(vikor_out['avg_link'])
    output_dict["avg_node"].append(vikor_out['avg_node'])
    output_dict["avg_exec"].append(vikor_out['avg_exec'].total_seconds()*1000/vikor_out['total_request'])

    if vikor_out['revenue']>gred_out['revenue']:
        rev_cnt += 1
    
    if (vikor_out['revenue']/vikor_out['total_cost'])*100 >(gred_out['revenue']/gred_out['total_cost'])*100:
        rct_cnt += 1
    
    if vikor_out['accepted']>gred_out['accepted']:
        acc_cnt += 1
  
    if vikor_out['avg_exec']<gred_out['avg_exec']:
        exec_cnt += 1
    
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
    output_dict["avg_link"].append('')
    output_dict["avg_node"].append('')
    output_dict["avg_exec"].append('')
excel = pd.DataFrame(output_dict)
excel.to_excel("test.xlsx")
