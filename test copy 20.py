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

cmp, vmin, vmax = cmaps.ref1()
print(vmax, vmin)

# data = xr.open_dataset(r"C:\Users\deela\Downloads\temp\HWX_2000_08_15_12_08_38.nc")
data = xr.open_mfdataset(r"C:\Users\deela\Downloads\temp\HWX_2000_08_15_12_08*",
                             combine="nested",          # don't try coordinate-aware alignment
    concat_dim="time",         # just stack along time
    data_vars="minimal",
    coords="minimal",
    compat="override",
    join="override",
    decode_timedelta=True,
)
ref = data['DBZ']
print(data)

# Build azimuths (time -> azimuth assumption) and ranges
time_dim2 = ref.shape[0]
ranges2 = ref['range'].values
azimuth = data['azimuth']
print(azimuth)

# Polar -> Cartesian
r2, theta2 = np.meshgrid(ranges2, np.deg2rad(azimuth))
x2 = r2 * np.sin(theta2)
y2 = r2 * np.cos(theta2)

# Plot with radar-like colormap and a 5 NM ring overlay
plt.figure(figsize=(8, 8))
plt.pcolormesh(x2, y2, ref.values, cmap= cmp, vmin=0, vmax=30)
plt.colorbar(label='Reflectivity (dBZ)')

plt.xlabel("X (NM)")
plt.ylabel("Y (NM)")
plt.title("Radar Reflectivity (PPI-style) with 5 NM ring")
plt.axis("equal")
plt.show()
