import pandas as pd
from vikor import main as vikor
from greedy import main as greedy
from rethinking import main as rethinking
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
for req_no in range(5, 56, 5):
    tot += 1
    for_automate(req_no)
    setup_logger('log1','vikor.log')
    setup_logger('log2','greedy.log')
    setup_logger('log3','rethinking.log')
    gred_out = greedy()
    print(f"greedy done for req no {req_no}")
    vikor_out = vikor()
    print(f"vikor done for req no {req_no}")
    rethink_out = rethinking()
    print(f"rethinking done for req no {req_no}\n\n")

    # cnt =0
    # while(gred_out is None or vikor_out is None or rethink_out is None):
    #     for_automate(req_no)
    #     setup_logger('log1','vikor.log')
    #     setup_logger('log2','greedy.log')
    #     setup_logger('log3','rethinking.log')
    #     gred_out = greedy()
    #     vikor_out = vikor()
    #     rethink_out = rethinking()
    #     cnt += 1
    #     if cnt >= 5:
    #         break
    
    if (gred_out is None or vikor_out is None or rethink_out is None):
        continue
    
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
    
    output_dict["algorithm"].append('RETHINKING')
    output_dict["revenue"].append(rethink_out['revenue'])
    output_dict["total_cost"].append(rethink_out['total_cost'])
    output_dict["revenuetocostratio"].append((rethink_out['revenue']/rethink_out['total_cost'])*100)
    output_dict["accepted"].append(rethink_out['accepted'])
    output_dict["total_request"].append(rethink_out['total_request'])
    output_dict["embeddingratio"].append((rethink_out['accepted']/rethink_out['total_request'])*100)
    output_dict["pre_resource"].append(rethink_out['pre_resource'])
    output_dict["post_resource"].append(rethink_out['post_resource'])
    output_dict["consumed"].append(rethink_out['pre_resource']-rethink_out['post_resource'])
    output_dict["avg_link"].append(rethink_out['avg_link'])
    output_dict["avg_node"].append(rethink_out['avg_node'])
    output_dict["avg_exec"].append(rethink_out['avg_exec'].total_seconds()*1000/rethink_out['total_request'])

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

output_dict["algorithm"].append(tot)
output_dict["revenue"].append(rev_cnt)
output_dict["total_cost"].append('')
output_dict["revenuetocostratio"].append(rct_cnt)
output_dict["accepted"].append(acc_cnt)
output_dict["total_request"].append('')
output_dict["embeddingratio"].append(acc_cnt)
output_dict["pre_resource"].append('')
output_dict["post_resource"].append('')
output_dict["consumed"].append('')
output_dict["avg_link"].append('')
output_dict["avg_node"].append('')
output_dict["avg_exec"].append(exec_cnt)

excel = pd.DataFrame(output_dict)
excel.to_excel("test.xlsx")
