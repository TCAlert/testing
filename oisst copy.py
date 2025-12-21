import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import xarray as xr
import bdeck as bdeck 
from matplotlib import cm
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from helper import REGIONS, gridlines 
import cmaps as cmap 

# Plot data
def stormCenteredOISST(storm, time):
    fig = plt.figure(figsize=(25, 7))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder = 21)
    ax.add_feature(cartopy.feature.BORDERS.with_scale('10m'), edgecolor='black', linewidth=0.5, zorder = 25) 
    ax.add_feature(cartopy.feature.LAND.with_scale('10m'))
    ax = gridlines(ax, 5)

    try:
        (int(storm[2:]) > 0) == True
        lat, lon = bdeck.latlon(storm.lower())
        extent = [lon - 15, lon + 15, lat - 15, lat + 15]
        ax.set_extent(extent, crs = ccrs.PlateCarree())
        plt.scatter(lon, lat, color = 'white', facecolor = None, marker = '$\\mathrm{L}$', s = 700, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))
        plt.scatter(lon, lat, color = 'black', facecolor = None, marker = '$\\mathrm{L}$', s = 600, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))
        contour = 0.5
    except:
        extent = REGIONS[storm.upper()][0]
        ax.set_extent(extent, crs = ccrs.PlateCarree())
        contour = 1

    file = xr.open_dataset(f"http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{time[0:4]}.nc")
    data = file['sst'].sel(time = time, lat = slice(extent[2], extent[3]), lon = slice(360 + extent[0], 360 + extent[1]))
    print(data)

    time = (str(time).split('T'))

    plt.contour(data.lon, data.lat, data.values, levels = [26], colors = 'black', linewidths = 1.5, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contour(data.lon, data.lat, data.values, levels = np.arange(0, 33, contour), colors = 'black', linewidths = 0.25, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contourf(data.lon, data.lat, data.values, levels = np.arange(0, 33, contour), cmap= cmap.sst(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)

    plt.title(f'OISSTv2.1 Sea Surface Temperature (\u00b0C), 26C Isotherm Outlined\nDate: {time[0]}', fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{storm.upper()}\nDeelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\stormcenteredoisst.png", dpi = 300, bbox_inches = 'tight')
    plt.show()
    plt.close()
stormCenteredOISST('car', '2025-10-26T00')
