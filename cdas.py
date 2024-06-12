import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from file import getGRIB

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder = 21)
    ax.add_feature(cartopy.feature.BORDERS.with_scale('10m'), edgecolor='black', linewidth=0.5, zorder = 25) 
    ax.add_feature(cartopy.feature.LAND.with_scale('10m'), zorder = 10)
    
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)

    return ax 

year = 2024
month = 6
day = 4
hour = 12
contour = 1
link = f'https://nomads.ncep.noaa.gov/pub/data/nccf/com/cdas/prod/cdas.{year}{str(month).zfill(2)}{str(day).zfill(2)}/cdas.t{str(hour).zfill(2)}z.sstgrb.grib2'
name = getGRIB(link, title = f'cdas.grib2')

test = xr.open_dataset(r"C:\Users\deela\Downloads\cdas.grib2")
print(test)
data = test['t'] - 273

ax = map(5, 5*1.5)
bounds = [-100, -10, 0, 65]
bounds = [bounds[0] - 1, bounds[1] + 1, bounds[2] - 1, bounds[3] + 1]
ax.set_extent(bounds, crs = ccrs.PlateCarree())
plt.contour(data.longitude, data.latitude, data.values, levels = [26], colors = 'black', linewidths = 1.5, transform=ccrs.PlateCarree(central_longitude=0))
plt.contour(data.longitude, data.latitude, data.values, levels = np.arange(0, 33, contour), colors = 'black', linewidths = 0.25, transform=ccrs.PlateCarree(central_longitude=0))
plt.contourf(data.longitude, data.latitude, data.values, levels = np.arange(0, 33, contour), cmap= cmap.sst(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
ax.set_title(f'CDAS Sea Surface Temperature (\u00b0C), 26C Isotherm Outlined\nTime: {year}-{str(month).zfill(2)}-{str(day).zfill(2)} at {str(hour).zfill(2)}00 UTC', fontweight='bold', fontsize=10, loc='left')
#ax.set_title(f'10N to 25N | 90W to 0W', fontsize=9, loc='center') 
ax.set_title(f'NATL\nDeelan Jariwala', fontsize=10, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\saltest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
