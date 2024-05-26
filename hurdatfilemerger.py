import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import numpy as np
import cmaps as cmap 
from matplotlib import rcParams 
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

# natl = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2Density1x1.nc")
# epac = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityEPAC.nc")
# print(natl, epac)
# data = xr.concat([natl, epac], dim = 'basin')
# data = data.sum(dim = 'basin')
# data.to_netcdf(r"C:\Users\deela\Downloads\HURDAT2DensityALL.nc")
data = xr.open_dataset(r"C:\Users\deela\Downloads\HURDAT2DensityALL.nc")
print(data)

ax = map(10, 9)
ax.set_extent([-177.5, -2.5, 2.5, 67.5], crs = ccrs.PlateCarree())
c = ax.imshow(data['ACE'].mean('time'), origin='lower', cmap = cmap.probs(), vmin = 0)
ax.set_title(f'HURDAT2 ACE Density Composite', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Atlantic: 1851-2023 | East Pacific: 1949-2023', fontsize=9, loc='center') 
ax.set_title(f'1\u00b0x1\u00b0\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.savefig(r"C:\Users\deela\Downloads\hurdat2climo.png", dpi = 400, bbox_inches = 'tight')
plt.show()