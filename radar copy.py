import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
import cartopy.feature as cfeature
import scipy 
import cmaps 
import cartopy.mpl.ticker as cticker
import boto3
from botocore import UNSIGNED
from botocore.config import Config

def rePoPolar(dataset):
    r = dataset.range.values
    t = dataset.azimuth.values * (np.pi / 180)
    R, T = np.meshgrid(r, t)
    newX, newY = R * np.cos(T), R * np.sin(T)

    range = np.arange(-3e+05, 3e+05, 300)
    gridX, gridY = np.meshgrid(range, range)
    gridded_data = scipy.interpolate.griddata((newX.flatten(), newY.flatten()), dataset.values.flatten(), (gridX.flatten(), gridY.flatten()), method='nearest')
    gridded_data = gridded_data.reshape(2000, 2000).transpose()

    radLat = dataset['latitude'].values
    radLon = dataset['longitude'].values
    lons = radLon + (gridX / (6371000 * np.cos(np.radians(radLat)))) * (180 / np.pi)
    lats = radLat + (gridY / 6371000) * (180 / np.pi)
    
    return lons, lats, gridded_data

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = '#545454', linewidth = 0.5, zorder = 9)

    return ax 

def getData(radar, year, month, day, time):
    bucket = f'noaa-nexrad-level2'    
    
    month = str(month).zfill(2)
    day = str(day).zfill(2)
    time = str(time).zfill(4)
    hour = time[0:2]
    min = time[2:4]

    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    prefix = f'{year}/{month}/{day}/{radar.upper()}'
    kwargs = {'Bucket': bucket,
                'Prefix': prefix}

    resp = s3_client.list_objects_v2(**kwargs)
    files = []
    mins = []
    for x in range(len(resp['Contents'])):
        key = resp['Contents'][x]['Key']
        if key.startswith(f'{prefix}/{radar.upper()}{year}{month}{day}_{hour}'):
            files.append(key)
            mins.append(int(key[31:33]) - int(min))

    s3_client.download_file(bucket, files[np.argmin(np.array(mins)**2)], r"C:\Users\deela\Downloads\radar.gz")

    return files[np.argmin(np.array(mins)**2)]

lat = 30.17
lon = -85.47

fileName = getData('kokx', '2018', '1', '4', '1800')

data = xr.open_dataset(r"C:\Users\deela\Downloads\radar.gz", engine = 'nexradlevel2', group = 'sweep_00')
lons, lats, data = rePoPolar(data['DBZH'])

cmap, vmin, vmax = cmaps.reflectivity()
ax = map(1, 9)
c = ax.pcolormesh(lons, lats, data, cmap = cmap, vmin = vmin, vmax = vmax)
#ax.set_extent([lon - 1, lon + 1, lat - 1, lat + 1], crs = ccrs.PlateCarree())
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.title(f'this is a radar test\ntime goes here', fontweight='bold', fontsize=10, loc='left')
plt.title('Deelan Jariwala', fontsize=10, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\radar.png", dpi = 400, bbox_inches = 'tight')

plt.show()