import numpy as np
from netCDF4 import Dataset
import scipy 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import satcmaps as cmaps 
import xarray as xr
from scipy.ndimage import gaussian_filter

labelsize = 9

def map(lon, lat, zoom = 2, center = 0):
    try:
        zoom = int(zoom)
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))

        if zoom == -2:
            ax.set_extent([lon - .5, lon + .5, lat - .5, lat + .5], crs=ccrs.PlateCarree())
        elif zoom == -1:
            ax.set_extent([lon - 1, lon + 1, lat - 1, lat + 1], crs=ccrs.PlateCarree())
        elif zoom == 0:
            ax.set_extent([lon - 2.5, lon + 2.5, lat - 2.5, lat + 2.5], crs=ccrs.PlateCarree())
        elif zoom == 1:
            ax.set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())
        elif zoom == 3:
            ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs=ccrs.PlateCarree())
        elif zoom == 2:
            ax.set_extent([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], crs=ccrs.PlateCarree())
    except:
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))

    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = .5, color='black', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False    

    return ax

def plot(ax, num = '5', cmp = 'irg'):
    file = xr.open_dataset(r"C:\Users\deela\Downloads\NmHRIR3H.DownIR.1969.08.17.G.hdf")
    print(file)

    data = file['Temperature at highest view angle']

    cmap, vmax, vmin = cmaps.irtables[cmp.lower()]
    c = ax.imshow(gaussian_filter(data, .5) - 273.15, origin = 'upper', vmin = vmin, vmax = vmax, cmap = cmap, transform = ccrs.PlateCarree(central_longitude = 180))
    print(np.nanmax(file.latitude.values))
    #c = ax.pcolormesh(file.longitude, file.latitude, data - 273, vmin = vmin, vmax = vmax, cmap = cmap)

    return c

date = "08/17/1969"

ax = map(-91.039, 21.755, -4, 0)
c = plot(ax, '4', 'rbtop3')
plt.title(f'NIMBUS HRIR Infrared Image\n{date}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
#plt.savefig(r"C:\Users\deela\Downloads\sentineltest.png", dpi = 500, bbox_inches = 'tight')
plt.show()