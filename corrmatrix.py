import matplotlib.pyplot as plt
import xarray as xr 
import scipy 
import numpy as np
import cmaps as cmap 
import matplotlib.patheffects as pe

def genShear(u, v):
    print(u.shape)
    meanU = np.mean(u, axis = 1)
    meanV = np.mean(v, axis = 1)

    sum = np.sum(np.sqrt((u - meanU[:, np.newaxis])**2 + (v - meanV[:, np.newaxis])**2), axis = 1)
    print(sum.shape)

    return sum

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(dataset)
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
validCases = dataset['case']
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))

variable = 'fdelta_vmax'
gShear = genShear(dataset['u_data'].values, dataset['v_data'].values)
dShear = dataset['sh_mag'].sel(upper = 200, lower = 850)
uShear = dataset['sh_mag'].sel(upper = 200, lower = 500)
mShear = dataset['sh_mag'].sel(upper = 500, lower = 850)
vmax = np.nan_to_num(dataset['vmax'])
dist = np.nan_to_num(dataset['dist_land'])
rhlm = np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper'))
sst = np.nan_to_num(dataset.sst)
mpi = np.nan_to_num(dataset.mpi)
bdv = np.nan_to_num(dataset.bdelta_vmax)
tmp = np.nan_to_num(dataset.temperature.sel(upper = 200))
div = np.nan_to_num(dataset.divergence.sel(upper = 200))
lat = np.nan_to_num(dataset.lats)

corrList = []
predictors = [gShear, dShear, uShear, mShear, vmax, dist, rhlm, sst, mpi, bdv, tmp, div, lat]
for x in range(len(predictors)):
    for y in range(len(predictors)):
        try:
            corr, sig = scipy.stats.pearsonr(predictors[x], predictors[y])
            corr = corr**2
        except:
            corr = 0
        corrList.append(corr)

corrList = np.transpose(np.array(corrList).reshape(len(predictors), len(predictors)))
corrList = corrList# - corrList[:, [0]]

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()
ax.set_frame_on(False)
ax.set_xticks(range(len(predictors)))
ax.set_yticks(range(len(predictors)))
ax.set_xticklabels(['GSHR', 'DSHR', 'USHR', 'MSHR', 'VMAX', 'DIST', 'RHLM', 'SST', 'MPI', '-DVMAX', 'TMP200', 'DIV200', 'LAT']) 
ax.set_yticklabels(['GSHR', 'DSHR', 'USHR', 'MSHR', 'VMAX', 'DIST', 'RHLM', 'SST', 'MPI', '-DVMAX', 'TMP200', 'DIV200', 'LAT']) 

s = plt.pcolormesh(np.arange(len(predictors)), np.arange(len(predictors)), corrList, cmap = cmap.probs2(), vmin = 0, vmax = .75)
for x in range(len(predictors)):
    for y in range(len(predictors)):
        plt.text(y, x, f'{(round(corrList[x][y], 3))}', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label("R^2")

ax.set_title(f'Table of Predictors (NATL)/R^2', fontweight='bold', fontsize=9, loc='left')  
ax.set_title(f'RF\nDeelan Jariwala', fontsize=9, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\corrmatrixthing.png", dpi = 400, bbox_inches = 'tight')
plt.show()
