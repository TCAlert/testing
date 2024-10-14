import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
np.set_printoptions(suppress=True)

class Normalizer:
    def __init__(self, data):
        self.data = data
        self.mean = data.mean(['case'])
        self.stdd = data.std(['case'])

    def normalize(self):
        all_zscores = ((self.data - self.mean) / self.stdd)
        return all_zscores.values

    def denormalize(self, data):
        return data * self.stdd + self.mean

def bin(xPC, yPC, zPC, values, cases):
    xBins = np.arange(-5, 6, 1)
    yBins = np.arange(-5, 6, 1)
    zBins = np.arange(-5, 6, 1)
    grid = np.meshgrid(xBins, yBins, zBins)

    data = []
    bCase = []
    nobs = []
    for x in range(len(xBins)):
        for y in range(len(yBins)):
            for z in range(len(zBins)):
                subList = []
                subList2 = []
                for a in range(len(values)):
                    try:
                        if (xPC[a] > xBins[x]) and (xPC[a] < xBins[x + 1]) and (yPC[a] > yBins[y]) and (yPC[a] < yBins[y + 1]) and (zPC[a] > zBins[z]) and (zPC[a] < zBins[z + 1]):
                            subList.append(values[a])
                            subList2.append(cases[a].values)
                    except:
                        pass
                data.append(np.nanmean(subList))
                bCase.append(subList2)
                nobs.append(len(subList))
    data = np.array(data)
    nobs = np.array(nobs)
    print(np.nanmax(data), np.nanmin(data))

    return grid, data.reshape(grid[0].shape), nobs.reshape(grid[0].shape), bCase

name = 'All TCs'
ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
EOFs = ds['eof'].values

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.lats > 0, drop = True)
dataset = dataset.where(dataset.sst > 26, drop=True)
validCases = dataset['case']

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data - ds['climoMean'].values) / ds['climoStdd'].values)
pcseries = np.dot(anom.reshape(24235, 28), EOFs.reshape(28, 28).T)

variable = 'delta_vmax'

grid, data, nobs, cases = bin(pcseries[:, 0], pcseries[:, 1], pcseries[:, 2], dataset[variable], validCases)
print(np.nanmax(nobs))
nobs = (nobs)# / np.nanmax(nobs))

temp = []
for x in range(len(data)):
    for y in range(len(data[x])):
        for z in range(len(data[x][y])):
            if np.isnan(data[x, y, z]):
                pass
            else:
                temp.append([x - 5, y - 5, z - 5, nobs[x, y, z], data[x, y, z]])

temp = np.array(temp)
temp = temp[temp[:, 4].argsort()[::-1]]
for x in range(len(temp)):
    print(temp[x])