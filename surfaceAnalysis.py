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
import cdsapi as cds 

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
            'area'          : [lat + 6, lon - 7.5, lat - 6, lon + 7.5], # North, West, South, East.          Default: global
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

def stationPlot(ax, lat, lon, u, v, slp = None, temp = None):
    ax.barbs(lon, lat, u, v, fill_empty = True, length = 6, sizes=dict(emptybarb = 0.25), zorder = 15)
    for x in range(len(lon)):
        try:
            ax.text(lon.iloc[x] - 0.2, lat.iloc[x] - 0.1, round(int(slp.iloc[x]), 0), size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
        except:
            pass

def plot(data, year, month, day, hour, lat, lon, name = None):
    data = data[(data['YR'] == year) & (data['MO'] == month) & (data['DY'] == day) & (data['HR'] == hour) & (data['LAT'] > lat - 6) & (data['LAT'] < lat + 6) & (data['LON (W)'] > lon - 7.5) & (data['LON (W)'] < lon + 7.5)]
    windDir = data['D']
    windSpd = data['W (kts)']
    seaLevP = data['SLP']
    obsLats = data['LAT']
    obsLons = data['LON (W)']

    u, v, = helper.dirSpdToUV(270 - windDir, windSpd)

    labelsize = 8 
    ax = map(1, labelsize)   
    stationPlot(ax, obsLats, obsLons, u, v, seaLevP)
    
    ax.set_extent([lon - 7.5, lon + 7.5, lat - 6, lat + 6])
    ax.text(lon, lat, 'L', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))
    
    retrieve(['temperature', 'u_component_of_wind', 'v_component_of_wind',], [1000], [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    era5Data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
    #temp = ((era5Data['t'].squeeze() - 273.15) * (9/5)) + 32
    #c = ax.contourf(temp.longitude, temp.latitude, temp.values, levels = np.arange(-100, 101, 1), cmap = cmap.temperature())
    mag = (((era5Data['u'].squeeze()).values)**2 + ((era5Data['v'].squeeze()).values)**2)**0.5 * 1.94384
    c = ax.contourf(era5Data.longitude, era5Data.latitude, mag, levels = np.arange(0, 161, 1), cmap = cmap.wind2())

    plt.title(f'ICOADS Ship Observations (Winds and SLP Plotted)\nDate: {str(year)}-{str(month).zfill(2)}-{str(day).zfill(2)} at {str(hour).zfill(2)}00z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'{str(name).upper()}', fontsize = labelsize + 1, loc = 'center')
    plt.title('Deelan Jariwala\nERA5 1000mb Wind Speed (kt)', fontsize=labelsize + 1, loc='right')  
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\sfcMap.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

data = pd.read_csv(r"C:\Users\deela\Downloads\GILDA ICOADS Set #1 - ICOADS_R3.0_Rqst717075_19731015-19731022.csv")

plot(data, 1973, 10, 22, 18, 25.6, -75.7, 'Gilda')