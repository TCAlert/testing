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

year = 2024
month = 5
day = 31
hour = 6
# for x in range(0, 123, 3):
#     link = f'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_chem_0p25.pl?dir=%2Fgefs.{year}{str(month).zfill(2)}{str(day).zfill(2)}%2F{str(hour).zfill(2)}%2Fchem%2Fpgrb2ap25&file=gefs.chem.t{str(hour).zfill(2)}z.a2d_0p25.f{str(x).zfill(3)}.grib2&var_COLMD=on&lev_entire_atmosphere=on&subregion=&toplat=25&leftlon=270&rightlon=359.75&bottomlat=10'    
#     name = getGRIB(link, title = f'GEFSChem_{x}.grib2')

test = xr.open_mfdataset(r"C:\Users\deela\Downloads\GEFSChem_*.grib2", combine='nested', concat_dim='valid_time')
plt.imshow(test['unknown'].isel(valid_time = 0), cmap = cmap.dust2(), vmin = 0, vmax = 7.5/1e4)
#test.to_netcdf(r"C:\Users\deela\Downloads\sal.nc")
test = test['unknown'].mean('latitude')
test = test.sortby('valid_time')

fig = plt.figure(figsize=(12, 12))
ax = plt.axes()

ax.invert_yaxis()
c = plt.contourf(test.longitude, test.valid_time, test.values, cmap = cmap.dust2(), levels = np.arange(0, 7.5/1e4, .01/1e4))
ax.set_title(f'GEFS Column-Integrated Mass Density (kg/m^2) Hovmoller\nInitialization: {year}-{str(month).zfill(2)}-{str(day).zfill(2)} at {str(hour).zfill(2)}00 UTC', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'10N to 25N | 90W to 0W', fontsize=9, loc='center') 
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\saltest.png", dpi = 400, bbox_inches = 'tight')
plt.show()