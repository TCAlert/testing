import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import numpy as np
import xarray as xr
import datetime
import urllib
import cmaps as cmap 
    
# Function to retrieve storm centered SMAP passes and the maximum detected wind
# The 'storm' object is a tuple containing the latitude and longitude of a given TC based on the NHC of JTWC's best track fix
# The 'ascending' variable is used to determine whether an ascending or descending pass is requested by the user
# Regression to calculate windspeed courtesy of Gene Aguas: https://cdn.discordapp.com/attachments/767902538950901760/956337409598062622/unknown.png
def smap(storm, ascending):
    year = datetime.datetime.now().year
    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day 
    file = f"http://data.remss.com/smap/wind/L3/v01.0/daily/NRT/{str(year)}/RSS_smap_wind_daily_{str(year)}_{str(mon).zfill(2)}_{str(day).zfill(2)}_NRT_v01.0.nc"
    urllib.request.urlretrieve(file, r"C:\Users\deela\Downloads\latestSMAP.nc")
    data = xr.open_dataset(r"C:\Users\deela\Downloads\latestSMAP.nc", decode_times=False)
    lat, lon = storm

    date = str(mon).zfill(2) + "/" + str(day).zfill(2) + "/" + str(year)

    if ascending == 'asc':
        asc = "Ascending"
        node = 0
    elif ascending == 'desc':
        asc = "Descending"
        node = 1

    # Retrieve needed data from file
    minu = data['minute'].sel(node = node)
    data = data['wind'].sel(node = node)

    # Mask unnecessary information to speed up processing
    mask_lon = (data.lon >= lon - 7.5) & (data.lon <= lon + 7.5)
    mask_lat = (data.lat >= lat -7.5) & (data.lat <= lat + 7.5)
    data = data.where(mask_lon & mask_lat, drop=True)

    # Convert data to knots and retrieve maximum value
    data = data * 1.944
    given = data.where(data == data.max(), drop = True).squeeze()

    # Calculate maximum winds using the formula in the usage instructions
    calc = ((given * 362.644732816453) + 2913.62505913216) / 380.88384339523

    # Gets the nearest time to the satellite overpass and reformats it
    try:
        time = minu.sel(lat = lat, lon = lon, method = 'nearest')
        time = f'{str(int(time / 60)).zfill(2)}{str(int(time % 60)).zfill(2)}z'
    except:
        time = minu.sel(lat = given.lat, lon = given.lon, method = 'nearest')
        time = f'{str(int(time / 60)).zfill(2)}{str(int(time % 60)).zfill(2)}z'

    # Creates plot and saves it
    plt.figure(figsize=(20,12))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=-180))
    ax.set_extent([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], crs=ccrs.PlateCarree())
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels = True, linewidth = 0.5, color='black', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False

    c = plt.contour(data.lon, data.lat, data.values, origin='lower', levels = [34, 64, 96, 137], colors = 'black', linewidths = 2, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contourf(data.lon, data.lat, data.values, origin='lower', levels = np.arange(0, 161), cmap = cmap.wind(), transform=ccrs.PlateCarree(central_longitude=0))
    plt.clabel(c, inline=1, fontsize=10, fmt='%1.0f')
    plt.title(f'SMAP Pass on {date} at {time} ({asc})\nCalculated Windspeed - {str(round(float(calc.values), 2))} knots | Max Wind (10 min) - {str(round(float(given.values), 2))} knots' , fontweight='bold', fontsize=10, loc='left')
    plt.title('Deelan Jariwala', fontsize=10, loc='right') 
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\deela\Downloads\stormSMAP.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
#smap((45, 168), 'asc')
#Sample Usage:
# smap((45, 168), 'desc')

