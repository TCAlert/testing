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

def norm(data):
    return (data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))

# Plot data
def oisstTransect(lats, lons, normalize = False):
    fig = plt.figure(figsize=(12, 12))

    date = '08-27T00'
    years = np.arange(1982, 2026)
    baselink = f"http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean."
    links = [f'{baselink}{str(year)}.nc' for year in years]
    dates = [np.datetime64(f'{str(year)}-{date}') for year in years]
    
    # data = xr.open_mfdataset(links)['sst'].sel(time = dates)
    data_list = []
    for i, link in enumerate(links):
        ds = xr.open_dataset(link)
        sst_slice = ds['sst'].sel(time=dates[i], lat = slice(lats[0], lats[1]), lon = slice(lons[0], lons[1]))
        sst_slice = sst_slice.mean('lon')
        data_list.append(sst_slice)
    data = xr.concat(data_list, dim='time')
    print(data)

    climo = data.mean('time')

    ax = plt.axes()
    ax.grid(True, linestyle = '--')
    ax.set_frame_on(False)
    if normalize == True:
        ax.set_xlabel('Relative Temperature')
    else:
        ax.set_xlabel('Temperature (\u00b0C)')
        ax.set_xlim(18.75, 31.25)
    ax.set_ylabel('Latitude')

    for x in range(len(dates)):
        temp = data.sel(time = dates[x])
        if normalize == True:
            temp.values = norm(temp.values)
        plt.plot(temp.values, temp.lat, color = 'black', linewidth = .5, alpha = 0.5)
    plt.plot(temp.values, temp.lat, color = 'red', linewidth = 1.5, label = '2025')
    if normalize == True:
        climo.values = norm(climo.values)
    plt.plot(climo.values, climo.lat, linewidth = 1.5, color = 'black', label = 'Mean')
    plt.legend()

    plt.title(f'OISSTv2.1 Sea Surface Temperature (\u00b0C) by Latitude\nDate: {date[:5]} 1982-2025', fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{lons[0]}E-{lons[1]}E\nDeelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\oisstTransect.png", dpi = 300, bbox_inches = 'tight')
    plt.show()
    plt.close()
# oisstTransect([0, 32.5], [120, 170])
# oisstTransect([0, 45], [360 - 80, 360 - 35])
# oisstTransect([-20, 20], [180, 360 - 75])
oisstTransect([0, 45], [360 - 70, 360 - 40], True)
