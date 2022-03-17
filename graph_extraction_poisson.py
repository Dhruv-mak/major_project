import os
import pickle
import sys
import graph_p
from vne_p import create_vne


class Extract:
    # def get_graphs(self, req_no = 5):     # USE THIS DEFINATION FOR AUTOMATION & comment line no 10
    def get_graphs(self):
        current = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(os.path.join(os.path.dirname(current), "P3_ALIB_MASTER"))
        current = os.path.join(
            os.path.dirname(current),
            "P3_ALIB_MASTER",
            "input",
            "senario_RedBestel.pickle",
        )
        with open(current, "rb") as f:
            data = pickle.load(f)
        para = graph_p.Parameters(100, 1000, 100, 1000, 0, 100, 0, 100, 1, 1)  # Parameters for subsrate graph BW ,CRB, Location,Delay
        mean = 0.4
        try: 
            substrate = graph_p.Graph(
                len(data.scenario_list[0].substrate.nodes),
                data.scenario_list[0].substrate.edges,
                para,
                mean,
            )
        except:
            substrate = graph_p.Graph(
                data.get("substrate").nodes,
                data.get("substrate").edges,
                para,
                mean,
            )
        # vne_list = create_vne(no_requests = req_no)   # USE THIS STATEMENT FOR AUTOMATION & comment line no 28
        vne_list = create_vne()
        return substrate, vne_list

def for_automate(req_no = 5):
    x = Extract()
    substrate, vne_list = x.get_graphs(req_no)
    output = {"substrate": substrate, "vne_list" : vne_list}
    pickle_file = open("input.pickle", "wb")
    pickle.dump(output, pickle_file)


if __name__ == "__main__":
    x = Extract()
    # substrate, vne_list = x.get_graphs(req_no = 15)    # USE THIS STATEMENT FOR AUTOMATION & comment line no 42
    substrate, vne_list = x.get_graphs()
    output = {"substrate": substrate, "vne_list" : vne_list}
    pickle_file = open("input.pickle", "wb")
    pickle.dump(output, pickle_file)