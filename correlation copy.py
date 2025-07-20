import xarray as xr 
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cartopy
import numpy as np 
import cmaps as cmap 
import pandas as pd 
from helper import numToMonth
import scipy.stats
from scipy.signal import detrend
import matplotlib as mpl
from ersstTimeseriesGenerator import timeseries 
from regionalACE import createClimoData
from correlationPCA import pcaSeries
import psl
import helper
from scipy.ndimage import gaussian_filter
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

def yearlySum(data):
    values = data.values
    values = values.reshape(int(values.shape[0] / 12), 12, 71, 181)
    values = np.sum(values, axis = 1)

    data = data.resample(time = 'AS').mean()
    data.values = values

    return data

def getIndex(ts = False, ACEbox = False, SSTAbox = False, EOFbox = False, **kwargs):
    if ts == True: 
        # index = 'Zach_Residuals'
        # indexMonth = '12'
        # dataMonth = '6'
        # startYear = 1980
        # endYear = 2024
        print(startYear, endYear)
        csv = pd.read_csv(r"C:\Users\deela\Downloads\composites - " + index + ".csv")
        csv = csv[(csv['Year'] >= startYear) & (csv['Year'] <= endYear)]
        print(csv)
        csv = csv[numToMonth(indexMonth)[0:3]]
    elif ACEbox == True:
        # startYear = 1971
        # endYear = 2023
        # indexMonth = '8'
        # dataMonth = '8'
        # day = 365
        # day2 = 233
        # index = f'ACE in Box (to day {day})'
        # lats = [0, 70]
        # lons = [-120, -1]
        boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
        boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
        csv = createClimoData([startYear, endYear], 'AL', lats, [lons[0] - 360, lons[1] - 360])
        print(csv)
        try:
            csv = csv[day] - csv[day2]
        except:
            csv = csv[day]
    elif SSTAbox == True:
        # startYear = 1971
        # endYear = 2020
        # indexMonth = '7'
        # dataMonth = '7'
        # index = 'SSTAs in Box'
        # lats = [40, 60]
        # lons = [360-70, 360-35]
        boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
        boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
        csv = timeseries(indexMonth, range(startYear, endYear + 1), slice(lats[1], lats[0]), slice(lons[0], lons[1]))[numToMonth(indexMonth)[0:3]]
    elif EOFbox == True:
        # startYear = 1971
        # endYear = 2023
        # indexMonth = '9'
        # dataMonth = '9'
        # eofNum = 2
        # index = f'EOF{eofNum} of Box'
        # lats = [0, 70]
        # lons = [280, 360]
        boxXCoords = [lons[0] - 360, lons[1] - 360, lons[1] - 360, lons[0] - 360, lons[0] - 360]
        boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
        csv = pcaSeries(startYear, endYear, lats, lons, indexMonth, eofNum)[numToMonth(indexMonth)[0:3]]
    
    return csv

# dataset1 = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/pressure/hgt.mon.mean.nc')
# dataset1 = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/spectral/chi.mon.mean.nc')
# dataset = dataset1['chi'].sel(level = .2101).fillna(0)
# data = dataset * np.cos(np.radians(dataset['lat']))
# print(data)
# dataset = psl.createClimoMonthly([1971, 2023], '8', ['air', 'shum'], ['Pressure', 'Pressure'], False)
# dataset = helper.thetae(dataset[0].sel(level = 850) + 273.15, 850, 1000, dataset[1].sel(level = 850) / 1000)
dataset1 = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
dataset = dataset1['sst']
# print(dataset)
# dates = []
# for x in range(1987, 2024):
#     for y in range(1, 13):
#         dates.append(np.datetime64(f'{x}-{str(y).zfill(2)}-01T00'))

# dataset = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/cdr/mean_layer_temperature/amsu/rss/avrg/uat4_tb_v04r00_avrg_chtts_s198701_e202402_c20240314.nc')
# data = dataset['brightness_temperature'].isel(time = slice(0, 444))
# data = data.rename({'latitude' : 'lat', 'longitude' : 'lon'})
# data = data.assign_coords(time = dates)
data = dataset.fillna(0) * np.cos(np.radians(dataset['lat']))
#dataset = xr.open_dataset(r"C:\Users\deela\Downloads\R1CI1971-2023.nc")
#data = dataset['__xarray_dataarray_variable__'].fillna(0) * np.cos(np.radians(dataset['lat']))

# dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityALL2025.nc")
# dataset = dataset1['ACE']
# data = dataset * np.cos(np.deg2rad(dataset['latitude']))
# print(data.shape)
# data = yearlySum(data)
# data = data.coarsen(latitude=2, longitude=2, boundary='trim').mean()

# s = 3
# data.values = gaussian_filter(data.values, sigma = s, axes = (1, 2))
# print(data)

index = 'ACE in Box (1995-2024)'
dataMonth = '8'
indexMonth = '6'
startYear = 1995
endYear = 2024
day = 365
lats = [0, 70]
lons = [360 - 100, 360 - 5]
boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
csv1 = getIndex(ACEbox = True, day = day, lats = lats, lons = lons, startYear = startYear, endYear = endYear)

# lats = [10, 20]
# csv2 = getIndex(ts = False, ACEbox = True, dataMonth = dataMonth, day = day, startYear = startYear, endYear = endYear, lats = lats, lons = lons)
csv = csv1# - csv2
print(csv)

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
print(fMonths)
data = data.sel(time = fMonths)
print(data)
ogShape = data.shape

temp = data.values
temp = np.reshape(temp, (ogShape[0], ogShape[1] * ogShape[2]))
temp = detrend(temp, axis = 0)
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
dataset1['sig'] = ((ogShape[1], ogShape[2]), np.reshape(signData, (ogShape[1], ogShape[2])))

ax = map(20, 9)
# ax.set_extent([180, 359.9, 0, 70], crs = ccrs.PlateCarree())
try:
    c = plt.contourf(data.longitude, data.latitude, data.values, cmap = cmap.tempAnoms3(), levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
    # c = plt.pcolormesh(data.longitude, data.latitude, data.values, cmap = cmap.tempAnoms3(), vmin = -1, vmax = 1.1, transform = ccrs.PlateCarree(central_longitude = 0))
    h = plt.contourf(data.longitude, data.latitude, dataset1['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))
except:
    c = plt.contourf(data.lon, data.lat, data.values, cmap = cmap.tempAnoms3(), levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
    # c = plt.pcolormesh(data.lon, data.lat, data.values, cmap = cmap.tempAnoms3().reversed(), vmin = -1, vmax = 1.1, transform = ccrs.PlateCarree(central_longitude = 0))
    h = plt.contourf(data.lon, data.lat, dataset1['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))

try:
    for y in range(len(boxXCoords)):
        try:
            print([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]])
            ax.plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'black', zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
        except:
            pass
except:
    pass

try:
    for collection in h.collections:
        collection.set_edgecolor('#262626')
        collection.set_linewidth(0)
except:
    pass

# ax.set_title(f'NCEP/NCAR R1 .2101 Velocity Potential Correlation with {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'ERSSTv5 Correlation with {numToMonth(indexMonth)} {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'AMSU Tropopause (TTS) Brightness Temp. Correlation with {numToMonth(indexMonth)} {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
# ax.set_title(f'ERSSTv5 Correlation with {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
# ax.set_title(f'HURDAT2 ACE Density Correlation with {numToMonth(indexMonth)} {index.upper()}\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(dataMonth)}', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\correlationPlot" + dataMonth + "_" + index + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()