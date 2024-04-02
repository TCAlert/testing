import matplotlib.pyplot as plt  # Plotting library
import numpy as np
from datetime import datetime 
import gefsRetrieve as gefs
import cmaps as cmap 
from matplotlib import patheffects
from matplotlib.offsetbox import AnchoredText
import adeck 
import xarray as xr 
from matplotlib import rcParams
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cartopy.crs as ccrs
rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 7))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
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
    # ax.grid(linestyle = '--', which = 'minor', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    # ax.minorticks_on()
    return ax 

# Sample usage
t = datetime.now()
year = t.year
month = t.month
day = t.day
hr = 0
fcastHour = 210

data, init = gefs.getData2(['tcdcclm'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
data[0] = data[0].mean('ens')
print(data[0])
print(init)

time = (str(data[0].time.values)).split('T')
time = f'{time[0]} at {(time[1][:5])}z'

ax = map(5, 9)
ax.set_extent([-127.5, -62.5, 22.5, 52.5])
c = plt.contourf(data[0].lon, data[0].lat, data[0].values, cmap = cmap.cloud(), levels = np.arange(0, 101, 1), extend = 'both', transform = ccrs.PlateCarree(central_longitude = 0))

ax.set_title(f'0.5\u00b0 GEFS Total Cloud Cover (%)\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
ax.set_title(f'Forecast Hour: {fcastHour} ({time})', fontsize = 10, loc = 'center')
ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
cbar.set_ticks(np.arange(0, 110, 10))
plt.savefig(r"C:\Users\deela\Downloads\gefstest.png", dpi = 400, bbox_inches = 'tight')
plt.show()