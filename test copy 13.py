import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap

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

data = xr.open_dataset(r"C:\Users\deela\Downloads\CERES_TOA_zonal_mean_fluxes_data.nc")
print(data)

lats = data['lat'] * (np.pi / 180)
data = data['ztoa_net_all_mon'].mean(['time'])
print(data)

c = 2 * np.pi * (6371000**2)
dphi = []
for i in range(180):
    j = i - 1
    dphi.append(lats[i].values - lats[j].values)
print(np.array(dphi).shape, lats.shape, data.shape)
Rtoa_a2_coslat = []
for i in range(1, 180):
    Rtoa_a2_coslat.append(c * np.cos(lats[i].values) * data[i].values * dphi[i])

# Compute poleward energy transport using cumulative integral
Rtoa_a2_coslat = c * np.cos(lats) * data * dphi
poleward_transport = np.cumsum(Rtoa_a2_coslat[::-1])[::-1]  # Integrate from pole to equator

total_poleward_transport = poleward_transport / (2 * np.pi)

print(Rtoa_a2_coslat)

plt.plot(data['lat'], total_poleward_transport / 1e15)
plt.xlabel('Latitude')
plt.ylabel('Heat Transport (Watts)')
plt.grid()
plt.title('Total Poleward Heat Transport', fontweight='bold', fontsize=9, loc='left')
plt.savefig(r"C:\Users\deela\Downloads\heattransportwatts.png", dpi = 400, bbox_inches = 'tight')
plt.show()
