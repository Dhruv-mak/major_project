import pickle
from pprint import pprint
def read_pickle():
    filehandler = open("input.pickle", 'rb')
    mapping = pickle.load(filehandler)
    substrate = mapping["substrate"]
    vne_list = mapping["vne_list"]
    return substrate, vne_list