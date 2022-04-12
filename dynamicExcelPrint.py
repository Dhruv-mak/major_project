import pandas as pd  
import pickle
filehandler = open("geekyfile", 'rb')
mapping = pickle.load(filehandler)

excel = pd.DataFrame(mapping)
excel.to_excel("test.xlsx")


