from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import urllib.request as urllib
import matplotlib.patches as mpatches
import xarray as xr 
from siphon.catalog import TDSCatalog
from siphon.http_util import session_manager
from datetime import datetime 
from netCDF4 import num2date
import cartopy.feature as cfeature

def url():
    yer = datetime.now().year
    mon = datetime.now().month
    day = datetime.now().day

    date = f"{yer}{str(mon).zfill(2)}{str(day).zfill(2)}"

    url = f'http://nomads.ncep.noaa.gov:80/dods/rap/rap{date}/rap_f00'
    return date, url

def retrieveData(requests):
    date, link = url()
    print("RAP Forecast Hour 00: ", date)
    dataset = xr.open_dataset(link)
    times = dataset['time']
    dat = []
    for x in range(len(requests)):
        dat.append((dataset[requests[x]]).sel(time = times[0].values))
    dataset.close()
    print("Data retrieved")
    return dat

def map(e, w, s, n, size):
    plt.figure(figsize = size)

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_extent([e, w, s, n])

    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 1)
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude=0), zorder = 9, draw_labels = True, linewidth = 0.5, color='white', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False 
    return ax

def windbarbs(lons, lats, uwnd, vwnd, lvl):
    uwnd = uwnd.sel(lev = lvl)
    vwnd = vwnd.sel(lev = lvl)
    plt.barbs(lons, lats, uwnd.values * 1.9438, vwnd.values * 1.94384, zorder = 10)