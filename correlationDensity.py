import xarray as xr 
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
import pandas as pd 
from helper import numToMonth
import scipy.stats
from scipy.signal import detrend
from scipy.ndimage import gaussian_filter
import matplotlib as mpl
from ersstTimeseriesGenerator import timeseries 
mpl.rcParams['hatch.linewidth'] = 0.5
mpl.rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 5))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())

    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', which = 'major', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    # ax.grid(linestyle = '--', which = 'minor', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    # ax.minorticks_on()
    return ax 

def yearlySum(data):
    values = data.values
    values = values.reshape(int(values.shape[0] / 12), 12, 71, 181)
    values = np.sum(values, axis = 1)

    data = data.resample(time = 'AS').mean()
    data.values = values

    return data

startYear = 1978
endYear = 2023
indexMonth = '10'
dataMonth = '1'
index = 'SSTAs in Box'
type = 'ACE'
lats = [40, 60]
lons = [-70, -35]
boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
csv = timeseries(indexMonth, range(startYear, endYear + 1), slice(lats[1], lats[0]), slice(360 + lons[0], 360 + lons[1]))[numToMonth(indexMonth)[0:3]]
#csv = pd.read_csv(r"C:\Users\deela\Downloads\composites - " + index + ".csv")[numToMonth(indexMonth)[0:3]]
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityALL.nc")
data = dataset[type]
print(data.shape)
data = yearlySum(data)
s = 2
data.values = gaussian_filter(data.values, sigma = s, axes = (1, 2))
print(data)

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
data = data.sel(time = fMonths)
ogShape = data.shape

temp = data.values
temp = np.reshape(temp, (ogShape[0], ogShape[1] * ogShape[2]))
#temp = detrend(temp, axis = 0)
print(temp.shape, csv.shape)

corrData = []
signData = []
for x in range(temp.shape[1]):
    temp[:, x] = np.nan_to_num(temp[:, x])
    corr, sig = scipy.stats.pearsonr(temp[:, x], csv)
    corrData.append(corr)
    signData.append(sig)

print(np.array(corrData).shape)
data = data.mean('time')
data.values = np.reshape(corrData, (ogShape[1], ogShape[2]))
dataset['sig'] = ((ogShape[1], ogShape[2]), np.reshape(signData, (ogShape[1], ogShape[2])))

data.to_netcdf(r"C:\Users\deela\Downloads\HarrisonFile.nc")

ax = map(20, 9)
ax.set_extent([180, 359.9, 0, 70], crs = ccrs.PlateCarree(central_longitude = 0))
c = plt.contourf(data.longitude, data.latitude, data.values, cmap = cmap.tempAnoms3(), levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
h = plt.contourf(data.longitude, data.latitude, dataset['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))

try:
    for y in range(len(boxXCoords)):
        try:
            print([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]])
            ax.plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'black', zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
        except:
            pass
except:
    pass

for collection in h.collections:
    collection.set_edgecolor('#262626')
    collection.set_linewidth(0)

ax.set_title(f'HURDAT2 {type} Density Correlation with {numToMonth(indexMonth)} {index.upper()}\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Full Year', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\corrtest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
