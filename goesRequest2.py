import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import s3fs
from datetime import datetime
import boto3
from botocore import UNSIGNED
from botocore.config import Config

# Function that retrieves GOES-R data based on satellite and requested band (single band format)
# Resulting file is called "goesfile.nc"
# Data is returned at full resolution, regardless of band
def getData(satellite, band):
    fs = s3fs.S3FileSystem(anon=True)
    fs.ls('s3://noaa-goes16/')
    
    date = datetime.utcnow()
    days = date.strftime('%j')
    try:
        files = fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days}/{str(date.hour).zfill(2)}/')
    except:
        try:
            fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days}/{str(date.hour - 1).zfill(2)}/')
        except:
            fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days - 1}/{str(23).zfill(2)}/')
    files = np.array(files)

    l = []
    for x in range(len(files)):
        if f'M6C{band.zfill(2)}' in files[x]:
            l.append(files[x])
    
    fs.get(l[-1], r"C:\Users\deela\Downloads\goesfile.nc")
    data = xr.open_dataset(r"C:\Users\deela\Downloads\goesfile.nc")
    
    dat = data['CMI']
    center = data['geospatial_lat_lon_extent'].geospatial_lon_center
    
    time = (data.time_coverage_start).split('T')
    time = f"{time[0]} at {time[1][:5]} UTC"
    
    return dat, center, time

# Function that retrieves Himawari-9 tiles of the requested band and melds them together
# Data is returned at full resolution, regardless of band
bucket = 'noaa-himawari9'
product_name = 'AHI-L2-FLDK-ISatSS'
def getHimawariData(band):
    dat = []
    dataset = []
    date = datetime.utcnow()
    time = str(date.hour).zfill(2) + (str(date.minute))[0] + '0'
    year = date.year
    month = date.month
    day = date.day
    band = str(band).zfill(2)
    
    if int(band) > 4:
        res = '020'
    elif int(band) == 3:
        res = '005'
    else:
        res = '010'

    if int(band) in [10, 11, 12, 13, 14, 15]:
        bits = '12'
    elif int(band) == 7:
        bits = '14'
    else:
        bits = '11'
    
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    while True:
        print('Trying again.')
        try:
            prefix = f'{product_name}/{year}/{month:02.0f}/{day:02.0f}/{time}/OR_HFD-{res}-B{bits}-M1C{band}'
            print(f'Time: {prefix}')
            kwargs = {'Bucket': bucket,
                      'Prefix': prefix}

            resp = s3_client.list_objects_v2(**kwargs)
            files = []
            for x in range(len(resp['Contents'])):
                key = resp['Contents'][x]['Key']
                if key.startswith(prefix):
                    files.append(key)
            print('Success!')
            break
        except:
            if time[-2:] == '00':
                time = str(int(time) - 50).zfill(4)
            else:
                time = str(int(time) - 10).zfill(4)
            prefix = f'{product_name}/{year}/{month:02.0f}/{day:02.0f}/{time}/OR_HFD-{res}-B{bits}-M1C{band}'
            print(f'New Time: {prefix}')
          
    try:
        for x in range(len(files)):
            s3_client.download_file(bucket, files[x], r"C:\Users\deela\Downloads\himawari8\tile" + str(x) + ".nc")  
        f = '8'      
    except:
        for x in range(len(files)):
            s3_client.download_file(bucket, files[x], r"C:\Users\deela\Downloads\himawari9\tile" + str(x) + ".nc")        
        f = '9'

    with xr.open_mfdataset(r"C:\Users\deela\Downloads\himawari" + f + "\*.nc", autoclose = True) as dataset:
        dat = dataset['Sectorized_CMI']
        center = dataset.product_center_longitude
        time = f"{str(month).zfill(2)}/{str(day).zfill(2)}/{str(year)} at {str(time).zfill(4)} UTC"
        dataset.close()
    
    return dat, center, 'Brightness Temperature', time, dataset


# Creates Cartopy map 
def makeMap(loc, size):
    # Choose the plot size (width x height, in inches)
    plt.figure(figsize = size)

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_extent(loc, crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False
    return ax
