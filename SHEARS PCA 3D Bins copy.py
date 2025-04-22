import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
import csv
np.set_printoptions(suppress=True)

def bin(xPC, yPC, zPC, values, cases):
    xBins = np.arange(-40, 45, 5)
    yBins = np.arange(-40, 45, 5)
    zBins = np.arange(-40, 45, 5)

    data = []
    for x in range(len(xBins)):
        for y in range(len(yBins)):
            for z in range(len(zBins)):
                subList = []
                subList2 = []
                for a in range(len(values)):
                    try:
                        if (xPC[a] > xBins[x]) and (xPC[a] < xBins[x + 1]) and (yPC[a] > yBins[y]) and (yPC[a] < yBins[y + 1]) and (zPC[a] > zBins[z]) and (zPC[a] < zBins[z + 1]):
                            subList.append(values[a])
                            subList2.append(int(cases[a].values))
                    except:
                        pass
                print([[xBins[x], yBins[y], zBins[z]], np.nanmean(subList), len(subList), subList2])
                data.append([[xBins[x], yBins[y], zBins[z]], np.nanmean(subList), len(subList), subList2])
    return data

name = 'All TCs'
ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
EOFs = ds['eof'].values

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.lats > 0, drop = True)
validCases = dataset['case']

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))
pcseries = np.dot(anom.reshape(32250, 28), EOFs.reshape(28, 28).T)

variable = 'delta_vmax'    

data = bin(pcseries[:, 0], pcseries[:, 1], pcseries[:, 2], dataset[variable], validCases)

with open(r"C:\Users\deela\Downloads\EOFs\PCs.csv", "w") as f:
    wr = csv.writer(f)
    wr.writerows(data)

# temp = []
# for x in range(len(data)):
#     print(data[x])

# temp = np.array(temp)
# temp = temp[temp[:, 4].argsort()[::-1]]
# for x in range(len(temp)):
#     print(temp[x])