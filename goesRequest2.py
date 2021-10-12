import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import s3fs
from datetime import datetime

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
    
    fs.get(l[-1], r"C:\Users\Username\Downloads\goesfile.nc")
    data = xr.open_dataset(r"C:\Users\Username\Downloads\goesfile.nc")
    
    dat = data['CMI']
    center = data['geospatial_lat_lon_extent'].geospatial_lon_center
    
    time = (data.time_coverage_start).split('T')
    time = f"{time[0]} at {time[1][:5]} UTC"
    
    return dat, center, time

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
    gl.xlabels_top = gl.ylabels_right = False
    return ax
