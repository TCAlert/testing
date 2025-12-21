import xarray as xr
import matplotlib.pyplot as plt
import satcmaps as cmaps 
import numpy as np 
from matplotlib import rcParams 
import cartopy, cartopy.crs as ccrs 
import bdeck as bdeck 
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
from helper import thetae
import cmaps 

def makeMap(figsize, interval = 5, center = 0):
    labelsize = 8
    fig = plt.figure(figsize = figsize)

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude = center))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = '#cccccc', linewidth = 0.5, zorder = 12)
    # ax.set_extent(extent, crs=ccrs.PlateCarree())

    return ax

lat, lon = 18.2, 360-77.9
time = np.datetime64('2025-10-28T18')
dist = 10

udata = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis/surface_gauss/uwnd.10m.gauss.2025.nc')
vdata = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis/surface_gauss/vwnd.10m.gauss.2025.nc')

print(udata)

uwnd = udata['uwnd'].sel(lat = slice(lat + dist, lat - dist), lon = slice(lon - dist, lon + dist), time = time) * 1.94384
vwnd = vdata['vwnd'].sel(lat = slice(lat + dist, lat - dist), lon = slice(lon - dist, lon + dist), time = time) * 1.94384
wspd = (uwnd**2 + vwnd**2)**0.5
plt.contourf(wspd.lon, wspd.lat, wspd.values, vmin = 0, vmax = 160, cmap = cmaps.wind())
plt.show()