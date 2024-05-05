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

filename = ir.getDataGOES('18', 2023, 9, 7, '0600', '9')

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\\" + filename + ".nc")
data = dataset['CMI']
plt.imshow(data)
plt.show()
center = dataset['geospatial_lat_lon_extent'].geospatial_lon_center
time = (dataset.time_coverage_start).split('T')
time = f"{time[0]} at {time[1][:5]} UTC"

def stormir(data, lon, lat, cmap = 'irg'):
    plt.figure(figsize = (18, 9))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    #ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs=ccrs.PlateCarree())
    ax.set_extent([-145, -80, -10, 30], crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False    
    cmap, vmax, vmin = cmaps.wv()#cmaps.wvtables[cmap]
    print(data)

    plt.imshow(data - 273, origin = 'upper', transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0), vmin = vmin, vmax = vmax, cmap = cmap)
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.title(f'GOES-16 Channel 13 Brightness Temperature\nSatellite Image: {time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\stormir.png", dpi = 250, bbox_inches = 'tight')
    plt.show()
    plt.close()

stormir(data, -78.1, 13.3, 'gaytestir')