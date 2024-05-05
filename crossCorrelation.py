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
import matplotlib as mpl
from ersstTimeseriesGenerator import timeseries 
mpl.rcParams['hatch.linewidth'] = 0.5
mpl.rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(14, 6))

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

fullDataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
dataset = fullDataset['sst']
dataset = dataset.fillna(0) * np.cos(np.radians(dataset['lat']))
print(dataset)

startYear = 1951
endYear = 2020
indexMonth = '12'
dataMonth = '1'

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
data1 = dataset.sel(time = fMonths)
fMonths = np.array([np.datetime64(f'{y}-{str(indexMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
data2 = dataset.sel(time = fMonths)
ogShape = data1.shape
print(ogShape)

temp1 = data1.values
temp1 = np.reshape(temp1, (ogShape[0], ogShape[1] * ogShape[2]))
temp1 = detrend(temp1, axis = 0)
temp2 = data2.values
temp2 = np.reshape(temp2, (ogShape[0], ogShape[1] * ogShape[2]))
temp2 = detrend(temp2, axis = 0)

print(temp1.shape, temp2.shape)

corrData = []
signData = []
for x in range(temp1.shape[1]):
    temp1[:, x] = np.nan_to_num(temp1[:, x])
    temp2[:, x] = np.nan_to_num(temp2[:, x])
    corr, sig = scipy.stats.pearsonr(temp1[:, x], temp2[:, x])
    corrData.append(corr)
    signData.append(sig)

print(np.array(corrData).shape)
data = data1.mean('time')
data.values = np.reshape(corrData, (ogShape[1], ogShape[2]))
fullDataset['sig'] = ((ogShape[1], ogShape[2]), np.reshape(signData, (ogShape[1], ogShape[2])))

ax = map(20, 9)
#ax.set_extent([220, 358, -20, 70], crs = ccrs.PlateCarree())
c = plt.contourf(data.lon, data.lat, data.values, cmap = cmap.tempAnoms3(), levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
h = plt.contourf(data.lon, data.lat, fullDataset['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))

for collection in h.collections:
    collection.set_edgecolor('#262626')
    collection.set_linewidth(0)

ax.set_title(f'ERSSTv5 Correlation with {numToMonth(indexMonth)} SSTs | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(dataMonth)}', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\correlationplot.png", dpi = 400, bbox_inches = 'tight')
plt.show()
