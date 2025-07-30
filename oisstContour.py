import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import xarray as xr
import bdeck as bdeck 
from matplotlib import cm
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from helper import REGIONS, gridlines
from datetime import datetime
import cmaps 
import matplotlib.patheffects as pe

# Plot data
def oisstContour(storm, isotherm = 26):
    fig = plt.figure(figsize=(18, 9))

    date = '07-25T00'
    years = np.arange(1995, 2026)
    baselink = f"http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean."
    links = [f'{baselink}{str(year)}.nc' for year in years]
    dates = [np.datetime64(f'{str(year)}-{date}') for year in years]
    
    # data = xr.open_mfdataset(links)['sst'].sel(time = dates)
    data_list = []
    for i, link in enumerate(links):
        ds = xr.open_dataset(link)
        sst_slice = ds['sst'].sel(time=dates[i])
        data_list.append(sst_slice)
    data = xr.concat(data_list, dim='time')
    print(data)

    climo = data.mean('time')

    # Use the Geostationary projection in cartopy
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))

    # Add coastlines, borders and gridlines
    ax.set_frame_on(False)
    ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder = 21)
    ax.add_feature(cartopy.feature.BORDERS.with_scale('10m'), edgecolor='black', linewidth=0.5, zorder = 25) 
    ax.add_feature(cartopy.feature.LAND.with_scale('10m'))
    ax = gridlines(ax, 5)


    bounds = REGIONS[storm.upper()][0]
    fig = fig.set_size_inches(REGIONS[storm.upper()][1])
    bounds = [bounds[0] - 1, bounds[1] + 1, bounds[2] - 1, bounds[3] + 1]
    ax.set_extent(bounds, crs = ccrs.PlateCarree())
    contour = 1
    atcf = True

    for x in range(len(dates)):
        temp = data.sel(time = dates[x])
        alpha = x / len(dates)
        plt.contour(temp.lon, temp.lat, temp.values, levels = [isotherm], colors = 'black', alpha = alpha, linewidths = 1, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contour(temp.lon, temp.lat, temp.values, levels = [isotherm], colors = 'red', linewidths = 1.5, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contourf(climo.lon, climo.lat, climo.values, levels = np.arange(0, 33, .1), cmap= cmaps.sst(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)

    plt.title(f'OISSTv2.1 Sea Surface Temperature (\u00b0C), {isotherm}C Isotherm\nDate: {date[:5]}', fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{storm.upper()}\nDeelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\oisstContour.png", dpi = 300, bbox_inches = 'tight')
    plt.show()
    plt.close()
oisstContour('wpac', isotherm = 28)