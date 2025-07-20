import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import s3fs
from datetime import datetime
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from helper import REGIONS, USREGIONS
import satcmaps as cmaps
import warnings 
import matplotlib
matplotlib.use('Agg')
warnings.simplefilter(action='ignore', category=UserWarning)

# Function that retrieves GOES-R data based on satellite and requested band (single band format)
# Resulting file is called "goesfile.nc"
# Data is returned at full resolution, regardless of band
def getData(satellite, band, year, day, hour, n):
    fs = s3fs.S3FileSystem(anon=True)
    fs.ls('s3://noaa-goes16/')
    
    files = fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{str(year)}/{str(day)}/{str(hour).zfill(2)}/')
    files = np.array(files)

    l = []
    for x in range(len(files)):
        if f'M6C{band.zfill(2)}' in files[x]:
            l.append(files[x])
    
    for x in range(len(l)):
        fs.get(l[x], r"C:\Users\deela\Downloads\goesLoopfile.nc")
        data = xr.open_dataset(r"C:\Users\deela\Downloads\goesLoopfile.nc")
    
        dat = data['CMI']
        center = data['geospatial_lat_lon_extent'].geospatial_lon_center
    
        time = (data.time_coverage_start).split('T')
        time = f"{time[0]} at {time[1][:5]} UTC"
        
        stormwv('nwatl', dat, center, time, n + x + 1, 'wv14')
        
        data.close()

    return n + len(l)

def stormwv(storm, data, center, time, n, cmp = 'wv14'):
    band = '09'
    try:
        extent, figSize = REGIONS[storm.upper()]
    except:
        extent, figSize = USREGIONS[storm.upper()]
    lon = (extent[0] + extent[1]) / 2
    title = 'GOES East'

    plt.figure(figsize = figSize)
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False

    cmp, vmax, vmin = cmaps.wvtables[cmp.lower()]
    plt.imshow(data - 273, origin = 'upper', transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0), vmin = vmin, vmax = vmax, cmap = cmp)
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.title(f'{title} Channel {band.zfill(2)} Brightness Temperature\nSatellite Image: {time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'2km\nDeelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\fiona\\" + str(n) + "_.png", dpi = 100, bbox_inches = 'tight')
    #plt.show()
    plt.close()
    data.close()

dates = np.arange(266, 267, 1)
hours = np.arange(3, 28, 1)

n = 0
for x in range(len(dates)):
    for y in range(len(hours)):
        print(n)
        if hours[y] == 24:
            hours[y:] = hours[y:] - 24
            dates[x] = dates[x] + 1
        n = getData('16', '09', 2022, dates[x], hours[y], n)