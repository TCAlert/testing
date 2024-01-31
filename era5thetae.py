import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import cdsapi as cds
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import xarray as xr 
import satcmaps as scmaps 
import helper 
import matplotlib.ticker as mticker

c = cds.Client()

def retrieve(type, level, date, lat, lon): 
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type'  : 'reanalysis',
            'variable'      : type,
            'pressure_level': level,
            'year'          : f'{date[0]}',
            'month'         : f'{date[1]}',
            'day'           : f'{date[2]}',
            'time'          : f'{date[3]}:00',
            'format'        : 'netcdf',                 # Supported format: grib and netcdf. Default: grib
            'area'          : [lat + 20, lon - 20, lat - 20, lon + 20], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

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

def chart(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.set_yscale('log')
    ax.invert_yaxis()
    
    # Add state boundaries to plot
    ax.set_xticks(np.arange(-180, 181, interval))
    ax.set_yticks(np.arange(100, 1100, 100))
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='y')
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

labelsize = 8 
year = 2017
month = 9
day = 5
hour = 18
levels = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
lat, lon = 16.9, -59.2
date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
retrieve(['specific_humidity', 'temperature', 'u_component_of_wind', 'v_component_of_wind'], levels, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
thetaeDataset = []
for x in range(len(levels)):
    tempData = data.sel(level = levels[x])
    thetaeDataset.append(helper.thetae(tempData['t'].squeeze(), levels[x], 1000, tempData['q'].squeeze()))
thetae = xr.concat(thetaeDataset, dim = 'level')

#for x in range(len(levels)):
#    ax = map(5, labelsize)
#    temp = thetae.sel(level = levels[x])
#    c = plt.contourf(temp.longitude, temp.latitude, temp.values - temp.mean(['longitude', 'latitude']).values, cmap = cmap.tempAnoms(), levels = np.arange(-20, 21, 1))
#    plt.streamplot(data['u'].longitude, data['v'].latitude, (data['u'].sel(level = levels[x])).squeeze(), (data['v'].sel(level = levels[x])).squeeze(), linewidth = 1, density = 1, color = 'black')
#    plt.title(f'{levels[x]}mb Theta-E')
#    plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
#    print('This works')
#plt.show()

mean = thetae.mean(['latitude', 'longitude'])
thetae = thetae.sel(latitude = lat).squeeze()
print(thetae)

ax = chart(5, labelsize)
print(data['w'])
c = plt.contourf(data['t'].longitude, data['t'].level, thetae - mean, cmap = cmap.tempAnoms(), levels = np.arange(-20, 21, 1), extend = 'both')
plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)

ax.set_title(f'ERA5: Equivalent Potential Temperature Anomaly from 20x20 Box\nDate: {date} at {hour}00z', fontweight='bold', fontsize=10, loc='left')
ax.set_title(f'Zonal Cross Section Centered at {lat}N, {lon * -1}W', fontsize = 10, loc = 'center')
ax.set_title('Deelan Jariwala', fontsize=10, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\gfstest.png", dpi = 400, bbox_inches = 'tight')
plt.show()