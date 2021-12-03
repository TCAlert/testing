import matplotlib.pyplot as plt 
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr  
import bdeck as bdeck 

# sample usage
#   run('al01')

def run(storm):
    # Grabs lat/lon position for existing storm off of best track
    lat, lon = bdeck.latlon(storm)
    if lon > 180:
        lon = lon - 360
    
    # Grabs data in a 10 by 10 lat/lon grid for the most recent date
    link = 'https://cwcgom.aoml.noaa.gov/thredds/dodsC/UOHC/UOHC.nc'
    data = xr.open_dataset(link)
    ohc = data['Ocean_Heat_Content'].sel(lon = slice(lon - 10, lon + 10), lat = slice(lat - 10, lat + 10), time = data['time'][-1])

    time = (str(ohc.time.values).split(' '))[0]

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(25, 7))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels = True, linewidth = 0.5, color='black', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False
    
    # Plots data along with center fix
    plt.contourf(ohc.lon, ohc.lat, ohc.values, cmap = 'inferno', levels = np.arange(0, 200, 1))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    c = plt.contour(ohc.lon, ohc.lat, ohc.values, colors = 'black', linewidths = 1.5, levels = [16, 60, 100])
    plt.clabel(c, inline=1, fontsize=10, fmt='%1.0f')
    plt.scatter(lon, lat, color = 'white', facecolor = None, marker = '$\\mathrm{L}$', s = 700, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))
    plt.scatter(lon, lat, color = 'black', facecolor = None, marker = '$\\mathrm{L}$', s = 600, zorder = 101, transform=ccrs.PlateCarree(central_longitude=0))

    plt.title(f'Oceanic Heat Content ({time}) - {storm.upper()}\n16, 60, and 100 KJcm-2 Outlined', fontweight='bold', fontsize=10, loc='left')
    plt.title('TCAlert', fontsize=10, loc='right')

    plt.savefig(r"C:\Users\[Username]\Downloads\ohc.png", dpi = 200, bbox_inches = 'tight')
    plt.show()
    plt.close()
