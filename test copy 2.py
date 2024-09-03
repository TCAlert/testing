import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from helper import numToMonth
from matplotlib import rcParams
rcParams['font.family'] = 'Courier New'

def computeClimo(data, month, year):
    #if year - 30 < 1987:
    allYears = range(1987, 2024)
    #else:
    #    allYears = range(year - 30, year - 1)
    allYears = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in allYears]
    data = data.sel(time = allYears)

    return data

def map(interval, labelsize):
    fig = plt.figure(figsize=(14, 6))
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

dates = []
for x in range(1987, 2024):
    for y in range(1, 13):
        dates.append(np.datetime64(f'{x}-{str(y).zfill(2)}-01T00'))

dates = dates + [np.datetime64(f'2024-{str(y).zfill(2)}-01T00') for y in range(1, 6)]

dataset = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/cdr/mean_layer_temperature/amsu/rss/avrg/uat4_tb_v04r00_avrg_chtts_s198701_e202405_c20240615.nc')
print(dataset['brightness_temperature'])
dataset = dataset['brightness_temperature']
dataset = dataset.assign_coords(time = dates)

years = [2024]#1995, 1996, 1998, 1999, 2003, 2004, 2005, 2010, 2017, 2020]
month = '05'

allData = []
for year in years:
    climo = computeClimo(dataset, month, int(year))

    data = dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])

    globalMean = data.mean()
    allData.append((data).values)
allData = sum(allData) / len(allData)

ax = map(20, 9)
#ax.set_extent([-120, 0, 0, 60])
c = plt.contourf(dataset.longitude, dataset.latitude, allData, cmap = cmap.tempAnoms(), levels = np.arange(-2, 2.01, .01), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
ax.set_title(f'MSU/AMSU Tropopause (TTS) Brightness Temperature Anomalies\nClimatology: 1987-2023', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'{numToMonth(month)} {years}', fontsize=9, loc='center') 
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
cbar.set_ticks(np.arange(-2, 2.2, .4))
plt.savefig(r"C:\Users\deela\Downloads\amsutest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
