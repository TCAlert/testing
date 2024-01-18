import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import gfsRetrieve as gfs 
import numpy as np 
import cmaps as cmap 
import urllib.request 

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

labelsize = 9
year = 2016
month = 1
day = 25
link = f'https://www.nohrsc.noaa.gov/snowfall_v2/data/{year}{str(month).zfill(2)}/sfav2_CONUS_72h_{year}{str(month).zfill(2)}{str(day).zfill(2)}12.nc'
urllib.request.urlretrieve(link, r"C:\Users\deela\Downloads\snow.nc")
data = xr.open_dataset(r"C:\Users\deela\Downloads\snow.nc")
print(data)
data = data['Data'].squeeze() * 39.3700789
print(data.attrs)

date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
ax = map(4, labelsize - 1)
ax.set_extent([-126, -67, 23, 51])
c = plt.contourf(data.lon, data.lat, data.values, levels = np.arange(0, 96.1, .1), cmap = cmap.snow(), extend = 'both')
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.set_yticks(np.arange(0, 102, 6))

plt.title(f'National Gridded Snowfall Analysis\n72hr Accumulation (inches)', fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'Ending at {date} at 12:00z', fontsize=labelsize)
plt.title('NOHRSC\nDeelan Jariwala', fontsize=labelsize, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\snowtest.png", dpi = 400, bbox_inches = 'tight')
plt.show()