import numpy as np
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import cmaps as cmap 
import xarray as xr 
from helper import numToMonth
from scipy.ndimage import gaussian_filter
from matplotlib import rcParams
import pandas as pd 
rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
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

def computeClimo(data, month, year):
    if year - 30 < 1851:
        allYears = range(1851, 1880)
    else:
        allYears = range(year - 30, year - 1)
    allYears = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in allYears]
    data = data.sel(time = allYears)

    return data

def std(dataset):
    print(dataset)
    dev = []
    average = np.mean(dataset, axis = 0)
    for x in range(len(dataset)):
        temp = dataset[x]
        dev.append((average - temp)**2)
    stddev = np.sqrt(np.mean(dev, axis = 0))

    return stddev

def getData(data, years, months):
    allData = []
    for year in years:
        monthlyData = 0
        for month in months:
            climo = computeClimo(data, month, int(year))
            #stddev = np.std(climo, axis = 0)
            temp = (data.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time']))# / stddev
            temp = np.nan_to_num(temp)
            monthlyData += temp
        allData.append(monthlyData)

    data = (np.array(allData)).mean(axis = 0)  
    # plt.imshow(data, vmin = -.5, vmax = .5, origin = 'lower', cmap = 'RdBu_r')  
    # plt.show() 
    print(np.nanmax(data))
    s = 3
    data = gaussian_filter(data, sigma = s)
    # plt.imshow(data, vmin = -.5, vmax = .5, origin = 'lower', cmap = 'RdBu_r') 
    # plt.show() 
    return data

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
interval = 1
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityEPAC.nc")
RI = dataset['RI']
track = dataset['track']
change = dataset['24hrChange']
ACE = dataset['ACE']
wind = dataset['wind']
print('HURDAT density data loaded.')

usage = '```$density [dataType: track, RI, ACE, 24hrchange, wind] [year]```'

def makePlot(years, dataType = 'track'):
    if dataType.lower() == 'track':
        data = track
        vmin, vmax = -0.5, 0.5
    elif dataType.lower() == 'ri':
        data = RI
        vmin, vmax = -0.1, 0.1
    elif dataType.lower() == '24hrchange':
        data = change
        vmin, vmax = -2, 2
    elif dataType.lower() == 'ace':
        data = ACE
        vmin, vmax = -0.25, 0.25
    elif dataType.lower() == 'wind':
        data = wind
        vmin, vmax = -25, 25
    
    lons = data['longitude']
    lats = data['latitude']
    data = getData(data, years, months)

    ax = map(5, 9)
    ax.set_extent([-177.5, -82.5, 2.5, 67.5], crs = ccrs.PlateCarree())
    c = ax.contourf(lons, lats, data, cmap = cmap.tempAnoms(), levels = np.arange(vmin, vmax + ((vmax - vmin) / 200), (vmax - vmin) / 200), extend = 'both', transform = ccrs.PlateCarree())
    ax.set_title(f'HURDAT2 {dataType.upper()} Density Anomaly\n30-Year Sliding Climatology', fontweight='bold', fontsize=9, loc='left')
    ax.set_title(f'Full Year {years}', fontsize=9, loc='center') 
    ax.set_title(f'{interval}\u00b0x{interval}\u00b0\nDeelan Jariwala', fontsize=9, loc='right') 
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
    cbar.set_ticks(np.arange(vmin, vmax + ((vmax - vmin) / 20), (vmax - vmin) / 10))
    plt.savefig(r"C:\Users\deela\Downloads\hurdatDensityPlot.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

makePlot([2010, 2020, 2008, 2022, 2021, 1995, 2017], 'ACE')