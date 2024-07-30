import numpy as np
from netCDF4 import Dataset
import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import satcmaps as cmaps 
import cmaps as cmaps2 

labelsize = 9

def map(lat, lon, zoom = 2, center = 0):
    try:
        zoom = int(zoom)
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))
    
        if zoom == 1:
            ax.set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())
        elif zoom == 3:
            ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs=ccrs.PlateCarree())
        elif zoom == 2:
            ax.set_extent([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], crs=ccrs.PlateCarree())
    except:
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))

    # Add coastlines, borders and gridlines
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.75)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)  
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False    

data = xr.open_dataset(r"C:\Users\deela\Downloads\TCPRIMED_v01r00-final_WP181998_SSMI_F14_007864_19981013122713.nc", group = 'infrared')
data2 = xr.open_dataset(r"C:\Users\deela\Downloads\TCPRIMED_v01r00-final_WP181998_SSMI_F14_007864_19981013122713.nc", group = 'passive_microwave/S2')
print(data2)

ir = data['IRWIN'] - 273.15
mw = data2['TB_85.5V']

cmp = 'irg'
cmap, vmax, vmin = cmaps.irtables[cmp.lower()]

ax = map(0, 0, 4)
c = plt.pcolormesh(data['longitude'], data['latitude'], ir, vmin = vmin, vmax = vmax, cmap = cmap)
#c = plt.pcolormesh(data2['longitude'], data2['latitude'], data2['TB_85.5V'], cmap = cmaps2.probs2().reversed())
plt.title(f'TC-PRIMED: F14 SSMI 85.5V (gHZ)\nWP181998' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.savefig(r"C:\Users\deela\Downloads\tcprimedtest.png", dpi = 400, bbox_inches = 'tight')
plt.show()