import numpy as np 
import pandas as pd 

og = pd.read_csv(r"C:\Users\deela\Downloads\AL161973 - Gilda - original.csv", header = None)
md = pd.read_csv(r"C:\Users\deela\Downloads\AL161973 - Gilda - revised.csv", header = None)

metadata = []
for x in range(len(og)):
    metadata.append(og.iloc[x].values)
    metadata.append(md.iloc[x].values)
    metadata.append(['', '', '', '', '', '', '', ''])

newCSV = pd.DataFrame(np.array(metadata))
newCSV.to_csv(r"C:\Users\deela\Downloads\AL161973 - Gilda.csv")
print(newCSV)