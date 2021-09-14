from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
from siphon.catalog import TDSCatalog
import xarray as xr 
import s3fs
import cmaps as cmap
from datetime import datetime

def getData(satellite, band):
    # Use the anonymous credentials to access public data
    fs = s3fs.S3FileSystem(anon=True)

    # List contents of GOES-16 bucket.
    fs.ls('s3://noaa-goes16/')

    # List specific files of GOES-17 CONUS data (multiband format) on a certain hour
    # Note: the `s3://` is not required
    date = datetime.utcnow()
    days = date.strftime('%j')
    try:
        files = np.array(fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days}/{str(date.hour).zfill(2)}/'))
    except:
        try:
            files = np.array(fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days}/{str(date.hour - 1).zfill(2)}/'))
        except:
            files = np.array(fs.ls(f'noaa-goes{satellite}/ABI-L2-CMIPF/{date.year}/{days - 1}/{str(23).zfill(2)}/'))

    l = []
    for x in range(len(files)):
        if f'M6C{band.zfill(2)}' in files[x]:
            l.append(files[x])
    #print(np.array(l))
    # Download the first file, and rename it the same name (without the directory structure)
    fs.get(l[-1], r"C:\Users\Jariwala\Downloads\goesfile.nc")
    data = xr.open_dataset(r"C:\Users\Jariwala\Downloads\goesfile.nc")
    
    dat = data['CMI']
    center = data['geospatial_lat_lon_extent'].geospatial_lon_center
    
    time = (data.time_coverage_start).split('T')
    time = f"{time[0]} at {time[1][:5]} UTC"
    
    return dat, center, 'Brightness Temperature', time

def makeMap(loc, size):
    # Choose the plot size (width x height, in inches)
    plt.figure(figsize = size)

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))#, satellite_height=35786023.0))
    ax.set_extent(loc, crs=ccrs.PlateCarree())
    #ax = plt.axes(projection = ccrs.Geostationary(central_longitude=-75.2, satellite_height=35786023.0)) 

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False
    return ax

#satellite = '17'
#band = '9'
#data, center, info, time = getData(satellite, band)
#lat = 13.6
#lon = -105.9
#makeMap([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], (18, 9))
#img_extent = (-5434894.67527,5434894.67527,-5434894.67527,5434894.67527)

#plt.imshow(data - 273, origin = 'upper', extent = img_extent, vmin = -90, vmax = 0, cmap = cmap.wv(), transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))# interpolation = 'Gaussian')
#plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
#plt.title(f'GOES {satellite} Channel {band.zfill(2)} {info}\nSatellite Image: {time}' , fontweight='bold', fontsize=10, loc='left')
#storm = 'test'
#plt.title(f'{storm.upper()}\nTCAlert', fontsize=10, loc='right')
#plt.show()
