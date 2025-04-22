import pandas as pd

oni = pd.read_csv(r"C:\Users\deela\Downloads\ensoni.csv")
pdo = pd.read_fwf(r"C:\Users\deela\Downloads\pdo.txt")

aso = (pdo['Aug'] + pdo['Sep'] + pdo['Oct']) / 3

l1 = list(oni[(oni['ASO'] > -0.6) & (oni['ASO'] < 0.6)]['Year'].values)
l2 = list(oni[(aso < 0)]['Year'].values)

clean = []

for x in range(len(l1)):
    if l1[x] not in clean:
            clean.append(l1[x])
for y in range(len(l2)):
     if l2[y] not in clean:
           clean.append(l2[y])

print(clean)

