import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
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

data = xr.open_dataset('https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXAER.5.12.4/2024/02/MERRA2_400.tavg1_2d_aer_Nx.20240201.nc4?DUFLUXV[0:1:23][0:1:360][0:1:575],DUFLUXU[0:1:23][0:1:360][0:1:575]')
test = (data['DUFLUXU'].isel(time = 0)**2 + data['DUFLUXV'].isel(time = 0)**2)**0.5

ax = map(15, 9)
#ax.set_extent([-120, 0, 0, 60])
c = plt.contourf(test.lon, test.lat, test, cmap = cmap.probs(), levels = 100, extend = 'both')
ax.set_title(f'MERRA2 Integrated Dust Transport\nTest', fontweight='bold', fontsize=9, loc='left')
#ax.set_title(f'JJASON {years}', fontsize=9, loc='center') 
#ax.set_title(f'{interval}\u00b0x{interval}\u00b0\nDeelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\saltest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
