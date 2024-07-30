import xarray as xr
import numpy as np
from scipy.signal import detrend
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cmaps as cmap 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
np.set_printoptions(suppress=True)

labelsize = 9
storm = 'AL25'
y = '2005'

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.atcf == storm, drop = True)
year = [str(x).split('-')[0] for x in dataset.time.values]
dataset = dataset.assign(year = (['case'], year))
dataset = dataset.where(dataset.year == y, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
shearData = dataset['sh_mag']
shearData.values = np.nan_to_num(shearData.values)

eofData = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
anom = np.nan_to_num((shearData.values - eofData['climoMean'].values))# / eofData['climoStdd'].values)
print(eofData)

eof1 = np.nan_to_num(eofData['eof'].sel(num = 1).values)
eof2 = np.nan_to_num(eofData['eof'].sel(num = 2).values)
pcseries1, pcseries2 = [], []
for x in range(len(shearData)):
    # print(dataset.where(dataset.time == np.datetime64('2005-10-23T06'), drop = True).case)
    # test = np.multiply(eof2.flatten(), anom[30].flatten())
    # plt.imshow(anom[30])
    # plt.colorbar()
    # plt.show()
    # print(list(test.flatten()))
    # plt.imshow(test.reshape(14, 14))
    # plt.colorbar()
    # plt.show()
    pcseries1.append(np.dot(eof1.flatten(), anom[x].flatten()))
    pcseries2.append(np.dot(eof2.flatten(), anom[x].flatten()))
print(pcseries1[-1], pcseries2[-1])
pcseries1 = (pcseries1)# - eofData['mean'].sel(num = 1).values) / eofData['stddev'].sel(num = 1).values
pcseries2 = (pcseries2)# - eofData['mean'].sel(num = 2).values) / eofData['stddev'].sel(num = 2).values

fig = plt.figure(figsize=(14, 11))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'PC2 Series', weight = 'bold', size = 9)
ax.set_ylabel(f'PC1 Series', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')
ax.plot(pcseries2, pcseries1, color = 'black', alpha = 0.5, linewidth = 0.5)

stat = dataset['system_type']
for x in range(len(stat)):
    if stat[x] in ['SD', 'SS']:
        ax.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6, marker = 's')
    elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
        ax.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), alpha = 0.375, vmin = 0, vmax = 140, linewidths=0.75, edgecolors='black', zorder = 6, marker = '^')
    else:
        s = plt.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])
cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])
cbar.set_label('Maximum Sustained Wind (kt)')
ax.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical'), plt.Line2D([0], [0], marker = "^", markersize = 8, linewidth = 0, label = 'Non-TC')], loc = 'upper right')
ax.set_title(f'SHEARS TC Vertical Wind Shear Distribution PC1/PC2 Scatterplot\n{storm.upper()}{y}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSPCscatter.png", dpi = 400, bbox_inches = 'tight')
plt.show()
