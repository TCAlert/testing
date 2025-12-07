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

data = xr.open_mfdataset(r"C:\Users\deela\Downloads\melissa_20251028U1.nc")
print(data, list(data.variables))

lat = data['LAT']
lon = data['LON']
tmp = data['TA'] + 273.15
dpt = data['TD'] + 273.15
prs = data['CSP']
slp = data['SLP']
vvl = data['V']

thte = thetae(tmp, prs, 1000, dpt, dew = True)

ax = makeMap((18, 9), interval = .05)
ax.set_extent([-78.30, -77.80, 17.30, 17.80])

ax.set_title(f'Hurricane Melissa USAF Mission 20251028U1\nFlight Level Theta-E (K)', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right')

c = ax.scatter(lon, lat, c = thte, cmap = cmaps.probs4(), vmin = 350, vmax = 370, zorder = 15)
ax.plot(lon, lat, color = 'black', linewidth = 2, zorder = 10)

cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.savefig(r"C:\Users\deela\Downloads\melThetaE.png", dpi = 400, bbox_inches = 'tight')
plt.show()