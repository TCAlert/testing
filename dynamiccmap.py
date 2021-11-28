from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import xarray as xr
import metpy 
import windclimo as wc
from datetime import datetime 
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import goesRequest2 as goes2
import cgfs as gfs
import bdeck as bdeck 

def getGFSData(storm):
    requests = ['tmpprs', 'tmptrop']
    t = datetime.utcnow()
    hour = xr.Dataset({"time": datetime(t.year, t.month, t.day, t.hour)})['time'].values
    dat = gfs.data(requests, hour)
    time = dat[0].time.values

    lat, lon = bdeck.latlon(storm)
    
    tmp500 = int((dat[0].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5), lev = 500).mean() - 273).values)
    tmptro = int((dat[1].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean() - 273).values)

    return tmp500, tmptro, lat, lon, time

def dynamicCMAP(storm):
    tmp500, tmptro, lat, lon, time = getGFSData(storm)

    num1 = 40 - tmp500
    num2 = abs(tmptro - tmp500)
    num3 = 150 - num1 - num2

    top = cm.get_cmap('bone_r', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('PuRd', num3)

    newcolors = np.vstack((bot(np.linspace(0, 1, num3)), mid(np.linspace(0, 1, num2)), top(np.linspace(0, 1, num1))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp, tmp500, tmptro, lat, lon, time

#tmp500, tmptro, lat, lon = getGFSData('al94')

#ax = plt.axes(projection=ccrs.Geostationary(central_longitude=-75.0, satellite_height=35786023.0))
#img_extent = (-5434894.67527,5434894.67527,-5434894.67527,5434894.67527)
 
## Add coastlines, borders and gridlines
#ax.coastlines(resolution='10m', color='black', linewidth=0.8)
#ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 

#data, center, info, time = goes2.getData('16', '13')
#plt.imshow(data - 273, origin = 'upper', extent = img_extent, vmin = -110, vmax = 40, cmap = dynamicCMAP('al94'))#, transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))
#plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)    

#plt.title(f'Dynamic Colortable Test\n5x5 Box At {lat}N, {360-lon}W' , fontweight='bold', fontsize=10, loc='left')
#plt.title(f'500mb Temp:        {tmp500}C\nTropopause Temp:  {tmptro}C\nTCAlert', fontsize=10, loc='right')

#plt.show()

