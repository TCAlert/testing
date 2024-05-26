import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import numpy as np
import cmaps as cmap 
from matplotlib import rcParams 
from helper import numToMonth
from scipy.ndimage import gaussian_filter
rcParams['font.family'] = 'Courier New'

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
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

data = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityALL.nc")
data = data['24hrChange']
print(data)

month = '9'
years = [1949, 2023]
months = np.array([np.datetime64(f'{y}-{str(month).zfill(2)}-01') for y in range(years[0], years[1] + 1)])
print(months)

data = data.sel(time = months).mean('time')

s = 3
data.values = gaussian_filter(data.values, sigma = s)

ax = map(10, 9)
ax.set_extent([-177.5, -2.5, 2.5, 67.5], crs = ccrs.PlateCarree())
c = ax.imshow(data, origin='lower', cmap = cmap.tempAnoms(), vmin = -1, vmax = 1)
f = ax.contour(data, levels = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2], colors = 'black')
plt.clabel(f, fontsize = 5, inline = 1)#, fmt = '%1.3f')
ax.set_title(f'HURDAT2 Wind Density Climatology\nYears Used: {years[0]}-{years[1]}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(numToMonth(month), fontsize=9, loc='center') 
ax.set_title(f'1\u00b0x1\u00b0\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
#plt.savefig(r"C:\Users\deela\Downloads\hurdat2climo" + month + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()