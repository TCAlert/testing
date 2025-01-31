import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cartopy, cartopy.crs as ccrs
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

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def bin(xPC, yPC, values):
    xBins = np.arange(45, 347.5, 2.5)
    yBins = np.arange(-10, 82.5, 2.5)
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
    print(np.nanmax(data), np.nanmin(data), grid[0].shape)

    return [grid[0].T, grid[1].T], np.array(data.T).reshape(grid[0].T.shape), np.array(nobs.T).reshape(grid[0].T.shape)

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
lons = dataset['lons'].values
lats = dataset['lats'].values
print(dataset)
print(np.nanmin(lons), np.nanmax(lons))

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))# - ds['climoMean'].values) / ds['climoStdd'].values)
pcseries = np.dot(anom.reshape(32250, 28), EOFs.reshape(28, 28).T)

num = 1

grid, data, nobs = bin(lons, lats, pcseries[:, num - 1])
#nobs = 10 * (nobs / np.nanmax(nobs))**1.4
#nobs = np.where(nobs > 1, 1, nobs)

ax = map(20, labelsize)

c = plt.pcolormesh(grid[0], grid[1], nobs, cmap = cmap.probs(), vmin = 0, vmax = 100, transform = ccrs.PlateCarree(central_longitude=0))
#c = plt.pcolormesh(grid[0], grid[1], data, cmap = cmap.tempAnoms(), levels = np.arange(-15, 15.25, 0.25), transform = ccrs.PlateCarree(central_longitude=0))
cbar = plt.colorbar(c, orientation = 'horizontal', aspect = 100, pad = .08)

ax.set_title(f'SHEARS TC Hodograph Cases Map\n2.5 Degree Bins', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\EOFs\SHEARSPCCasesMap.png", dpi = 400, bbox_inches = 'tight')
plt.show()
