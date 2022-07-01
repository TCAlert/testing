from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import xarray as xr
import datetime
import wget
import urllib
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colors import from_levels_and_colors
import matplotlib.patches as mpatches
import cmaps as cmap 

# Open the GOES-R image
    
usage = '`$smap [storm] [asc/desc]`\nRegression Courtesy of Gene Aguas: https://cdn.discordapp.com/attachments/767902538950901760/956337409598062622/unknown.png'

def smap(storm, ascending):
    year = datetime.datetime.now().year
    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day
    file = f"http://data.remss.com/smap/wind/L3/v01.0/daily/NRT/{str(year)}/RSS_smap_wind_daily_{str(year)}_{str(mon).zfill(2)}_{str(day).zfill(2)}_NRT_v01.0.nc"
    urllib.request.urlretrieve(file, r"C:\Users\Jariwala\Downloads\latestSMAP.nc")
    data = xr.open_dataset(r"C:\Users\Jariwala\Downloads\latestSMAP.nc", decode_times=False)
    lat, lon = storm
    #print(lat, lon)

    date = str(mon).zfill(2) + "/" + str(day).zfill(2) + "/" + str(year)

    if ascending == 'asc':
        asc = "Ascending"
        node = 0
    elif ascending == 'desc':
        asc = "Descending"
        node = 1

    # Get the pixel values
    minu = data['minute'].sel(node = node)
    minu = minu.sel(lat = lat, lon = lon, method = 'nearest')
    time = f'{str(int(minu / 60)).zfill(2)}{str(int(minu % 60)).zfill(2)}z'
    data = data['wind'].sel(node = node)

    #print('Checking data...')
    mask_lon = (data.lon >= lon - 8) & (data.lon <= lon + 8)
    mask_lat = (data.lat >= lat -6) & (data.lat <= lat + 6)
    data = data.where(mask_lon & mask_lat, drop=True)

    data = data * 1.944
    given = np.nanmax(data)

    calc = ((given * 362.644732816453) + 2913.62505913216) / 380.88384339523

    # Choose the plot size (width x height, in inches)
    plt.figure(figsize=(20,12))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=-180))
    ax.set_extent([lon - 8, lon + 8, lat - 6, lat + 6], crs=ccrs.PlateCarree())
    ax.coastlines(resolution='10m', color='orange', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='orange', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels = True, linewidth = 0.5, color='black', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False

    c = plt.contour(data.lon, data.lat, data.values, origin='lower', levels = [34, 64, 96, 137], colors = 'black', linewidths = 2, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contourf(data.lon, data.lat, data.values, origin='lower', levels = range(0, 160), cmap = cmap.wind(), transform=ccrs.PlateCarree(central_longitude=0))
    plt.clabel(c, inline=1, fontsize=10, fmt='%1.0f')
    plt.title(f'SMAP Pass on {date} at {time} ({asc})\nCalculated Windspeed - {str(round(np.nanmax(calc), 2))} knots | Max Wind (10 min) - {str(round(given, 2))} knots' , fontweight='bold', fontsize=10, loc='left')
    plt.title('TCAlert', fontsize=10, loc='right') 
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\Jariwala\Downloads\stormSMAP.png", dpi = 250, bbox_inches = 'tight')
    #print('saving works')
    plt.show()
    plt.close()
smap((45, 168), 'desc')