import xarray as xr
import matplotlib.pyplot as plt
import satcmaps as cmaps 
import numpy as np 
from matplotlib import rcParams 
import cartopy, cartopy.crs as ccrs 
import bdeck as bdeck 
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker


def makeMap(extent, figsize, interval = 5, center = 0):
    labelsize = 8
    fig = plt.figure(figsize = figsize)

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude = center))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.LAND.with_scale('50m'), color = 'black')
    ax.add_feature(cfeature.OCEAN.with_scale('50m'), color = 'black')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5, edgecolor = '#cccccc')
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = '#cccccc', linewidth = 0.5, zorder = 12)
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    return ax

data = xr.open_dataset(r"C:\Users\deela\Downloads\S8_BT_in.nc")
data = data.sel(rows = slice(21500, 22500))
print(data)


map = xr.open_dataset(r"C:\Users\deela\Downloads\geodetic_in.nc")
print(map)
map = map.sel(rows = slice(21500, 22500))
x, y = map['longitude_in'], map['latitude_in']
x2, y2 = map['longitude_orphan_in'], map['latitude_orphan_in']


temp = data['S8_exception_in']
temp2 = data['S8_exception_orphan_in']

# from scipy.interpolate import griddata

# # Use flattened coordinates and valid data
# valid = np.isfinite(temp2.values)
# points = np.column_stack((x2.values[valid], y2.values[valid]))
# values = temp2.values[valid]

# # Interpolate to full grid
# xg, yg = x.values, y.values
# grid_points = np.column_stack((xg.ravel(), yg.ravel()))

# interp_result = griddata(points, values, grid_points, method='nearest')
# interp_result = interp_result.reshape(temp.shape)

# # Merge into original
# temp_merged = temp.copy()
# mask = np.isnan(temp.values)
# temp_merged.values[mask] = interp_result[mask]

cmap, vmax, vmin = cmaps.irg()
print(vmin, vmax)

# plt.pcolormesh(x, y, temp)# - 273.15, vmin = vmin, vmax = vmax, cmap = cmap)
plt.imshow(temp2)
plt.show()