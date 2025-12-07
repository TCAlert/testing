import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import pandas as pd 
import helper 
import matplotlib.patheffects as pe
import psl 
import hurdatParser 
import warnings
import cdsapi as cds
from scipy.ndimage import gaussian_filter
warnings.simplefilter(action='ignore', category=FutureWarning)
c = cds.Client()

def retrieve(type, level, date, lat, lon): 
    if "mean_sea_level_pressure" in type:
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type'  : 'reanalysis',
                'variable'      : type,
                'year'          : f'{date[0]}',
                'month'         : f'{date[1]}',
                'day'           : f'{date[2]}',
                'time'          : f'{date[3]}:00',
                'data_format'   : 'netcdf',                               # Supported format: grib and netcdf. Default: grib
                'area'          : [lat + 9, lon - 11, lat - 9, lon + 11], # North, West, South, East.          Default: global
            },
            r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.
    else:
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
                'data_format'   : 'netcdf',                               # Supported format: grib and netcdf. Default: grib
                'area'          : [lat + 9, lon - 11, lat - 9, lon + 11], # North, West, South, East.          Default: global
            },
            r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.


def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('longitude') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

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

def stationPlot(ax, lat, lon, u, v, slp = None, temp = None, dews = None):
    ax.barbs(lon, lat, u, v, fill_empty = True, length = 6, sizes=dict(emptybarb = 0.25), zorder = 15, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    for x in range(len(lon)):
        try:
            ax.text(lon.iloc[x] + 0.4, lat.iloc[x] + 0.2, round(int(slp.iloc[x]), 0), size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.75, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
            ax.text(lon.iloc[x] - 0.4, lat.iloc[x] + 0.2, round(int(temp.iloc[x]), 0), size=8, color='red', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.75, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
            ax.text(lon.iloc[x] - 0.4, lat.iloc[x] - 0.2, round(int(dews.iloc[x]), 0), size=8, color='green', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.75, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
        except:
            pass

def plot(data, year, month, day, hour, level = '1000', name = None, t = 'wind'):
    # print(hurdatParser.retrieveStorm(hurdatParser.database(), [name, str(year)]))
    stormData = hurdatParser.retrieveStorm(hurdatParser.database(), [name, str(year)])['Storm Data']
    stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
    lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    # lat, lon = 13.5, -24.	

    print(data[(data['YR'].astype(str) == year) & (data['MO'].astype(str) == month)])
    data = data[(data['YR'].astype(str) == year) & (data['MO'].astype(str) == month) & (data['DY'].astype(str) == day) & (data['HR'] == float(hour)) & (data['LAT'] > lat - 6) & (data['LAT'] < lat + 6) & (data['LON (W)'] > lon - 7.5) & (data['LON (W)'] < lon + 7.5)]
    print(data)
    windDir = data['D']
    windSpd = data['W (kts)']
    seaLevP = data['SLP']
    airTemp = data['AT']
    dewTemp = data['DPT']
    obsLats = data['LAT']
    obsLons = data['LON (W)']

    u, v, = helper.dirSpdToUV(270 - windDir, windSpd)

    labelsize = 8 
    ax = map(2, labelsize)   
    ax.set_extent([lon - 10, lon + 10, lat - 8, lat + 8])

    stationPlot(ax, obsLats, obsLons, u, v, seaLevP, airTemp, dewTemp)    
    ax.text(lon, lat, 'L', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))
    
    if t.lower() == 'wind':        
        retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        uwnd = (data['u']).squeeze()
        vwnd = (data['v']).squeeze()

        mag = (((uwnd.squeeze()).values)**2 + ((vwnd.squeeze()).values)**2)**0.5 * 1.94384
        c = ax.contourf(uwnd.longitude, vwnd.latitude, mag, levels = np.arange(0, 161, 1), cmap = cmap.wind2())
        ax.streamplot(uwnd.longitude - 180, vwnd.latitude, uwnd.values, vwnd.values, linewidth = 1, density = 1, color = '#404040', transform = ccrs.PlateCarree(central_longitude=180))
        title = f'{level}mb Wind Speed (kt)'
    elif t.lower() == 'temp':
        retrieve(['temperature', 'u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        temp = (data['t']).squeeze() - 273
        uwnd = (data['u']).squeeze()
        vwnd = (data['v']).squeeze()
        
        c = ax.contourf(temp.longitude, temp.latitude, temp, levels = np.arange(-80, 40.25, .25), cmap = cmap.tempC(), extend = 'both')
        ax.streamplot(uwnd.longitude - 180, vwnd.latitude, uwnd.values, vwnd.values, linewidth = 1, density = 1, color = '#404040', transform = ccrs.PlateCarree(central_longitude=180))
        title = f'{level}mb Air Temperature (C)'
    elif t.lower() == 'tempadv':
        retrieve(['temperature', 'u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        temp = (data['t']).squeeze()
        uwnd = (data['u']).squeeze()
        vwnd = (data['v']).squeeze()
        
        temp = temp - 273.15
        dx, dy = Gradient2D(temp)
        c = ax.contourf(dx.longitude, dy.latitude, (uwnd[1:, 1:] * dx + vwnd[1:, 1:] * dy) * -1, levels = np.arange(-10, 10.1, .1), cmap = cmap.tempAnoms(), extend = 'both')
        ax.streamplot(uwnd.longitude - 180, vwnd.latitude, uwnd.values, vwnd.values, linewidth = 1, density = 1, color = '#404040', transform = ccrs.PlateCarree(central_longitude=180))
        title = f'{level}mb Temperature Advection (C)'
    elif t.lower() == 'thetae':
        retrieve(['specific_humidity', 'temperature', 'u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        uData = (data['u']).squeeze()
        vData = (data['v']).squeeze()
        sphum = (data['q']).squeeze()
        tempe = (data['t']).squeeze()
        thetae = helper.thetae(tempe, level, 1000, sphum)
        
        c = ax.contourf(thetae.longitude, thetae.latitude, thetae, levels = np.arange(-40 + 273, 80.25 + 273, .25), cmap = cmap.tempC(), extend = 'both')
        ax.streamplot(uData.longitude, vData.latitude, uData.values, vData.values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
        title = f'{level}mb Theta-E (K)'
    elif t.lower() == 'divergence':
        retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        uData = (data['u']).squeeze()
        vData = (data['v']).squeeze()

        fxx, fxy = Gradient2D(uData * 1.94384)
        fyx, fyy = Gradient2D(vData * 1.94384)
        mag = fxx + fyy
        s = 3
        mag = gaussian_filter(mag, sigma = s)

        c = ax.contourf(fxx.longitude, fyy.latitude, mag, levels = np.arange(-25, 25.25, .25), cmap = cmap.tempAnoms(), extend = 'both')
        ax.streamplot(uData.longitude, vData.latitude, uData.values, vData.values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
        title = f'{level}mb Divergence (Smoothed)'
    elif t.lower() == 'mslp':
        retrieve(['mean_sea_level_pressure'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
        data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
        temp = (data['msl']).squeeze() / 100
        c = ax.contourf(temp.longitude, temp.latitude, temp, levels = np.arange(960, 1030.25, .25), extend = 'both', cmap = cmap.mw().reversed())
        f = ax.contour(temp.longitude, temp.latitude, temp, levels = np.arange(900, 1035, 5), linewidths = 1.5, colors = "black")
        ax.contour(temp.longitude, temp.latitude, temp, levels = np.arange(902.5, 1032.5, 5), linewidths = .75, colors = "black")
        plt.clabel(f, inline=1, fontsize=10, fmt='%1.0f')
        title = f'Mean Sea Level Pressure'

    plt.title(f'ICOADS Ship Observations\nDate: {str(year)}-{str(month).zfill(2)}-{str(day).zfill(2)} at {str(hour).zfill(2)}00z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'{str(name).upper()}', fontsize = labelsize + 1, loc = 'center')
    plt.title(f'Deelan Jariwala\nERA5 {title}', fontsize=labelsize + 1, loc='right')  
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    # plt.savefig(r"C:\Users\deela\Downloads\\al18\\" + name + title + str(year) + str(month).zfill(2) + str(day).zfill(2) + str(hour).zfill(2) + ".png", dpi = 400, bbox_inches = 'tight')
    plt.savefig(r"C:\Users\deela\Downloads\sandy1.png", dpi = 400, bbox_inches = 'tight')
    # plt.show()
    plt.close()

data = pd.read_csv(r"C:\Users\deela\Downloads\\AL181975 - data.csv")
# print(data)
# for x in list(np.arange(14, 18)):
#     for y in range(0, 24, 6):
#         year, month, day, hour = '1975', '10', str(x), y
#         level = 1000

#         try:
#             plot(data, year, month, day, hour, level, 'AL181975', 'wind')
#             print(year, month, day, hour, 'Wind done')
            # plot(data, year, month, day, hour, level, 'Alex', 'thetae')
            # print('Temp done')
            # plot(data, year, month, day, hour, level, 'UNNAMED', 'tempAdv')
            # print('Advection done')
            # plot(data, year, month, day, hour, level, 'UNNAMED', 'thetae')
            # print('Theta-E done')
            # plot(data, year, month, day, hour, level, 'Carmen', 'divergence')
            # print('Divergence done')
            # plot(data, year, month, day, hour, level, 'Unnamed', 'mslp')
            # print('mslp done')
        # plot(data, year, month, day, hour, level, 'UNNAMED', 'tempAdv')
        # print('Temp done')
            #print('Temperature done')
        # except Exception as e:
        #     print(e)
        #     pass

plot(data, 2012, 10, 27, 0, 850, 'Sandy', 'tempAdv')
