import xarray as xr
import matplotlib.pyplot as plt
import cmaps as cmaps 
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

type_of_levels = [
    'surface', 'heightAboveGround', 'isobaricInhPa', 'meanSea', 'cloudTop',
    'isothermal', 'pressureFromGroundLayer', 'sigmaLayer', 'heightAboveGroundLayer',
    'sigma', 'atmosphere', 'atmosphereSingleLayer', 'depthBelowLand', 'isobaricLayer',
    'lowCloudLayer', 'middleCloudLayer', 'highCloudLayer', 'cloudBase',
    'cloudCeiling', 'nominalTop', 'isothermZero', 'highestTroposphericFreezing',
    'adiabaticCondensation', 'equilibrium'
]

# for lvl in type_of_levels:
#     try:
#         print(f"Trying: {lvl}")
#         ds = xr.open_dataset(
#             r"C:\Users\deela\Downloads\hrrr.t18z.wrfsfcf00.grib2",
#             engine="cfgrib",
#             backend_kwargs={"filter_by_keys": {"typeOfLevel": lvl, "stepType" : 'instant'}}
#         )
#         print(f"Success with: {lvl}")
#         print(ds)
#         break
#     except Exception as e:
#         print(f"Failed with {lvl}: {str(e).splitlines()[-1]}")

ds = xr.open_dataset(
    r"C:\Users\deela\Downloads\hrrr.t18z.wrfsfcf00.grib2",
    engine="cfgrib",
    backend_kwargs={"filter_by_keys": {"typeOfLevel": 'heightAboveGround', "stepType" : 'instant', 'level' : 2}})

ds2 = xr.open_dataset(
    r"C:\Users\deela\Downloads\hrrr.t18z.wrfsfcf00.grib2",
    engine="cfgrib",
    backend_kwargs={"filter_by_keys": {"typeOfLevel": 'surface', "stepType" : 'instant'}})


print(list(ds2.variables))

mslp = ds2['sp'] / 100
temp = ds['t2m']
shum = ds['sh2']

from helper import thetae, REGIONS

extent, figSize = REGIONS['GOM']

ax = makeMap(extent, figSize, 2) 

the = thetae(temp, mslp, 1000, shum)
c = plt.contourf(ds['longitude'], ds['latitude'], the, levels = np.arange(330, 360, .25), cmap = cmaps.probs2(), extend = 'both')
ax.set_title(f'Near Surface Equivalent Potential Temperature\nInitialization: 09/14/2020 at 18z', fontweight='bold', fontsize=10, loc='left')
ax.set_title(f'Forecast Hour: 00', fontsize = 10, loc = 'center')
ax.set_title('HRRR\nDeelan Jariwala', fontsize=10, loc='right') 

cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\hrrrsallythetae.png", dpi = 250, bbox_inches = 'tight')
# plt.show()
plt.close()
