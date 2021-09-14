import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from siphon.catalog import TDSCatalog
import xarray as xr 

# This set of functions grabs GOES 16 and 17 data from Unidata's Thredds Data Server

# Function to retrieve GLM lightning data
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

# Function to retrieve GOES ABI data
# NOTE: Full Disk imagery on this TDS is reduced to 8 kilometer resolution. Other products remain their native size.
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

# Creates a map using Cartopy
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
