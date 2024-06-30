import pandas as pd 
import numpy as np 
data = pd.read_csv(r"C:\Users\deela\Downloads\ens oni trimonthly - Sheet2.csv")
aso = data['ASO']
print(np.percentile(aso.to_numpy(), 10))

for x in range(len(aso)):
    if aso[x] < -0.9454:
        print(data['Year'][x], aso[x])