import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import satcmaps as cmaps
import cmaps as cmp 
import image_retrieval as ir
import numpy as np 
from datetime import datetime 
from pyproj import Proj 
import scipy 

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\FIDUCEO_FCDR_L15_MVIRI_MET5-63.0_200106210630_200106210700_EASY_v2.6_fv3.1.nc", decode_times=False)
data1 = np.flip(dataset['toa_bidirectional_reflectance_vis'], axis = 1).sel(x = slice(2454.5 * 2, 46 * 2), y = slice(46 * 2, 2454 * 2))
data1 = data1#[::2, ::2]
data2 = dataset['a_wv'] + dataset['b_wv'] * dataset['count_wv'] 
data2 = (dataset['bt_b_wv'] / (np.log(data2) - dataset['bt_a_wv']) - 273).sel(x_ir_wv = slice(46, 2454), y_ir_wv = slice(46, 2454))
data2 = np.flip(data2, axis = 1)
#data2 = (data2 - np.nanmin(data2)) / -150
#data = np.dstack([data1, data1, data2 + 1])

center = 63
time = f"2001-06-21 at 06:45 UTC"

def stormir(d, lon, lat, cmap = 'irg'):
    plt.figure(figsize = (18, 9))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    #ax.set_extent([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], crs=ccrs.PlateCarree())
    ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs = ccrs.PlateCarree())
    #ax.set_extent([-5, 35, 25, 55], crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False    

    #plt.imshow(data, origin = 'lower', cmap = 'Greys_r', vmin = 0, vmax = 1, transform = ccrs.Geostationary(central_longitude = center))
    #plt.imshow(data1, origin = 'lower', cmap = 'Greys_r', vmin = 0, vmax = 1, transform = ccrs.Geostationary(central_longitude = center))
    plt.imshow(data2, origin = 'lower', cmap = cmaps.codywv3()[0], vmin = -90, vmax = 0, transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.title(f'METEOSAT-5 Water Vapor Imagery\nTime: {time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\meteosatewv.png", dpi = 250, bbox_inches = 'tight')
    plt.show()
    plt.close()

stormir(0, 35.3, -26.5)