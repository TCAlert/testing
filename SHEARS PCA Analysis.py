import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
import scipy 
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
    print(values)
    xBins = np.arange(-40, 45, 5)
    yBins = np.arange(-40, 45, 5)
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

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.lats > 0, drop = True)
validCases = dataset['case']
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))# - ds['climoMean'].values) / ds['climoStdd'].values)
pcseries = np.dot(anom.reshape(32250, 28), EOFs.reshape(28, 28).T)

variable = 'delta_vmax'

corr, sig = scipy.stats.pearsonr(pcseries[:, 0], pcseries[:, 1])
print("1 vs 2: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 1], pcseries[:, 2])
print("2 vs 3: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 0], pcseries[:, 2])
print("1 vs 3: " + str(corr) + "\n")

corr, sig = scipy.stats.pearsonr(pcseries[:, 0], np.nan_to_num(dataset[variable]))
print("1 vs DVmax: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 1], np.nan_to_num(dataset[variable]))
print("2 vs DVmax: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 2], np.nan_to_num(dataset[variable]))
print("3 vs DVmax: " + str(corr) + "\n")

dShear = dataset['sh_mag'].sel(upper = 200, lower = 850)
corr, sig = scipy.stats.pearsonr(pcseries[:, 0], dShear)
print("1 vs DShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 1], dShear)
print("2 vs DShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 2], dShear)
print("3 vs Dshear: " + str(corr) + "\n")

uShear = dataset['sh_mag'].sel(upper = 200, lower = 500)
corr, sig = scipy.stats.pearsonr(pcseries[:, 0], uShear)
print("1 vs UShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 1], uShear)
print("2 vs UShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 2], uShear)
print("3 vs Ushear: " + str(corr) + "\n")

mShear = dataset['sh_mag'].sel(upper = 500, lower = 850)
corr, sig = scipy.stats.pearsonr(pcseries[:, 0], mShear)
print("1 vs MShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 1], mShear)
print("2 vs MShear: " + str(corr))
corr, sig = scipy.stats.pearsonr(pcseries[:, 2], mShear)
print("3 vs Mshear: " + str(corr) + "\n")

corr, sig = scipy.stats.pearsonr(np.nan_to_num(dataset[variable]), dShear)
print("DVMax vs DShear: " + str(corr) + "\n")

grid, data, nobs = bin(pcseries[:, 2], pcseries[:, 0], dataset[variable])#dataset[variable].sel(upper = 200, lower = 500))
nobs = (nobs)# / 32250)#np.nanmax(nobs))# * 1.75
print(np.nanmin(nobs), np.nanmax(nobs))
#nobs = np.where(nobs > 1, 1, nobs)

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()
ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'PC3 Series', weight = 'bold', size = 9)
ax.set_ylabel('PC1 Series', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')

variable = 'Delta VMax (kt)'

s = plt.pcolormesh(grid[1], grid[0], data, cmap = 'RdBu_r', vmin = -30, vmax = 30)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label(variable)

ax.set_title(f'SHEARS TC Hodograph PC1/PC3 Binned 24hr Change in VMax\n{name.upper()}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
#plt.savefig(r"C:\Users\deela\Downloads\EOFs\SHEARSPC13Binned_" +  variable + "test_median.png", dpi = 400, bbox_inches = 'tight')
plt.show()
