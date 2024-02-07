import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
from datetime import datetime 
import gefsRetrieve as gefs
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.offsetbox import AnchoredText
import adeck 

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(lev = top) - u.sel(lev = bot)
    vShear = v.sel(lev = top) - v.sel(lev = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

def percentile(data, num):
    dim1 = len(data)
    dim2 = len(data[0])
    dim3 = len(data[0][0])
    num = int(num / 100 * len(data))
    print(num)

    listOfListOfColumns = []
    for z in range(dim3):
        listOfColumns = []
        for y in range(dim2):
            columns = []
            for x in range(dim1):
                columns.append(data[x][z][y])
            if num % 2 == 0:
                listOfColumns.append((sorted(columns)[num] + sorted(columns)[num - 1]) / 2)
            else:
                listOfColumns.append(sorted(columns)[num])
        listOfListOfColumns.append(listOfColumns)
    print(listOfListOfColumns)

    return listOfListOfColumns

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
def finalPlot(grid, shear, init, title, us = None, vs = None):
    # Creates the plot
    fig = plt.figure(figsize=(15, 12))
    ax = plt.axes()
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_ylabel('Pressure (Upper Bound)')
    ax.set_xlabel('Pressure (Lower Bound)')
    ax.grid()

    try:
        if us == None:
            c = ax.pcolormesh(grid[0], grid[1], shear, cmap = cmap.probs(), vmin = 0, vmax = 100)
            cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
            cb.set_ticks(range(0, 105, 5))
    except:    
        # Plots the data using the pressure level grid created before
        # Note that the vectors in the plot are normalized by the magnitude of the shear
        mag = (2.5 * (us**2 + vs**2)**0.5)
        c = ax.contourf(grid[0], grid[1], shear, cmap = cmap.shear(), levels = np.arange(0, 80, .1), extend = 'max')
        ax.quiver(grid[0], grid[1], us / mag, vs / mag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = 'black', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")])
        cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
        cb.set_ticks(range(0, 85, 5))
    time = (str(data[0].time.values)).split('T')
    time = f'{time[0]} at {(time[1][:5])}z'

    ax.set_title(f'GEFS Vertical Wind Shear Distribution: SH95\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
    ax.set_title(f'{title}\nDeelan Jariwala | cyclonicwx.com', fontsize=10, loc='right') 
    at = AnchoredText("Inspired by Michael Fischer",
                  prop=dict(size=8, color = 'gray'), frameon=False,
                  loc=4)
    at.patch.set_alpha(.1)
    ax.add_artist(at)

    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics_" + title + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

# Sample usage
t = datetime.now()
year = t.year
month = t.month
day = t.day
hr = 18
fcastHour = 120
storm = 'sh94'
shearStrength = 15
p = 10
#title = f'Percent of Members with Shear >{shearStrength}kt'
#title = 'Minimum Shear in Ensemble Suite'
#title = 'Interquartile Range'
title = 'Probability a Layer has the Max Shear Vector'
#title = f'{p}th Percentile of Wind Shears'

adeckDF = adeck.filterData(storm, [f'{year}{str(month).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}'], ['AP01', 'AP02', 'AP03', 'AP04', 'AP05', 'AP06', 'AP07', 'AP08', 'AP09', 'AP10', 'AP11', 'AP12', 'AP13', 'AP14', 'AP15', 'AP16', 'AP17', 'AP18', 'AP19', 'AP20', 'AP21', 'AP22', 'AP23', 'AP24', 'AP25', 'AP26', 'AP27', 'AP28', 'AP29', 'AP30', 'AP31'], [fcastHour])
print(adeckDF)
data, init = gefs.getData(['ugrdprs', 'vgrdprs'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
shears = []
us = []
vs = []
for x in range(1, 31):
    member = adeckDF.iloc[x - 1]
    uData, vData = data[0].sel(ens = x + 1), data[1].sel(ens = x + 1)
    lon, lat = member[7], member[6]
    if lon < 0:
        lon = lon + 360
    grid, shear, u, v = allShear(uData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, vData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438)
    shears.append(shear)
    us.append(u)
    vs.append(v)

if title == 'Ensemble Mean':
    shears = sum(shears) / len(shears)
    us = sum(us) / len(us)
    vs = sum(vs) / len(vs)
elif title == 'Maximum Shear in Ensemble Suite':
    shears = np.nanmax(shears, axis = 0)
    us = sum(us) / len(us)
    vs = sum(vs) / len(vs)
elif title == 'Minimum Shear in Ensemble Suite':
    shears = np.nanmin(shears, axis = 0)
    us = sum(us) / len(us)
    vs = sum(vs) / len(vs)
elif title == 'Probability a Layer has the Max Shear Vector':
    for x in range(len(shears)):
        shears[x] = np.where(shears[x] == np.nanmax(shears[x]), 1, 0)
    shears = (np.sum(shears, axis = 0) / len(shears)) * 100
    us = vs = None
elif title == f'Percent of Members with Shear >{shearStrength}kt':
    for x in range(len(shears)):
        shears[x] = np.where(shears[x] > shearStrength, 1, 0)
    shears = (np.sum(shears, axis = 0) / len(shears)) * 100
    us = vs = None    
elif title == f'{p}th Percentile of Wind Shears':
    shears = percentile(shears, p)
    us = sum(us) / len(us)
    vs = sum(vs) / len(vs)
elif title == f'Interquartile Range':
    shears = np.array(percentile(shears, 75)) - np.array(percentile(shears, 25))
    us = sum(us) / len(us)
    vs = sum(vs) / len(vs)
finalPlot(grid, shears, init, title, us, vs)