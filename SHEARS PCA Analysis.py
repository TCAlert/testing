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

def bin(xPC, yPC, values):
    xBins = np.arange(-10, 10.25, 0.25)
    yBins = np.arange(-10, 10.25, 0.25)
    grid = np.meshgrid(xBins, yBins)

    data = []
    nobs = []
    for x in range(len(xBins)):
        for y in range(len(yBins)):
            subList = []
            for z in range(len(values)):
                try:
                    if (xPC[z] > xBins[x]) and (xPC[z] < xBins[x + 1]) and (yPC[z] > yBins[y]) and (yPC[z] < yBins[y + 1]):
                        subList.append(values[z])
                except:
                    pass
            data.append(np.nanmean(subList))
            nobs.append(len(subList))
    data = np.array(data)
    nobs = np.array(nobs)
    print(np.nanmax(data), np.nanmin(data))

    return grid, np.array(data).reshape(grid[0].shape), np.array(nobs).reshape(grid[0].shape)

labelsize = 9
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
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data - ds['climoMean'].values) / ds['climoStdd'].values)
pcseries = np.dot(anom.reshape(24235, 28), EOFs.reshape(28, 28).T)

grid, data, nobs = bin(pcseries[:, 2], pcseries[:, 0], dataset.lats)
nobs = (nobs / np.nanmax(nobs)) * 1.75
nobs = np.where(nobs > 1, 1, nobs)

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'PC3 Series', weight = 'bold', size = 9)
ax.set_ylabel('PC1 Series', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')

s = plt.pcolormesh(grid[1], grid[0], data, cmap = cmap.tempAnoms3(), alpha = nobs, vmin = 0, vmax = 40)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label('Delta_VMax (kt)')

ax.set_title(f'SHEARS TC Hodograph PC1/PC3 Binned 24hr Change in VMax\n{name.upper()}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSPC13Binned_.png", dpi = 400, bbox_inches = 'tight')
plt.show()
