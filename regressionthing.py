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
from regionalACE import createClimoData
from sklearn.linear_model import LinearRegression 

mpl.rcParams['hatch.linewidth'] = 0.5
mpl.rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 4))

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

# dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/pressure/uwnd.mon.mean.nc')
# data = dataset['uwnd'].sel(level = 850).fillna(0) * np.cos(np.radians(dataset['lat']))
dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
data = dataset['sst'].sel(lat = slice(50, -50))
data = data.fillna(0) * np.cos(np.radians(data['lat']))
print(data)

startYear = 1971
endYear = 1997
indexMonth = '12'
dataMonth = '4'
day = 365
index = f'ACE in Box (to day {day})'
lats = [0, 90]
lons = [-120, 0]
csv = createClimoData([startYear, endYear - 1], 'AL', lats, lons)[day].to_numpy()
print(csv)

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
data = data.sel(time = fMonths)
data = data - data.sel(time = fMonths[:-1]).mean('time')

print(data)
ogShape = data.shape

temp = data.values
temp = np.reshape(temp, (ogShape[0], ogShape[1] * ogShape[2]))
temp = detrend(temp, axis = 0)
print(temp.shape, csv.shape)
year = temp[-1].reshape(1, ogShape[1] * ogShape[2])
temp = temp[:-1]
print(temp.shape, year.shape, csv.shape)

corrData = []
signData = []
for x in range(temp.shape[1]):
    temp[:, x] = np.nan_to_num(temp[:, x])
    model = LinearRegression().fit(temp[:, x].reshape(-1, 1), csv)
    corrData.append(model.predict([year[:, x]]))

corrData = np.array(corrData)
print(np.array(corrData).mean(), np.array(corrData).sum(), np.nanmax(corrData), np.nanmin(corrData))
#corrData = (corrData - np.nanmin(corrData)) / (np.nanmax(corrData) - np.nanmin(corrData))
data = data.mean('time')
data.values = np.reshape(corrData, (ogShape[1], ogShape[2]))

ax = map(20, 9)
#ax.set_extent([205, 355, -15, 55], crs = ccrs.PlateCarree())
c = plt.contourf(data.lon, data.lat, data.values, cmap = cmap.tempAnoms(), levels = np.arange(0, 200, 1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))

ax.set_title(f'How Much ACE Does a Linear Regression Here Yield?\nYears Used: {startYear}-{endYear - 1}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(dataMonth)} {endYear}', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\correlationPlot" + dataMonth + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()
