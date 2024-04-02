import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import pandas as pd 

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def anomalies(month, years, sd = False):
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
    y = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in years]
    print(y[:-1])
    data = dataset['sst'].sel(time = y)
    
    labelsize = 8 
    ax = map(10, labelsize)    
    ax.set_extent([260, 359, 0, 40], crs = ccrs.PlateCarree())
    print(data.time)
    for x in range(len(data.time)):
        plt.contourf(data.lon, data.lat, data.isel(time = x), origin = 'lower', levels = np.arange(26, 78, 26), alpha = 0.1, colors = 'red', extend = 'max', transform=ccrs.PlateCarree(central_longitude=0))
        if years[x] == 2024:
            plt.contour(data.lon, data.lat, data.isel(time = x), origin = 'lower', levels = [26], colors = 'black', linewidths = 2, transform=ccrs.PlateCarree(central_longitude=0))
        #else:
        #    plt.contour(data.lon, data.lat, data.isel(time = x), origin = 'lower', levels = [26], colors = 'black', linewidths = 1, transform=ccrs.PlateCarree(central_longitude=0))
    plt.contour(data.lon, data.lat, data.sel(time = y[:-1]).mean('time'), origin = 'lower', levels = [26], colors = 'green', linewidths = 2, transform=ccrs.PlateCarree(central_longitude=0))
    plt.title(f'ERSSTv5 26C Isotherm Location\n1974-2023 Mean in Green' , fontweight='bold', fontsize=labelsize, loc='left')
    plt.title(f'{helper.numToMonth(month)} {str(years)}', fontsize = labelsize, loc = 'center')
    plt.title('Deelan Jariwala', fontsize=labelsize, loc='right')  
    #cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    #cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\ersstComposite.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

anomalies('3', [1878, 1926, 1933, 1942, 1995, 1998, 2005, 2010, 2020])