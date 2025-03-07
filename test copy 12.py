import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap

dataType = 'track'

data = xr.open_dataset(r"C:\Users\deela\Downloads\\" + dataType + "Density.nc")
print(data)
time = data['time']
lons = np.arange(-120, 3, 3)
lats = np.arange(0, 75, 3)
data = data[f'{dataType}Density']#.values
print(data.shape)

# test = xr.DataArray(data, dims=("time", "latitude", "longitude"), coords={"time" : time, "latitude" : lats, "longitude" : lons}, name = 'trackDensity')
# test.to_netcdf(r"C:\Users\deela\Downloads\trackDensity2.nc")


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

ax = map(15, 9)
print((data.mean('time')).shape)
c = plt.imshow(data.mean('time'), cmap = cmap.probs())#, levels = 100)
#c = plt.contourf(test.longitude, test.latitude, test.mean('time'), cmap = cmap.probs(), levels = 10, extend = 'both')
ax.set_title('Placeholder', fontweight='bold', fontsize=9, loc='left')
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
#plt.savefig(r"C:\Users\deela\Downloads\saltest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
