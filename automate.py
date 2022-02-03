import pandas as pd
from vikor import main as vikor
from greedy import main as greedy
from graph_extraction import for_automate


output_dict = {
        "revenue": [],
        "total_cost" : [],
        "accepted" : [],
        "total_request": [],
        "pre_resource": [],
        "post_resource": [],
        "avg_link": [],
        "avg_node": [],
        "avg_exec": [],
    }

for req_no in range(5, 15, 5):
    for_automate(req_no)
    gred_out = greedy()
    vikor_out = vikor()
    for key, value in gred_out.items():
        output_dict[key].append(value)
    for key, value in vikor_out.items():
        output_dict[key].append(value)
excel = pd.DataFrame(output_dict)
excel.to_excel("dimag.xlsx")
