import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import cmaps as cmap 
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker

sattDICT  = {'mid' :{'atms' : ('S3', 'TB_88.2QV'),
                     'amsu' : ('S1', 'TB_89.0_0.0QV'),
                     'amsr' : ('S5', 'TB_A89.0H'),
                     'gmi'  : ('S1', 'TB_89.0H'),
                     'mhs'  : ('S1', 'TB_89.0V'),
                     'ssmi' : ('S2', 'TB_85.5H'),
                     'ssmis': ('S4', 'TB_91.665H'),
                     'tmi'  : ('S3', 'TB_85.5H')},
             'low' :{'atms' : ('S2', 'TB_31.4QV'),
                     'amsr' : ('S4', 'TB_36.5H'),
                     'gmi'  : ('S1', 'TB_36.64H'),
                     'ssmi' : ('S1', 'TB_37.0H'),
                     'ssmis': ('S2', 'TB_37.0H'),
                     'tmi'  : ('S2', 'TB_37.0H')}
}

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def getNearestTimes(times, target):
    target = float(target[0:2]) + (float(target[2:4]) / 60)

    minIndex = None
    minValue = float('Inf')
    for x in range(len(times)):
        temp = times[x]
        temp = float(temp[0:2]) + (float(temp[2:4]) / 60) + (float(temp[4:6]) / 3600) 
        if np.abs(temp - target) < minValue:
            minValue = np.abs(temp - target) 
            minIndex = x
    
    return times[minIndex]

bucket = 'noaa-nesdis-tcprimed-pds'
product_name = 'v01r01'
def getFile(storm, satellite, date, time):
    date = date.split('/')
    year = date[2]
    month = str(date[0]).zfill(2)
    day = str(date[1]).zfill(2)
    basin = storm[0:2].upper()
    date = f'{year}{month}{day}'
    dataset = []
    
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    paginator = s3_client.get_paginator('list_objects_v2')
    prefix = f'{product_name}/final/{year}/{basin}/{storm[2:]}/'

    response_iterator = paginator.paginate(
        Bucket = bucket,
        Delimiter='/',
        Prefix = prefix,
    )

    files = []
    for page in response_iterator:
        for object in page['Contents']:
            if satellite in object['Key'] and date in object['Key']:
                file = object['Key']
                files.append(file)

    time = getNearestTimes([temp.split('.')[0][-6:] for temp in files], time)
    for x in range(len(files)):
        if f'{date}{time}' in files[x]:
            file = files[x]
            
    s3_client.download_file(bucket, file, r"C:\Users\deela\Downloads\tcprimed_data.nc") 
    
    return time

def plot(storm, satellite, date, time, datatype = 'mid'):
    time = getFile(storm, satellite, date, time)
    if datatype == 'mid':
        num, band = sattDICT[datatype][satellite.lower()]
    dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tcprimed_data.nc", group = f'passive_microwave/{num}')
    stormData = xr.open_dataset(r"C:\Users\deela\Downloads\tcprimed_data.nc", group = f'overpass_storm_metadata/')
    lat = stormData['storm_latitude'].values
    lon = stormData['storm_longitude'].values

    data = dataset[band]
    lats = dataset['latitude']
    lons = dataset['longitude']
    
    ax = map(1, 9)

    ax.set_title(f'TC-PRIMED: {satellite.upper()} {band.upper()} Microwave\n{dataset.automated_tropical_cyclone_forecasting_system_storm_identifier.upper()}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'{date} at {time}z', fontsize = 10, loc = 'center')
    ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    if datatype == 'mid':
        cr = ax.pcolormesh(lons, lats, data, vmin = 180, vmax = 291, cmap = cmap.mw().reversed(), transform=ccrs.PlateCarree(central_longitude=0))
        cbar = plt.colorbar(cr, orientation = 'vertical', aspect = 50, pad = .02)
        cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    else:
        cw = ax.pcolormesh(lons, lats, data, cmap = cmap.probs2(), vmin = 220, vmax = 281, transform=ccrs.PlateCarree(central_longitude=0))
        cbar = plt.colorbar(cw, ax = ax, orientation = 'vertical', aspect = 50, pad = .02)
        cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    
    ax.set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())

    plt.savefig(r"C:\Users\deela\Downloads\tcprimedtest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()

plot('AL11', 'AMSR', '09/05/2017', '2230')