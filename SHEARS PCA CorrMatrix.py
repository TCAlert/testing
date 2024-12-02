import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
import pandas
from sklearn import linear_model
import scipy
np.set_printoptions(suppress=True)

def genShear(u, v):
    print(u.shape)
    meanU = np.mean(u, axis = 1)
    meanV = np.mean(v, axis = 1)

    sum = np.sum(np.sqrt((u - meanU[:, np.newaxis])**2 + (v - meanV[:, np.newaxis])**2), axis = 1)
    print(sum.shape)

    return sum

def regression(input, output):
    input = np.transpose(input)
    
    trainIn = input[:25000]
    trainOut = output[:25000]
    testIn = input[25000:]
    testOut = output[25000:]

    regr = linear_model.LinearRegression()
    regr.fit(trainIn, trainOut)

    predictTest = regr.predict(testIn)

    corr, sig = scipy.stats.pearsonr(predictTest, testOut)
    error = np.mean(np.abs(predictTest - testOut))
    plt.scatter(predictTest, testOut)
    plt.show()

    print(str(error) + f"kt error\nCorrelation: {corr**2}")

def norm(data):
    return (data - np.nanmean(data)) / np.nanstd(data)

labelsize = 9
name = 'All TCs'
ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
EOFs = ds['eof'].values

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(list(dataset.variables))
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.lats > 0, drop = True)
validCases = dataset['case']
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))
pcseries = np.dot(anom.reshape(32250, 28), EOFs.reshape(28, 28).T)

variable = 'delta_vmax'
gShear = norm(genShear(dataset['u_data'].values, dataset['v_data'].values))
dShear = norm(dataset['sh_mag'].sel(upper = 200, lower = 850))
uShear = norm(dataset['sh_mag'].sel(upper = 200, lower = 500))
mShear = norm(dataset['sh_mag'].sel(upper = 500, lower = 850))
vmax = norm(np.nan_to_num(dataset['vmax']))
dist = norm(np.nan_to_num(dataset['dist_land']))
rhlm = norm(np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper')))
sst = norm(np.nan_to_num(dataset.sst))
mpi = norm(np.nan_to_num(dataset.mpi))

corrList = []
variables = [pcseries[:, 0], pcseries[:, 1], pcseries[:, 2], np.nan_to_num(dataset['vmax']), np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper')), np.nan_to_num(dataset.sst), np.nan_to_num(dataset.mpi), dShear, uShear, mShear, gShear, np.nan_to_num(dataset[variable])]
regression(np.array([pcseries[:, 0], pcseries[:, 1], pcseries[:, 2], dShear, gShear, dist, vmax, sst, mpi]), np.nan_to_num(dataset[variable]))

for x in range(len(variables)):
    for y in range(len(variables)):
        if x >= y:
            corr, sig = scipy.stats.pearsonr(variables[x], variables[y])
            corrList.append(corr)
        else:
            corrList.append(0)

corrList = np.array(corrList).reshape(len(variables), len(variables))

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()
ax.set_frame_on(False)
ax.set_xticks(np.arange(len(variables)))
ax.set_xticklabels(['PC1', 'PC2', 'PC3', 'VMax', 'RLHM', 'MPI', 'LAT', 'DShr', 'UShr', 'MShr', 'GShr', 'DVMax']) 
ax.set_yticks(np.arange(len(variables)))
ax.set_yticklabels(['PC1', 'PC2', 'PC3', 'VMax', 'RLHM', 'MPI', 'LAT', 'DShr', 'UShr', 'MShr', 'GShr', 'DVMax']) 

s = plt.pcolormesh(np.arange(len(variables)), np.arange(len(variables)), corrList, cmap = 'seismic', vmin = -1, vmax = 1)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label("Correlation")

ax.set_title(f'Correlation Matrix', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
#plt.savefig(r"C:\Users\deela\Downloads\EOFs\corrMatrix.png", dpi = 400, bbox_inches = 'tight')
plt.show()
