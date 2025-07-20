import xarray as xr
import matplotlib.pyplot as plt
import cmaps as cmaps 
import numpy as np 
from matplotlib import rcParams 
import cartopy, cartopy.crs as ccrs 
import bdeck as bdeck 
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker


def makeMap(extent, figsize, interval = 5, center = 0):
    labelsize = 8
    fig = plt.figure(figsize = figsize)

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude = center))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.LAND.with_scale('50m'), color = 'black')
    ax.add_feature(cfeature.OCEAN.with_scale('50m'), color = 'black')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = '#cccccc', linewidth = 0.5, zorder = 12)
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    return ax

ds = xr.open_dataset(r"C:\Users\deela\Downloads\era5_tcpi_calc_2013.nc")
print(ds['vmax'])

vmax = ds['vmax'] * 1.94384
from helper import thetae, REGIONS

extent, figSize = REGIONS['NATL']

ax = makeMap(extent, figSize, 5) 

c = plt.contourf(ds['lon'], ds['lat'], vmax.sel(time = '2013-10-01') - vmax.sel(time = '2013-08-01') , levels = np.arange(-20, 21, 1), cmap = cmaps.tempAnoms3(), extend = 'both')
ax.set_title(f'ERA5 Maximum Potential Intensity (kt)\nSeptember 2013', fontweight='bold', fontsize=10, loc='left')
ax.set_title('Deelan Jariwala', fontsize=10, loc='right') 

cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\mpi2013.png", dpi = 250, bbox_inches = 'tight')
plt.show()
plt.close()
