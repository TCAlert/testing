import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from datetime import datetime
import cmaps as cmap 
import file 

# Function that retrieves Himawari-9 tiles of the requested band and melds them together
# Data is returned at full resolution, regardless of band
bucket = 'noaa-mrms-pds'
product_name = 'MergedBaseReflectivity_00.50'
def getData():
    dataset = []
    date = datetime.utcnow()
    time = str(date.hour).zfill(2) + (str(date.minute))[0] + '0'
    year = date.year
    month = date.month
    day = date.day
    
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    prefix = f'CONUS/{product_name}/{year}{month:02.0f}{day:02.0f}/'
    kwargs = {'Bucket': bucket,
                'Prefix': prefix}

    resp = s3_client.list_objects_v2(**kwargs)
    files = []
    for x in range(len(resp['Contents'])):
        key = resp['Contents'][x]['Key']
        if key.startswith(prefix):
            files.append(key)
    
    f = files[-1]
    print(f'Success! File Name: {f}')
    
    s3_client.download_file(bucket, f, r"C:\Users\deela\Downloads\mrms.grib2.gz")  

    file.getGZ(r"C:\Users\deela\Downloads\mrms.grib2.gz", r"C:\Users\deela\Downloads\mrms.grib2")
    data = xr.open_dataset(r"C:\Users\deela\Downloads\mrms.grib2", engine="cfgrib")

    return data

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor = 'white', linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'grey', linewidth = 0.5, zorder = 9)

    return ax 

def plot(lat, lon = 0):
    try:
        lat = float(lat)
        lon = float(lon)
        title = f'Centered at {lat}N, {abs(lon)}W'
        extent = [lon - 2.5, lon + 2.5, lat - 2.5, lat + 2.5]
    except:
        storm = lat
        lat, lon = bdeck.latlon(storm)
        title = storm.upper()
        extent = [lon - 2.5, lon + 2.5, lat - 2.5, lat + 2.5]

    labelsize = 8

    data = getData()
    mrms = data['unknown'].sel(longitude = slice(extent[0] + 360, extent[1] + 360), latitude = slice(extent[3], extent[2]))
    t = str(data['time'].values).split('T')
    time = f'{t[0]} at {t[1][0:5]}z'

    ax = map(.5, labelsize)
    ax.set_extent(extent)
    c = ax.pcolormesh(mrms.longitude, mrms.latitude, mrms.values, cmap = cmap.reflectivity(), vmin = -10, vmax = 70)
    plt.title(f'MRMS Base Reflectivity\nTime: {time}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'{title}\nDeelan Jariwala', fontsize=labelsize + 1, loc='right')  
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\mrmstest.png", dpi = 400, bbox_inches = 'tight')
    plt.close()
    data.close()
plot(30, -95)
