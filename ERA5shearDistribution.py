import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
from datetime import datetime 
import gfsRetrieve as gfs
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.offsetbox import AnchoredText
import cdsapi as cds 

c = cds.Client()

def retrieve(type, level, date, lat, lon): 
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type'  : 'reanalysis',
            'variable'      : type,
            'pressure_level': level,
            'year'          : f'{date[0]}',
            'month'         : f'{date[1]}',
            'day'           : f'{date[2]}',
            'time'          : f'{date[3]}:00',
            'format'        : 'netcdf',                 # Supported format: grib and netcdf. Default: grib
            'area'          : [lat + 5, lon - 5, lat - 5, lon + 5], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

labelsize = 8 
year = 2017
month = 9
day = 5
hour = 18
level = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
lat, lon = 16.9, -59.2
date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
#retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
print(data)
uData = (data['u'].sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5))).mean(['latitude', 'longitude']).squeeze()
vData = (data['v'].sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5))).mean(['latitude', 'longitude']).squeeze()

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(level = top) - u.sel(level = bot)
    vShear = v.sel(level = top) - v.sel(level = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

# Calculates all the possible shear layers
def allShear(u, v):
    # Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    # Also define a grid of these levels -- will be used later
    levels = np.arange(200, 900, 50)
    grid = np.meshgrid(levels, levels)

    # Calculate the shear magnitudes and append it to the blank list, as well as the U and V components of the vectors
    # Note that we are calculating shear as the difference between the upper and lower bound here (top - bottom)
    # To prevent redundancies, anything else is set to 0
    shear = []
    us = []
    vs = []
    for x in levels:
        for y in levels:
            if y > x:
                uShear, vShear = calcShear(u, v, x, y)
                shear.append(shearMag(uShear, vShear))
                us.append(uShear) 
                vs.append(vShear)
            else:
                shear.append(0)
                us.append(0)
                vs.append(0)
    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using  the 2D grid  
    return grid, np.array(shear).reshape(grid[0].shape), np.array(us).reshape(grid[0].shape), np.array(vs).reshape(grid[0].shape)

# Function to put together the whole plot
def finalPlot(hour):
    grid, shear, us, vs = allShear(uData * 1.9438, vData * 1.9438)
    mag = (2.5 * (us**2 + vs**2)**0.5)

    # Creates the plot
    fig = plt.figure(figsize=(15, 12))
    ax = plt.axes()
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_ylabel('Pressure (Upper Bound)')
    ax.set_xlabel('Pressure (Lower Bound)')
    ax.grid()

    # Plots the data using the pressure level grid created before
    # Note that the vectors in the plot are normalized by the magnitude of the shear
    c = ax.contourf(grid[0], grid[1], shear, cmap = cmap.shear(), levels = np.arange(0, 80, .1), extend = 'max')
    ax.quiver(grid[0], grid[1], us / mag, vs / mag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = 'black', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")])

    ax.set_title(f'Vertical Wind Shear Distribution\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Hurricane IRMA', fontsize = 10, loc = 'center')
    ax.set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 
    at = AnchoredText("Inspired by Michael Fischer",
                  prop=dict(size=8, color = 'gray'), frameon=False,
                  loc=4)
    at.patch.set_alpha(.1)
    ax.add_artist(at)
    cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cb.set_ticks(range(0, 85, 5))
    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics.png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

# Sample usage
finalPlot(hour)