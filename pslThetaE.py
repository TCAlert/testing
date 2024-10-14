import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import psl
import helper
import cmaps as cmap 

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('lon')[1:, :]
    dAy = data.diff('lat')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['lon'].diff('lon') * np.cos(data['lat'] * (np.pi / 180)) 
    dy = data['lat'].diff('lat')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

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

years = [2017]
months = [8]
level1 = 850
level2 = 500
if years[0] - 30 >= 1971:
    climoYears = [years[0] - 30, years[0] - 1]
else:
    climoYears = [1971, 2000]

data = psl.createClimoMonthly(years, months, ['air', 'shum', 'uwnd', 'vwnd'], ['Pressure', 'Pressure', 'Pressure', 'Pressure'], False)
clim = psl.createClimoMonthly(np.arange(climoYears[0], climoYears[1] + 1), months, ['air', 'shum', 'uwnd', 'vwnd'], ['Pressure', 'Pressure', 'Pressure', 'Pressure'], False)
stabData = helper.thetae(data[0].sel(level = level1) + 273.15, level1, 1000, data[1].sel(level = level1) / 1000)# - helper.thetae(data[0].sel(level = level2) + 273.15, level2, 1000, data[1].sel(level = level2) / 1000)
stabClim = helper.thetae(clim[0].sel(level = level1) + 273.15, level1, 1000, clim[1].sel(level = level1) / 1000)# - helper.thetae(clim[0].sel(level = level2) + 273.15, level2, 1000, clim[1].sel(level = level2) / 1000)

stabData = stabData.squeeze()
stabClim = stabClim.mean('time').squeeze()

uwnd = (data[2].sel(level = 850)).squeeze()
uClm = (clim[2].sel(level = 850).mean('time')).squeeze()

vwnd = (data[3].sel(level = 850)).squeeze()
vClm = (clim[3].sel(level = 850).mean('time')).squeeze()

dx, dy = Gradient2D(stabData)
advStab = (uwnd[1:, 1:] * dx + vwnd[1:, 1:] * dy) * -1

dx, dy = Gradient2D(stabClim)
advStabClim = (uClm[1:, 1:] * dx + vClm[1:, 1:] * dy) * -1

labelsize = 8 
ax = map(10, labelsize)    
ax.set_extent([295, 355, 5, 35], crs = ccrs.PlateCarree())

c = plt.contourf(advStab.lon, advStab.lat, advStab - advStabClim, origin='lower', levels = np.arange(-5, 5.05, .05), cmap = cmap.tempAnoms(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
plt.streamplot(uwnd.lon, vwnd.lat, uwnd.values - uClm.values, vwnd.values - vClm.values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
plt.title(f'NCEP/NCAR Reanalysis I: {level1}mb Theta-E Advection Anomalies\nClimatology: {climoYears[0]}-{climoYears[1]}' , fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'{helper.numToMonth(months[0])} {str(years[0])}', fontsize = labelsize, loc = 'center')
plt.title('2.5\u00b0\nDeelan Jariwala', fontsize=labelsize, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\thetaeanompsl4.png", dpi = 400, bbox_inches = 'tight')
plt.show()