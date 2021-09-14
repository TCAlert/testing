from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
from siphon.catalog import TDSCatalog
import xarray as xr 
import goesRequest as goes
import cgfs as gfs 
import cmaps as cmap
import bdeck as bdeck 
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import urllib.request as urllib
import math 
from matplotlib.offsetbox import AnchoredText
from datetime import datetime
import goesRequest2 as goes2
import pandas as pd

usage = '```$glm [storm (Best Track ID)]```'

def bold(string):
    string = r"$\bf{" + string + "}$" + " "
    return string

def archer(storm):
    if 'al' in storm.lower():
        storm = storm[2:4] + 'L'
    else:
        storm = storm[2:4] + 'E'
    
    link = f'http://tropic.ssec.wisc.edu/real-time/adt/ARCHER/listings/{storm}-summary.txt'
    data = pd.read_fwf(link, skiprows = 1)

    lat = data['Lat.1'].iloc[-1]
    lon = 360 - data['Lon.1'].iloc[-1]

    return lat, lon

#print(archer('al09'))

def ships(storm):
    year = (str(datetime.utcnow().year))[2:4]
    mon = (str(datetime.utcnow().month)).zfill(2)
    day = (str(datetime.utcnow().day)).zfill(2)
    for x in ['18', '12', '06', '00']:
        try:
            link = f'https://ftp.nhc.noaa.gov/atcf/stext/{year}{mon}{day}{x}{storm.upper()}{year}_ships.txt'
            data = urllib.urlopen(link).read().decode('utf-8')
            break
        except:
            continue 
    line = data.split("\n") 
    
    shear = ([x for x in (line[11]).split(' ') if x])[2]
    direc = ([x for x in (line[13]).split(' ') if x])[2]

    u = -1 * float(shear) * math.sin((math.pi/180) * float(direc))
    v = -1 * float(shear) * math.cos((math.pi/180) * float(direc))

    return (u, v, shear, direc)

def run(storm):
    lat, lon = archer(storm)
    rmwval = bdeck.rmw(storm)
    u, v, shear, direc = ships(storm)

    if int(lon) > 255:
        satellite = '16'
    else:
        satellite = '17'
    band = '13'
    mini = -110
    maxi = 40
    region = 'FullDisk'

    bounds = [lon - 5, lon + 5, lat - 5, lat + 5]
    #bounds = [lon - 70, lon + 70, lat - 70, lat + 70]

    try:
        data, center, info, time = goes2.getData(satellite, band)
        ax = goes2.makeMap(bounds, (18, 9))
        plt.imshow(data, origin = 'upper', vmin = 200, vmax = 310, cmap = 'Greys', transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))

    except:
        if int(lon) > 255:
            satellite = 'East'
        else:
            satellite = 'West'
        data, time, info, center = goes.getData(satellite.lower(), band, 'FullDisk')
        ax = goes.makeMap(bounds, (18, 9))
        plt.imshow(data, origin = 'upper', vmin = 200, vmax = 310, cmap = 'Greys', transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))

    #print('IR plotted')
    data, ltime = goes.getLightning('east', 'FullDisk', 'flash_extent_density')
    plt.imshow(data, origin = 'upper', cmap = 'BuPu_r', vmin = 0, vmax = 25, transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0))#, interpolation = 'Gaussian')
    #print('Lightning plotted')
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)

    rmw = plt.Circle((lon, lat), rmwval/60, edgecolor = 'black', fill = False, linewidth = 4, linestyle = '--', transform = ccrs.PlateCarree(central_longitude=0))
    for x in [100, 200, 300]:
        circ = plt.Circle((lon, lat), (x/1.852)/60, edgecolor = 'black', fill = False, linewidth = 1, transform = ccrs.PlateCarree(central_longitude=0))
        ax.add_artist(circ)
        plt.text(lon, lat - (x/1.852)/60 - 0.4, f"{str(x)}km", ha = 'center', transform = ccrs.PlateCarree(central_longitude=0))

    plt.quiver(lon, lat, u, v, transform = ccrs.PlateCarree(central_longitude=0))
    plt.text(lon, lat + rmwval/60 + 0.2, "RMW", ha = 'center', transform = ccrs.PlateCarree(central_longitude=0))

    ax.add_artist(rmw)

    at = AnchoredText(f"Idea taken from Stevensons et al. 2018\nhttps://doi.org/10.1175/WAF-D-17-0096.1",
                  prop=dict(size=8, color = 'white'), frameon=True,
                  loc=2)
    at.patch.set_boxstyle("square")
    at.patch.set_edgecolor('black')
    at.patch.set_facecolor('gray')
    at.patch.set_alpha(.2)
    ax.add_artist(at)

    plt.title(f'GOES {satellite} Channel {band.zfill(2)} {info} and GLM Flash Extent Density\nSatellite Image: {time} | GLM Frame: {ltime}' , fontweight='bold', fontsize=10, loc='left')
    plt.title('TCAlert', fontsize=10, loc='right')
    plt.legend(title = f'{bold("Data")}{bold("from")}{bold("SHIPS")}\nShear (kts): {shear}\nShear (°): {direc}\nCentered at: {str(round(float(lat), 2))}N, {str(round(float(lon), 2))}E', fancybox = True, shadow = True)
    plt.savefig(r"C:\Users\Jariwala\Downloads\stevenson2018iclbplot.png", dpi = 100, bbox_inches = 'tight')
    #plt.show()
    plt.close()
#run('al09')