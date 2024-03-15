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
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.5
mpl.rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

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
    ax.grid(linestyle = '--', which = 'major', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    # ax.grid(linestyle = '--', which = 'minor', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    # ax.minorticks_on()
    return ax 

startYear = 1950
endYear = 2020
indexMonth = '12'
dataMonth = '12'
index = 'oni'
csv = pd.read_csv(r"C:\Users\deela\Downloads\composites - " + index + ".csv")[numToMonth(indexMonth)[0:3]]
dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
data = dataset['sst']

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
data = data.sel(time = fMonths)
ogShape = data.shape

temp = data.values
temp = np.reshape(temp, (ogShape[0], ogShape[1] * ogShape[2]))
print(temp.shape, csv.shape)

corrData = []
signData = []
for x in range(temp.shape[1]):
    #corr = np.corrcoef(temp[:, x], csv)
    temp[:, x] = np.nan_to_num(temp[:, x])
    corr, sig = scipy.stats.pearsonr(temp[:, x], csv)
    corrData.append(corr)
    signData.append(sig)

print(np.array(corrData).shape)
data = data.mean('time')
data.values = np.reshape(corrData, (ogShape[1], ogShape[2]))
dataset['sig'] = ((ogShape[1], ogShape[2]), np.reshape(signData, (ogShape[1], ogShape[2])))
#stiples = np.where(dataset['sig'].values <= 0.05, dataset['sig'].values, 0)
#print(stiples.shape)

ax = map(20, 9)
#ax.set_extent([-110, -0.01, 0, 70])
c = plt.contourf(data.lon, data.lat, data.values, cmap = 'RdBu_r', levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
h = plt.contourf(data.lon, data.lat, dataset['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))

for collection in h.collections:
    collection.set_edgecolor('#262626')
    collection.set_linewidth(0)

ax.set_title(f'ERSSTv5 Correlation with {numToMonth(indexMonth)} {index.upper()}\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(dataMonth)}', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\corrtest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
