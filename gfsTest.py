import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import gfsRetrieve as gfs 
import numpy as np 
import cmaps as cmap 

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

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

labelsize = 8 
year = 2024
month = 1
day = 10
hour = 0
date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
data, init = gfs.getData(['ugrdprs', 'vgrdprs'], np.datetime64(f'{date}T{str(hour).zfill(2)}'))
values = ((data[0].sel(lev = 850).values * 1.94384)**2 + (data[1].sel(lev = 850).values * 1.94384)**2)**0.5
#data[0].values = ((data[0].values - 273.15) * (9/5)) + 32
ax = map(5, labelsize)
ax.set_extent([-132.5, -57.5, 17.5, 57.5])
plt.contourf(data[0].lon, data[0].lat, values, cmap = cmap.wind2(), levels = np.arange(0, 153, 1), extend = 'both')
plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
plt.streamplot(data[0].lon - 180, data[1].lat, data[0].sel(lev = 850).values, data[1].sel(lev = 850).values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 180))

plt.title(f'0.25\u00b0 GFS: 850mb Wind (kt)\nInitialization: {init}', fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'Valid at {date} at {str(hour).zfill(2)}:00z', fontsize=labelsize)
plt.title('Deelan Jariwala\nData from NOMADS', fontsize=labelsize, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\gfstest.png", dpi = 400, bbox_inches = 'tight')
plt.show()