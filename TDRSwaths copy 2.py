import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from file import getGZ 
import urllib.request

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

def spmap(ax, interval, labelsize):
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

# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")

def panelPlot(dataset, mission, height):
    data = dataset.sel(level = height)
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(2, 2)

    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree())]
    
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_frame_on(False)

    clon = dataset['LONGITUDE'].mean('x').values[0]
    clat = dataset['LATITUDE'].mean('y').values[0]

    for x in range(1, 5):
        axes[x] = spmap(axes[x], .5, 8)
        try:
            axes[x].set_extent([clon - 1, clon + 1, clat - 1, clat + 1], crs=ccrs.PlateCarree())
        except:
            try:
                axes[x].set_extent([clon2 - 1, clon2 + 1, clat2 - 1, clat2 + 1], crs=ccrs.PlateCarree())
            except:
                pass

    lats = data['LATITUDE'].squeeze()
    lons = data['LONGITUDE'].squeeze()
    # date = f"{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)} at {str(data['swath_hour'].values).zfill(2)}{str(data['swath_min'].values).zfill(2)}z"
    date = data['time'].values
    axes[0].set_title(f'Tail Doppler Radar {height}km Diagnostic Plot\n{mission.upper()}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date}', fontsize=10, loc='center')
    axes[0].set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons, lats, data['REFLECTIVITY'].squeeze().values, cmap = cmap.reflectivity2(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    
    cw = axes[2].pcolormesh(lons, lats, data['WIND_SPEED'].squeeze().values * 1.94384, cmap = cmap.wind(), vmin = 140, vmax = 180, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cw, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, 'Wind Speed (kt)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    
    cv = axes[3].pcolormesh(lons, lats, data['W'].squeeze().values, cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Vertical Velocity (m/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    
    vc = axes[4].pcolormesh(lons, lats, data['VORT'].squeeze().values / 1000, cmap = cmap.probs(), vmin = 0, vmax = 0.005, transform=ccrs.PlateCarree(central_longitude=0))
    axes[4].streamplot(lons, lats, data['U'].squeeze().values, data['V'].squeeze().values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    cbar = plt.colorbar(vc, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Relative Vorticity (1/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    # axes[4].scatter(clon, clat, marker = 'x', s = 70, c = '#FF1200', transform=ccrs.PlateCarree(central_longitude=0), label = f'{height}km Center', zorder = 20)
    # axes[4].legend()

    plt.savefig(r"C:\Users\deela\Downloads\TDRtest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

link = 'https://seb.omao.noaa.gov/pub/flight/radar/20251028H1/251028H1_1349_xy.nc.gz'
urllib.request.urlretrieve(link, r"C:\Users\deela\Downloads\RTTDR.nc.gz")
getGZ(r"C:\Users\deela\Downloads\RTTDR.nc.gz")

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\RTTDR.nc")

print(list(dataset.variables.keys()))
print(dataset['WIND_SPEED'].values.shape)
maxWinds = np.nanmax(dataset['WIND_SPEED'].values.squeeze(), axis = (0, 1))
for x in range(len(dataset.level)):
    print(dataset.level.values[x], ': ', round(maxWinds[x] * 1.94384, 1), 'kt')

height = .5
panelPlot(dataset, link.split('/')[6], height = height)

