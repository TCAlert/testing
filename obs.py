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
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor = '#242424')
    ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor = '#242424')
    ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor = '#242424')
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'dimgray', linewidth = 0.5, zorder = 9)

    return ax 

def stationPlot(ax, lat, lon, u, v, slp = None, temp = None, dews = None):
    ax.barbs(lon, lat, u, v, fill_empty = True, length = 6, sizes=dict(emptybarb = 0.1), zorder = 15, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    ax.scatter(lon, lat, s = 20, c = 'black', zorder = 16, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    for x in range(len(lon)):
        try:
            ax.text(lon.iloc[x] + 0.12, lat.iloc[x] + 0.08, round(int(slp.iloc[x]), 0), size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
            ax.text(lon.iloc[x] - 0.12, lat.iloc[x] + 0.08, round(int(temp.iloc[x]), 0), size=8, color='red', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
            ax.text(lon.iloc[x] - 0.12, lat.iloc[x] - 0.08, round(int(dews.iloc[x]), 0), size=8, color='green', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), zorder = 16)
        except:
            pass

def plot(lat, lon):
    data = pd.read_csv("https://aviationweather.gov/data/cache/metars.cache.csv", skiprows = 5)

    data = data[(data['latitude'] > lat - 2.5) & (data['latitude'] < lat + 2.5) & (data['longitude'] > lon - 2.5) & (data['longitude'] < lon + 2.5)]
    windDir = data['wind_dir_degrees']
    windDir = pd.to_numeric(windDir, errors='coerce').fillna(0)
    windSpd = data['wind_speed_kt'].astype(float)
    seaLevP = data['sea_level_pressure_mb'].astype(float)
    altimhg = data['altim_in_hg'].astype(float) * 33.864
    seaLevP = seaLevP.fillna(altimhg)
    airTemp = data['temp_c'].astype(float)
    dewTemp = data['dewpoint_c'].astype(float)
    obsLats = data['latitude'].astype(float)
    obsLons = data['longitude'].astype(float)

    u, v, = helper.dirSpdToUV(270 - windDir, windSpd)

    labelsize = 8 
    ax = map(.5, labelsize)   
    ax.set_extent([lon - 2.5, lon + 2.5, lat - 2.5, lat + 2.5])

    stationPlot(ax, obsLats, obsLons, u, v, seaLevP, airTemp, dewTemp)    
    
    plt.title(f'METAR Surface Observations\nLast Updated: {data["observation_time"].iloc[0]}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\obs.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

plot(40, -75)