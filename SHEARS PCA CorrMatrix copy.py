import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
import pandas
from sklearn import linear_model
import scipy
from matplotlib import patheffects as pe
from sklearn.ensemble import RandomForestRegressor
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

    # regr = linear_model.LinearRegression()
    # regr.fit(trainIn, trainOut)
    # predictTest = regr.predict(testIn)

    regr = RandomForestRegressor(n_estimators=100)
    regr.fit(trainIn, trainOut) 
    predictTest = regr.predict(testIn)

    corr, sig = scipy.stats.pearsonr(predictTest, testOut)
    # error = np.sqrt(np.mean((predictTest - testOut)**2))
    # error = np.mean(np.abs(predictTest - testOut))
    # plt.scatter(predictTest, testOut)
    # plt.show()

    #print(str(error) + f"kt error\nCorrelation: {corr**2}")

    return corr**2

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
gShear = genShear(dataset['u_data'].values, dataset['v_data'].values)
dShear = dataset['sh_mag'].sel(upper = 200, lower = 850)
uShear = dataset['sh_mag'].sel(upper = 200, lower = 500)
mShear = dataset['sh_mag'].sel(upper = 500, lower = 850)
vmax = np.nan_to_num(dataset['vmax'])
dist = np.nan_to_num(dataset['dist_land'])
rhlm = np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper'))
sst = np.nan_to_num(dataset.sst)
mpi = np.nan_to_num(dataset.mpi)

corrList = []
variables = [pcseries[:, 0], pcseries[:, 1], pcseries[:, 2], np.nan_to_num(dataset['vmax']), np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper')), np.nan_to_num(dataset.sst), np.nan_to_num(dataset.mpi), dShear, uShear, mShear, gShear, np.nan_to_num(dataset[variable])]

xList = [[], [pcseries[:, 0]], [pcseries[:, 1]], [pcseries[:, 2]], [pcseries[:, 0], pcseries[:, 1]], [pcseries[:, 1], pcseries[:, 2]], [pcseries[:, 0], pcseries[:, 2]], [pcseries[:, 0], pcseries[:, 1], pcseries[:, 2]]]
yList = [[], [gShear], [dShear], [gShear, dShear], [gShear, dist, vmax, sst, mpi, rhlm], [dShear, dist, vmax, sst, mpi, rhlm], [gShear, dShear, dist, vmax, sst, mpi, rhlm], [dist, vmax, sst, mpi, rhlm]]

for x in range(len(xList)):
    for y in range(len(yList)):
        print(np.shape(np.array(xList[x] + yList[y])))
        try:
            corr = regression(np.array(xList[x] + yList[y]), np.nan_to_num(dataset[variable]))
        except:
            corr = 0
        corrList.append(corr)

corrList = np.transpose(np.array(corrList).reshape(len(xList), len(yList)))
corrList = corrList - corrList[:, [0]]

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()
ax.set_frame_on(False)
ax.set_xticklabels(['', 'None', 'PC1', 'PC2', 'PC3', 'PC1, PC2', 'PC2, PC3', 'PC1, PC3', 'PC1, PC2, PC3']) 
ax.set_yticklabels(['', 'None', 'GSHR', 'DSHR', 'GSHR\nDSHR', 'GSHR\nEXTRA', 'DSHR\nEXTRA', 'GSHR\nDSHR\nEXTRA', 'EXTRA']) 

s = plt.pcolormesh(np.arange(len(xList)), np.arange(len(yList)), corrList, cmap = cmap.probs2(), vmin = 0, vmax = 0.5)
for x in range(len(xList)):
    for y in range(len(yList)):
        plt.text(y, x, f'{(round(corrList[x][y], 3))}', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label("R^2")

ax.set_title(f'Table of Predictors/R^2', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'RF\nDeelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\EOFs\rfcorrmatrix3.png", dpi = 400, bbox_inches = 'tight')
plt.show()
