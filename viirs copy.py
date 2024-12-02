import numpy as np
from netCDF4 import Dataset
import scipy 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import satcmaps as cmaps 
import xarray as xr

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

def plot(files, geofs, ax, num = '5', cmp = 'irg'):
    file = xr.open_dataset(r"C:\Users\deela\Downloads\S8_BT_in.nc")
    print(file)

    data = np.flip(file['S8_BT_in'], axis = 1)

    cmap, vmax, vmin = cmaps.irtables[cmp.lower()]
    c = ax.imshow(data - 273, origin = 'lower', vmin = vmin, vmax = vmax, cmap = cmap)

    return c

satt = 'NOAA-21'
date = "10/07/2024"
time = "1918z"
#files = ["SVI05_j02_d20241008_t1859222_e1900468_b09910_c20241008192803958000_oebc_ops.h5", "SVI05_j02_d20241008_t1900481_e1902109_b09910_c20241008192813706000_oebc_ops.h5"]
files = ["SVI01_j02_d20241007_t1919417_e1921064_b09896_c20241007194716838000_oebc_ops.h5", "SVI01_j02_d20241007_t1918176_e1919405_b09896_c20241007194705475000_oebc_ops.h5", "SVI01_j02_d20241007_t1916517_e1918163_b09896_c20241007194641289000_oebc_ops.h5"]
geofs = ["GIMGO_j02_d20241007_t1919417_e1921064_b09896_c20241007194510981000_oebc_ops.h5", "GIMGO_j02_d20241007_t1918176_e1919405_b09896_c20241007194458287000_oebc_ops.h5", "GIMGO_j02_d20241007_t1916517_e1918163_b09896_c20241007194436802000_oebc_ops.h5"]

#map(-91.039, 21.755, -2)
plt.figure(figsize = (18, 9))
ax = plt.axes()
c = plot(files, geofs, ax, '5', 'bd3')
plt.title(f'Mystery Sentinel-3 Infrared Image\nUnknown' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.savefig(r"C:\Users\deela\Downloads\sentineltest.png", dpi = 500, bbox_inches = 'tight')
plt.show()