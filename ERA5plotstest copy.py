import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
import cdsapi as cds 
#import hurdatParser
import matplotlib.patheffects as pe
import helper 
import metpy.interpolate as interp
from scipy.ndimage import gaussian_filter

USAGE = '```$era5wind [date] [hour] [level] [name (if in HURDAT2) | coordinate]```'
labelsize = 8 
c = cds.Client()

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('lon') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

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
            'area'          : [50, 270, 0, 345], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

# Create a map using Cartopy
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

# Function to put together the whole plot
def staticstabilityPlot(month, day, year, hour, level, name):
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, hour)

    # Requests GFS zonal and meridional wind data 
    years = np.arange(1991, 2021, 1)
    datasets = []
    for year in years:
        retrieve(['temperature'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], 0, 0)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        datasets.append(data)
    data = xr.merge(datasets)
    print(data)
    temp1 = (data['t'].sel(level = level[0])).squeeze() - 273
    theta500 = helper.theta(temp1, level[0], 1000)
    temp2 = (data['t'].sel(level = level[1])).squeeze() - 273
    theta1000 = helper.theta(temp2, level[1], 1000)

    ss = theta500 - theta1000 / 500

    # Creates the plot
    ax = map(5, 9)
    #ax.set_extent([lon - 20, lon + 20, lat - 15, lat + 15], crs = ccrs.PlateCarree())
    
    c = ax.contourf(data.longitude, data.latitude, ss, levels = np.arange(-10, 0.025, .025), cmap = cmap.tempAnoms(), extend = 'both')
    #ax.text(lon, lat, 'X', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))

    ax.set_title(f'{level[0]}-{level[1]}mb Bulk Static Stability (dTheta/dp)\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    try:
        ax.set_title(f'{name.upper()}', fontsize = 10, loc = 'center')
    except:
        ax.set_title(f'Hurricane OTIS', fontsize = 10, loc = 'center')
    ax.set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.set_ticks(np.arange(-10, 1, 1))
    #plt.savefig(r"C:\Users\deela\Downloads\\" + str(date) + "T" + str(hour) + ".png", dpi = 200, bbox_inches = 'tight')    
    plt.show() 

# Function to put together the whole plot
def thetaePlot(month, day, year, hour, level, name):
    if type(name) == str:
        # Retrieve storm data from HURDAT2
        stormData = hurdatParser.retrieveStorm(database, [name, str(year)])['Storm Data']
        stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
        lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    else:
        lat, lon = name
    
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, hour)

    # Requests GFS zonal and meridional wind data 
    retrieve(['specific_humidity', 'temperature', 'u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
    uData = (data['u']).squeeze()
    vData = (data['v']).squeeze()
    sphum = (data['q']).squeeze()
    tempe = (data['t']).squeeze() - 273
    thetae = helper.thetae(tempe, level, 1000, sphum)

    #dx, dy = Gradient2D(thetae)
    #adv = (uData[1:, 1:] * dx + vData[1:, 1:] * dy) * -1

    # Creates the plot
    ax = map(5, 9)
    ax.set_extent([lon - 20, lon + 20, lat - 15, lat + 15], crs = ccrs.PlateCarree())
    
    c = ax.contourf(uData.longitude, vData.latitude, thetae, levels = np.arange(-2, 0.525, .025), cmap = 'twilight_shifted', extend = 'both')
    ax.streamplot(uData.longitude, vData.latitude, uData.values, vData.values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    #ax.text(lon, lat, 'X', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))

    ax.set_title(f'{level}mb Wind Streamlines and Theta-E (shading)\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    try:
        ax.set_title(f'{name.upper()}', fontsize = 10, loc = 'center')
    except:
        ax.set_title(f'Hurricane OTIS', fontsize = 10, loc = 'center')
    ax.set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.set_ticks(np.arange(-2, 0.75, .25))
    plt.savefig(r"C:\Users\deela\Downloads\\" + str(date) + "T" + str(hour) + ".png", dpi = 200, bbox_inches = 'tight')    
    plt.close() 

# Function to put together the whole plot
def windPlot(month, day, year, hour, level, name):
    if type(name) == str:
        # Retrieve storm data from HURDAT2
        stormData = hurdatParser.retrieveStorm(database, [name, str(year)])['Storm Data']
        print(stormData)
        stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
        lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    else:
        lat, lon = name
    
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, lat, lon)

    # Requests GFS zonal and meridional wind data 
    retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
    uData = (data['u']).squeeze()
    vData = (data['v']).squeeze()

    fxx, fxy = Gradient2D(uData * 1.94384)
    fyx, fyy = Gradient2D(vData * 1.94384)
    mag = fxx + fyy
    s = 3
    mag = gaussian_filter(mag, sigma = s)#, truncate = (((interval - 1) / 2) - 0.5) / s)

    # Creates the plot
    ax = map(5, 9)
    
    c = ax.contourf(fxx.longitude, fyy.latitude, mag, levels = np.arange(-25, 25.25, .25), cmap = cmap.tempAnoms(), extend = 'both')
    ax.streamplot(uData.longitude, vData.latitude, uData.values, vData.values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    ax.text(lon, lat, 'X', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))

    ax.set_title(f'{level}mb Wind Streamlines and Divergence (shading)\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    try:
        ax.set_title(f'{name.upper()}', fontsize = 10, loc = 'center')
    except:
        ax.set_title(f'{name}', fontsize = 10, loc = 'center')
    ax.set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\deela\Downloads\ERA5Wind.png", dpi = 200, bbox_inches = 'tight')    
    plt.show() 

staticstabilityPlot('8', '20', '2024', '03', 850, (14.08, -82.7))