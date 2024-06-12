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
from correlationPCA import pcaSeries
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

udataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/pressure/uwnd.mon.mean.nc')
uData = udataset['uwnd'].sel(level = 850).fillna(0) * np.cos(np.radians(udataset['lat']))
uData = uData.fillna(0) * np.cos(np.radians(uData['lat']))
vdataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/pressure/vwnd.mon.mean.nc')
vData = vdataset['vwnd'].sel(level = 850).fillna(0) * np.cos(np.radians(vdataset['lat']))
vData = vData.fillna(0) * np.cos(np.radians(vData['lat']))
#csv = pd.read_csv(r"C:\Users\deela\Downloads\composites - " + index + ".csv")[numToMonth(indexMonth)[0:3]].iloc[16:]

print(uData, vData)

startYear = 1971
endYear = 2023
indexMonth = '12'
dataMonth = '8'
day = 365
index = f'ACE in Box (to day {day})'
lats = [0, 70]
lons = [-120, 0]
boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
csv = createClimoData([startYear, endYear], 'AL', lats, lons)
csv = csv[day]
print(csv)

# startYear = 1971
# endYear = 2020
# indexMonth = '9'
# dataMonth = '9'
# index = 'SSTAs in Box'
# lats = [-5, 5]
# lons = [300, 358]
# boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
# boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
# csv = timeseries(indexMonth, range(startYear, endYear + 1), slice(lats[1], lats[0]), slice(lons[0], lons[1]))[numToMonth(indexMonth)[0:3]]

# startYear = 1971
# endYear = 2023
# indexMonth = '4'
# dataMonth = '4'
# eofNum = 1
# index = f'EOF{eofNum} of Box'
# lats = [-20, 65]
# lons = [120, 360]
# boxXCoords = [lons[0] - 360, lons[1] - 360, lons[1] - 360, lons[0] - 360, lons[0] - 360]
# boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]
# csv = pcaSeries(startYear, endYear, lats, lons, indexMonth, eofNum)[numToMonth(indexMonth)[0:3]]

fMonths = np.array([np.datetime64(f'{y}-{str(dataMonth).zfill(2)}-01') for y in range(startYear, endYear + 1)])
uData = uData.sel(time = fMonths)
vData = vData.sel(time = fMonths)
ogShape = uData.shape

utemp = uData.values
utemp = np.reshape(utemp, (ogShape[0], ogShape[1] * ogShape[2]))
utemp = detrend(utemp, axis = 0)
vtemp = vData.values
vtemp = np.reshape(vtemp, (ogShape[0], ogShape[1] * ogShape[2]))
vtemp = detrend(vtemp, axis = 0)
print(utemp.shape, csv.shape)

ucorrData = []
usignData = []
for x in range(utemp.shape[1]):
    utemp[:, x] = np.nan_to_num(utemp[:, x])
    corr, sig = scipy.stats.pearsonr(utemp[:, x], csv)
    ucorrData.append(corr)
    usignData.append(sig)

print(np.array(ucorrData).shape)
uData = uData.mean('time')
uData.values = np.reshape(ucorrData, (ogShape[1], ogShape[2]))
udataset['sig'] = ((ogShape[1], ogShape[2]), np.reshape(usignData, (ogShape[1], ogShape[2])))

vcorrData = []
vsignData = []
for x in range(vtemp.shape[1]):
    vtemp[:, x] = np.nan_to_num(vtemp[:, x])
    corr, sig = scipy.stats.pearsonr(vtemp[:, x], csv)
    vcorrData.append(corr)
    vsignData.append(sig)

print(np.array(vcorrData).shape)
vData = vData.mean('time')
vData.values = np.reshape(vcorrData, (ogShape[1], ogShape[2]))
vdataset['sig'] = ((ogShape[1], ogShape[2]), np.reshape(vsignData, (ogShape[1], ogShape[2])))

mag = (uData**2 + vData**2)**0.5
ax = map(20, 9)
ax.set_extent([180, 359.9, -20, 75], crs = ccrs.PlateCarree())
c = plt.contourf(uData.lon, uData.lat, uData.values, cmap = cmap.tempAnoms3(), levels = np.arange(-1, 1.1, .1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))
#h = plt.contourf(uData.lon, uData.lat, dataset['sig'].values, colors = 'none', levels = np.arange(0, 0.06, 0.01), hatches = ['...'], transform = ccrs.PlateCarree(central_longitude = 0))
plt.quiver(uData.lon, vData.lat, uData.values, vData.values, transform = ccrs.PlateCarree(central_longitude = 0))

try:
    for y in range(len(boxXCoords)):
        try:
            print([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]])
            ax.plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'black', zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
        except:
            pass
except:
    pass

# for collection in h.collections:
#     collection.set_edgecolor('#262626')
#     collection.set_linewidth(0)

ax.set_title(f'NCEP/NCAR R1 850mb Vector Wind Correlation with {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'ERSSTv5 Correlation with {numToMonth(indexMonth)} {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'AMSU Tropopause (TTS) Brightness Temp. Correlation with {numToMonth(indexMonth)} {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'ERSSTv5 Correlation with {index} | All Data Detrended\nYears Used: {startYear}-{endYear}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(dataMonth)}', fontsize=9, loc='center') 
ax.set_title(f'Significant Values Hatched\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\correlationPlot" + dataMonth + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()
