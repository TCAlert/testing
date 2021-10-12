import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
from datetime import datetime 
import cartopy.feature as cfeature
import urllib.request as urllib

def retrieveData(storm, year = datetime.year):
  if year == datetime.year:
    link = f'https://ftp.nhc.noaa.gov/atcf/btk/b{storm}{year}.dat'
  else:
    link = f'https://ftp.nhc.noaa.gov/atcf/archive/{year}/b{storm}{year}.dat.gz'
  
  data = (urllib.urlopen(link).read().decode('utf-8')).split('\n')
    
def map(e, w, s, n, size):
    plt.figure(figsize = size)

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_extent([e, w, s, n])

    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 1)
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude=0), zorder = 9, draw_labels = True, linewidth = 0.5, color='white', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False 
    return ax

