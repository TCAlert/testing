import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
from datetime import datetime 
import cgfs as gfs
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(lev = top) - u.sel(lev = bot)
    vShear = v.sel(lev = top) - v.sel(lev = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)


# Returns the upper and lower level that compose this shear vector as integers
def maxShear(u, v):
    #Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    levels = np.arange(200, 900, 50)
    grid = np.meshgrid(levels, levels)

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
    return grid, np.array(shear).reshape(grid[0].shape), np.array(us).reshape(grid[0].shape), np.array(vs).reshape(grid[0].shape)

# Function to put together the whole plot
def finalPlot(hour, lat, lon):
    requests = ['ugrdprs', 'vgrdprs']
    data, mdate, init_hour = gfs.data(requests, hour)
    grid, shear, us, vs = maxShear(data[0].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, data[1].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438)
    mag = (2.5 * (us**2 + vs**2)**0.5)

    # Creates the plot
    fig = plt.figure(figsize=(15, 12))
    ax = plt.axes()
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_ylabel('Pressure (Upper Bound)')
    ax.set_xlabel('Pressure (Lower Bound)')
    ax.grid()
    c = ax.contourf(grid[0], grid[1], shear, cmap = cmap.shear(), levels = np.arange(0, 80, .1), extend = 'max')
    ax.quiver(grid[0], grid[1], us / mag, vs / mag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = 'black', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")])

    mdate = f'{mdate[:4]}-{mdate[4:6]}-{mdate[6:8]}'
    time = (str(data[0].time.values)).split('T')
    time = f'{time[0]} at {(time[1][:5])}z'
    print(time)

    ax.set_title(f'Wind Shear Diagnostics\nInitialization: {mdate} at {init_hour}:00z', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
    ax.set_title('Subtropical Storm DON\nDeelan Jariwala | cyclonicwx.com', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cb.set_ticks(range(0, 85, 5))
    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics.png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

t = datetime.utcnow()
year = t.year
month = t.month
day = 15
hr = 6
hour = xr.Dataset({"time": datetime(year, month, day, hr)})['time'].values
lat = 35.64
lon = 360 - 48.11
finalPlot(hour, lat, lon)