import xarray as xr 
import matplotlib.pyplot as plt
import satcmaps as cmap
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 

def map(interval, labelsize):
    fig = plt.figure(figsize=(14, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', which = 'major', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

xs = [-87 - 8/60, -87 - 36/60, -87 - 53/60, -88 - 48/60, -89, -89 - 2/60]
ys = [18 + 13/60, 18 + 30/60, 18 + 39/60, 18 + 49/60, 18 + 44/60, 18 + 44/60]

ax = map(.25, 9)
ax.set_extent([-90, -55, 5, 26], crs = ccrs.PlateCarree())

ax.scatter(xs, ys)
plt.show()