import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
import file 

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

#file.getGZ(r"C:\Users\deela\Downloads\MRMS_MergedBaseReflectivity_00.50_20240410-021422.grib2.gz")
labelsize = 8

data = xr.open_dataset(r"C:\Users\deela\Downloads\MRMS_MergedBaseReflectivity_00.50_20240410-021422.grib2", engine="cfgrib")
print(data)

mrms = data['unknown']
t = str(data['time'].values).split('T')
print(t)
time = f'{t[0]} at {t[1][0:5]}z'

ax = map(10, labelsize)
c = ax.pcolormesh(mrms.longitude, mrms.latitude, mrms.values, cmap = cmap.ref(), vmin = 0, vmax = 75)
plt.title(f'MRMS Base Reflectivity\nTime: {time}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
#plt.title(f'{str(name).upper()}', fontsize = labelsize + 1, loc = 'center')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
#plt.savefig(r"C:\Users\deela\Downloads\ " + name + title + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()