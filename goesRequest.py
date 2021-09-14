from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
from siphon.catalog import TDSCatalog
import xarray as xr 

def getLightning(satellite, region, var):
    catalog = TDSCatalog(f'https://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes/{satellite.lower()}/products/GeostationaryLightningMapper/FullDisk/current/catalog.xml')    
    dataset = list(catalog.datasets.values())[-1]
    data = dataset.access_urls
    data = xr.open_dataset(dataset.access_urls['OPENDAP'])
    
    time = data.time_coverage_start
    t = str(time).split('T')
    
    time = f"{t[0]} at {(t[1])[:5]} UTC"

    dat = data[var]
    data.close()
    return dat, time

def getData(satellite, band, region):
    catalog = TDSCatalog(f'https://thredds-test.unidata.ucar.edu/thredds/catalog/satellite//goes/{satellite}/products/CloudAndMoistureImagery/{region}/Channel{band.zfill(2)}/current/catalog.xml')
    dataset = list(catalog.datasets.values())[-1]
    data = dataset.access_urls
    data = xr.open_dataset(dataset.access_urls['OPENDAP'])
    cent = data.satellite_longitude
    dat = data['Sectorized_CMI']
    info = (dat.standard_name).split('_')

    info = f"{info[0].capitalize()} {info[1].capitalize()}"

    t = str(dat['time'].values).split('T')
    
    time = f"{t[0]} at {(t[1])[:5]} UTC"
    data.close()
    return dat, time, info, cent

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
