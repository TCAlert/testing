import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.stats import pearsonr
np.set_printoptions(suppress=True)

labelsize = 9
numOfEOFS = 3
lev = 200

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
pres = dataset.upper
climoMean = np.nanmean(dataset['sh_mag'].values, axis = 0)
climoStdd = np.nanstd(dataset['sh_mag'].values, axis = 0)

uData = dataset['u_data'].sel(upper = lev)
vData = dataset['v_data'].sel(upper = lev)

corr, sign = pearsonr(uData, vData)
print(corr, sign)

fig = plt.figure(figsize=(14, 11))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'Zonal Component (kt)', weight = 'bold', size = 9)
ax.set_ylabel(f'Meridional Component (kt)', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')

s = plt.scatter(uData, vData, c = dataset.vmax, cmap = cmap.probs2(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])
cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])
cbar.set_label('Maximum Sustained Wind (kt)')
ax.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical'), plt.Line2D([0], [0], marker = "^", markersize = 8, linewidth = 0, label = 'Non-TC')], loc = 'upper right')
ax.set_title(f'SHEARS TC Scatterplot of Zonal vs. Meridional {lev}mb Wind Components\nCorrelation: {round(corr, 2)}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSCompScatter" + str(lev) + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()
