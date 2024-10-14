import numpy as np
from netCDF4 import Dataset
import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import satcmaps as cmap 
import cmaps as cmaps2 

labelsize = 9

def spmap(ax, interval, labelsize, lat, lon, zoom = 2):
    ax.set_frame_on(False)

    zoom = int(zoom)    

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

def panelPlot():
    data = xr.open_dataset(r"C:\Users\deela\Downloads\TCPRIMED_v01r01-final_WP092004_AMSRE_AQUA_011271_20040616041614.nc", group = 'infrared')
    data2 = xr.open_dataset(r"C:\Users\deela\Downloads\TCPRIMED_v01r01-final_WP092004_AMSRE_AQUA_011271_20040616041614.nc", group = 'passive_microwave/S5')
    data3 = xr.open_dataset(r"C:\Users\deela\Downloads\TCPRIMED_v01r01-final_WP092004_AMSRE_AQUA_011271_20040616041614.nc", group = 'passive_microwave/S4')
    print(data3)

    ir = data['IRWIN'] - 273.15
    mmw = data2['TB_A89.0V']
    lmw = data3['TB_36.5V']
    lon = 136.06
    lat = 15.11

    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(2, 2)

    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree())]
    
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_frame_on(False)

    for x in range(1, 5):
        axes[x] = spmap(axes[x], 2, 9, lat, lon, 1)
    
    lats = data['latitude']
    lons = data['longitude']

    axes[0].set_title(f'TC-PRIMED: Microwave and Infrared Panel Plot\nWP092004', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].contourf(data2['longitude'], data2['latitude'], mmw, levels = np.arange(180, 291, 1), extend = 'both', cmap = cmaps2.mw().reversed(), transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, '89GHz (V)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    axes[1].set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())

    cw = axes[2].contourf(data3['longitude'], data3['latitude'], lmw, cmap = cmaps2.probs2(), levels = np.arange(220, 281, 1), transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cw, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, '36.5GHz (V)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    axes[2].set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())

    cw = axes[3].pcolormesh(lons, lats, ir, cmap = cmap.irg()[0], vmin = cmap.irg()[2], vmax = cmap.irg()[1], transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cw, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Infrared-IRG (C)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    axes[3].set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())

    vc = axes[4].pcolormesh(lons, lats, ir, cmap = cmap.bd05()[0], vmin = cmap.bd05()[2], vmax = cmap.bd05()[1], transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(vc, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Infrared-BD (C)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    axes[4].set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())

    plt.savefig(r"C:\Users\deela\Downloads\tcprimedtest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

# ax = map(15, 136, 1)
# #c = plt.pcolormesh(data['longitude'], data['latitude'], ir, vmin = vmin, vmax = vmax, cmap = cmap)
# c = plt.contourf(data2['longitude'], data2['latitude'], mw, levels = np.arange(180, 291, 1), extend = 'both', cmap = cmaps2.mw().reversed())
# plt.title(f'TC-PRIMED: AQUA AMSR-E 89.0H (gHZ)\nWP181998' , fontweight='bold', fontsize=labelsize + 1, loc='left')
# plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
# cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# plt.savefig(r"C:\Users\deela\Downloads\tcprimedtest.png", dpi = 400, bbox_inches = 'tight')
# plt.show()
panelPlot()