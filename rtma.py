import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import gfsRetrieve as gfs 
import numpy as np 
import cmaps as cmap 
import matplotlib.patheffects as pe

# Create a map using Cartopy
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

labelsize = 9
spacing = .5
year = 2024
month = 6
day = 18
hour = 17
extent = [-79, -69, 37, 45]
data = xr.open_dataset(f'http://nomads.ncep.noaa.gov:80/dods/rtma2p5/rtma2p5{str(year)}{str(month).zfill(2)}{str(day).zfill(2)}/rtma2p5_anl_{str(hour).zfill(2)}z')
data = data['dpt2m'].squeeze()
data.values = ((data.values - 273.15) * (9/5)) + 32
print(data)

date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
ax = map(spacing, labelsize - 1)
ax.set_extent(extent)
c = plt.contourf(data.lon, data.lat, data.values, cmap = cmap.pwat(), levels = np.arange(0, 91, 1), extend = 'both')
#plt.contour(data.lon, data.lat, data.values, colors = 'black', levels = [32])
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
#cbar.ax.set_yticks(np.arange(-100, 140, 10))

for x in np.arange(extent[0] + spacing / 2, extent[1], spacing):
    for y in np.arange(extent[2] + spacing / 2, extent[3], spacing):
        plt.text(x, y, int(np.round(data.sel(lon = x, lat = y, method = 'nearest').values, 0)), size=labelsize, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

plt.title(f'2m AGL Temperature (\u00b0F)\nInitialization: {date} at {str(hour).zfill(2)}:00z', fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'Valid at {date} at {str(hour).zfill(2)}:00z', fontsize=labelsize)
plt.title('RTMA\nDeelan Jariwala', fontsize=labelsize, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\rtmatest.png", dpi = 400, bbox_inches = 'tight')
plt.show()