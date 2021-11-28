import datetime as dt
from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr
from siphon.catalog import TDSCatalog
import xarray as xr 
import bdeck as bdeck 
from matplotlib import cm
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import basins as ba

usage = f'```$cyoi [basin/storm]\nAvailable Basins - {str(list(ba.func_map.keys()))}```'

def cmap():
    top = cm.get_cmap('BuPu_r', 128)
    bottom = cm.get_cmap('Reds', 32)

    newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                       bottom(np.linspace(0, 1, 32))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def stormCenteredOISST(storm):
    fig = plt.figure(figsize=(25, 7))

    file = xr.open_dataset("https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.2021.v2.nc")
    latest = file['time'][-1]
    data = file['sst'].sel(time = latest)

    # Use the Geostationary projection in cartopy
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    try:
        (int(storm[2:]) > 0) == True
        lat, lon = bdeck.latlon(storm.lower())
        ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs = ccrs.PlateCarree())
        plt.scatter(lon, lat, color = 'white', facecolor = None, marker = '$\\mathrm{L}$', s = 700, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))
        plt.scatter(lon, lat, color = 'black', facecolor = None, marker = '$\\mathrm{L}$', s = 600, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))
        contour = 0.5
    except:
        ax.set_extent(ba.func_map[storm](), crs = ccrs.PlateCarree())
        contour = 1

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder = 97)
    ax.add_feature(cartopy.feature.BORDERS.with_scale('10m'), edgecolor='black', facecolor=cartopy.feature.COLORS['land'], linewidth=0.5, zorder = 99) 
    #ax.add_feature(cartopy.feature.STATES.with_scale('10m'), edgecolor = 'black', linewidth = 0.1, zorder = 98)
    ax.add_feature(cartopy.feature.LAND.with_scale('10m'), zorder = 96)
    if (storm.lower() == 'npac' or storm.lower() == 'enso' or storm.lower() == 'pacific' or storm.lower() == 'spac' or storm.lower() == 'wpac'):
        pass
    else:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 0.5, color='gray', alpha=0.5, linestyle='--', zorder = 100)  
        gl.xlabels_top = gl.ylabels_right = False

    time = (str(latest.values).split('T'))

    plt.contour(data.lon, data.lat, data.values, levels = [26], colors = 'black', linewidths = 1.5, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contour(data.lon, data.lat, data.values, levels = np.arange(0, 33, contour), colors = 'black', linewidths = 0.25, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contourf(data.lon, data.lat, data.values, levels = np.arange(0, 33, contour), cmap= cmap(), transform=ccrs.PlateCarree(central_longitude=0))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)

    plt.title(f'OISST SST ({time[0]}) - {storm.upper()}\n26C Isotherm Outlined', fontweight='bold', fontsize=10, loc='left')
    plt.title('TCAlert\nCredit to guyph#0609 & CyclonicWx for CMap', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\Jariwala\Downloads\stormcenteredoisst.png", dpi = 300, bbox_inches = 'tight')
    #plt.show()
    plt.close()
#stormCenteredOISST("globe")