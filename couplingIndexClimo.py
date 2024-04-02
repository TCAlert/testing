import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import psl
import helper
import cmaps as cmap 

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
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

years = np.arange(1971, 2024)
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

llvlData = psl.createClimoMonthly(years, months, ['air', 'shum'], ['Pressure', 'Pressure'], False)
tropData = psl.createClimoMonthly(years, months, ['air', 'pres'], ['Tropopause', 'Tropopause'], False)

thetae850 = helper.thetae(llvlData[0].sel(level = 850) + 273.15, 850, 1000, llvlData[1].sel(level = 850) / 1000)
thetatrop = helper.theta(tropData[0], tropData[1], 1000)

CI = thetatrop - thetae850
CI.to_netcdf(r"C:\Users\deela\Downloads\R1CI1971-2023.nc")

temp = CI.sel(time = np.datetime64('2023-08-01')) - CI.mean('time')
labelsize = 8 
ax = map(20, labelsize)    
#ax.set_extent([240, 359, 0, 70])

plt.contourf(CI.lon, CI.lat, temp, origin='lower', levels = np.arange(-15, 15.1, .1), cmap = cmap.tempAnoms(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
plt.title(f'NCEP/NCAR Reanalysis I: Coupling Index\n1991-2023 Climatology' , fontweight='bold', fontsize=labelsize, loc='left')
#plt.title(f'{helper.numToMonth(month)} {str(years)}', fontsize = labelsize, loc = 'center')
plt.title('Deelan Jariwala', fontsize=labelsize, loc='right')  
cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\couplingindex.png", dpi = 400, bbox_inches = 'tight')
plt.show()