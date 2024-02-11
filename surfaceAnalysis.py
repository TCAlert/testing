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

def plot(data, year, month, day, hour, name = None):
    stormData = hurdatParser.retrieveStorm(hurdatParser.database(), [name, str(year)])['Storm Data']
    stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
    lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    print(lat, lon)

    data = data[(data['YR'] == year) & (data['MO'] == month) & (data['DY'] == day) & (data['HR'] == hour) & (data['LAT'] > lat - 6) & (data['LAT'] < lat + 6) & (data['LON (W)'] > lon - 7.5) & (data['LON (W)'] < lon + 7.5)]
    windDir = data['D']
    windSpd = data['W (kts)']
    seaLevP = data['SLP']
    airTemp = data['AT']
    dewTemp = data['DPT']
    obsLats = data['LAT']
    obsLons = data['LON (W)']

    u, v, = helper.dirSpdToUV(270 - windDir, windSpd)

    labelsize = 8 
    ax = map(1, labelsize)   
    ax.set_extent([lon - 10, lon + 10, lat - 8, lat + 8])

    stationPlot(ax, obsLats, obsLons, u, v, seaLevP, airTemp, dewTemp)    
    ax.text(lon, lat, 'L', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))
    
    level = '200'
    uwnd, vwnd = psl.getHourlyData(year, month, day, hour, 'uwnd', level), psl.getHourlyData(year, month, day, hour, 'vwnd', level)#, psl.getHourlyData(year, month, day, hour, 'slp', 'surface') / 100
    mag = (((uwnd.squeeze()).values)**2 + ((vwnd.squeeze()).values)**2)**0.5 * 1.94384

    c = ax.contourf(uwnd.lon, vwnd.lat, mag, levels = np.arange(0, 161, 1), cmap = cmap.wind2())
    #s = ax.contour(slp.lon, slp.lat, slp.values, alpha = 0.5, colors = ['black'], levels = np.arange(900, 1100, 4))
    #ax.clabel(s, inline=True)
    
    ax.streamplot(uwnd.lon - 180, vwnd.lat, uwnd.values, vwnd.values, linewidth = 1, density = 1, color = '#404040', transform = ccrs.PlateCarree(central_longitude=180))
    plt.title(f'ICOADS Ship Observations (Winds and SLP Plotted)\nDate: {str(year)}-{str(month).zfill(2)}-{str(day).zfill(2)} at {str(hour).zfill(2)}00z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'{str(name).upper()}', fontsize = labelsize + 1, loc = 'center')
    plt.title(f'Deelan Jariwala\nNCEP/NCAR R1 {level}mb Wind Speed (kt)', fontsize=labelsize + 1, loc='right')  
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\sfcMap.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

data = pd.read_csv(r"C:\Users\deela\Downloads\GILDA ICOADS Set #2 - ICOADS_R3.0_Rqst717076_19731023-19731027.csv")

plot(data, 1973, 10, 25, 18, 'Gilda')