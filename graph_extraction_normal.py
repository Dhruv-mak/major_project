import os
import pickle
import sys
import graph
import graph_n
from vne_n import create_vne


class Extract:
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
        para = graph.Parameters(100, 1000, 100, 1000, 0, 100, 0, 100, 1, 1)  # Parameters for subsrate graph
        try: 
            substrate = graph_n.Graph(
                len(data.scenario_list[0].substrate.nodes),
                data.scenario_list[0].substrate.edges,
                para,
            )
        except:
            substrate = graph_n.Graph(
                data.get("substrate").nodes,
                data.get("substrate").edges,
                para,
            )
        vne_list = create_vne()
        return substrate, vne_list

if __name__ == "__main__":
    x = Extract()
    substrate, vne_list = x.get_graphs()
    output = {"substrate": substrate, "vne_list" : vne_list}
    pickle_file = open("input.pickle", "wb")
    pickle.dump(output, pickle_file)