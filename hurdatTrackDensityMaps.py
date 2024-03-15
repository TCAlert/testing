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

# ens = pd.read_csv(r"C:\Users\deela\Downloads\ensoni - Sheet 1.csv")
# aso, ndj, y = ens['ASO'], ens['NDJ'], ens['Year']
# ninos = []
# ninas = []
# warmn = []
# cooln = []
# for x in range(len(aso)):
#     if aso[x] > 0.5 and ndj[x] > 0.5:
#         ninos.append(y[x])
#     elif aso[x] < -0.5 and ndj[x] < -0.5:
#         ninas.append(y[x])
#     elif (aso[x] > 0 and aso[x] < 0.5) and (ndj[x] > 0 and ndj[x] < 0.5):
#         warmn.append(y[x])
#     elif (aso[x] < 0 and aso[x] > -0.5) and (ndj[x] < 0 and ndj[x] > -0.5):
#         cooln.append(y[x])
# print('El Nino', ninos, '\nWarm Neutral', warmn, '\nCool Neutral', cooln, '\nLa Nina', ninas)

hyperactive = [1995, 1996, 1998, 1999, 2003, 2004, 2005, 2010, 2017, 2020]
belowNormal = [1991, 1993, 1994, 1997, 2002, 2009, 2013, 2014, 2015]
years =  [1995, 1998, 2005, 2010, 2020]#[1878, 1915, 1926, 1933, 1942, 1995, 1998, 2005, 2010, 2020]
months = ['08', '09', '10']
interval = 3
#dataType = 'RI'
dataType = 'track'
#dataType = '24hrChange'
#dataType = 'ACE'
#dataType = 'wind'

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
            stddev = std(climo)
            temp = (data.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time']))# / stddev
            monthlyData += temp
        allData.append(monthlyData)

    data = (np.array(allData)).mean(axis = 0)    
    s = 2
    data = gaussian_filter(data, sigma = s, truncate = (((interval - 1) / 2) - 0.5) / s)

    return data

data = xr.open_dataset(r"C:\Users\deela\Downloads\\" + dataType + "Density.nc")
lons = data['longitude']
lats = data['latitude']
data = data[f'{dataType}Density']

#data = getData(data, [2008,2020,1980,2005,2016,2011], months) 
data = getData(data, [1952,2012,2017,2001,2010,1998], months)

ax = map(interval * 2, 9)
ax.set_extent([-120, 0, 0, 60])
c = plt.contourf(lons, lats, data, cmap = cmap.tempAnoms(), levels = np.arange(-.125, .126, .001), extend = 'both')
#c = plt.pcolormesh(lons, lats, data, cmap = cmap.tempAnoms(), vmin = -0.1, vmax = 0.1)
ax.set_title(f'HURDAT2 {dataType.upper()} Density Anomaly\n30-Year Sliding Climatology', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'{numToMonth(int(month))} {years}', fontsize=9, loc='center') 
ax.set_title(f'ASO La Nina -NAO/+AMO', fontsize=9, loc='center') 
ax.set_title(f'{interval}\u00b0x{interval}\u00b0\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\hurdatDensity" + dataType + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()
