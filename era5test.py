import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import cdsapi as cds
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import xarray as xr 
import satcmaps as scmaps 

c = cds.Client()

def retrieve(type, level, date, lat, lon): 
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type'  : 'reanalysis',
            'variable'      : f'{type}',
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
#retrieve('Vorticity', level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
data = (data['vo'].mean(['latitude', 'longitude'])).squeeze()
#data = (data['z']).squeeze() / 98.0665
print(data)

# Calculates all the possible shear layers
def allShear():
    # Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    # Also define a grid of these levels -- will be used later
    levels = np.arange(200, 1050, 50)
    grid = np.meshgrid(levels, levels)

    # Calculate the shear magnitudes and append it to the blank list, as well as the U and V components of the vectors
    # Note that we are calculating shear as the difference between the upper and lower bound here (top - bottom)
    # To prevent redundancies, anything else is set to 0
    thickness = []
    for x in levels:
        for y in levels:
            if y >= x:
                thickness.append(data.sel(level = y) - data.sel(level = x))
            else:
                thickness.append(-1.5)
    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using the 2D grid  
    return grid, np.array(thickness).reshape(grid[0].shape)

# Function to put together the whole plot
def finalPlot():
    grid, thickness = allShear()

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
    c = ax.contourf(grid[0], grid[1], thickness * 100000, cmap = cmap.shear(), levels = np.arange(-1.5, 9.6, .1), extend = 'max')

    ax.set_title(f'ERA5: Vorticity Distribution\nDate: {date}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Centered at {lat}N, {lon * -1}W', fontsize = 10, loc = 'center')
    ax.set_title('Deelan Jariwala', fontsize=10, loc='right') 
    cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    #cb.set_ticks(range(-1.5, 10, .5))
    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics.png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

finalPlot()