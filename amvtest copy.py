import xarray as xr 
import urllib.request as urllib
import helper 
import numpy as np 
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import matplotlib.patheffects as pe
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
from collections import deque


# Creates Cartopy map 
def map(lon, lat, s = 5, center = 0):
    plt.figure(figsize = (18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))
    
    ax.set_extent([lon - s, lon + s, lat - s, lat + s], crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.75)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)  
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False

    return ax

year = 'test'
month = 'test'
day = 'test'
hour = 'test'

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\OR_ABI-L2-DMWF-M6C14_G16_s20250211600205_e20250211609513_c20250211623081.nc")
print(dataset)

plt.title(f'GOES-16 AMVs\nTime: {year}-{month}-{day} at {hour}:00 UTC' , fontweight='bold', fontsize=10, loc='left')
plt.title(f'Deelan Jariwala', fontsize=10, loc='right')
#plt.savefig(r"C:\Users\deela\Downloads\amvtest2.png", dpi = 250, bbox_inches = 'tight')
plt.show()