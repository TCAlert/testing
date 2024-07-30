import matplotlib.pyplot as plt  # Plotting library
import numpy as np
from datetime import datetime 
import gefsRetrieve as gefs
import cmaps as cmap 
from matplotlib import patheffects
from matplotlib.offsetbox import AnchoredText
import adeck 
import xarray as xr 
import matplotlib.patheffects as pe
import scipy.stats as stats

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(lev = top) - u.sel(lev = bot)
    vShear = v.sel(lev = top) - v.sel(lev = bot)
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
    for x in levels:
        for y in levels:
            if y > x:
                uShear, vShear = calcShear(u, v, x, y)
                shear.append(shearMag(uShear, vShear))
            else:
                shear.append(0)
        
    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using the 2D grid  
    return grid, np.array(shear).reshape(grid[0].shape)

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

    # Plots the data using the pressure level grid created before
    # This section plots probabilistic data
    c = ax.pcolormesh(grid[0], grid[1], shear, cmap = cmap.tempAnoms3(), vmin = -1, vmax = 1)
    cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cb.set_ticks(np.arange(-1, 1.1, .1))
    cb.set_label(title)

    for x in range(len(grid[0])):
        for y in range(len(grid[1])):
            if shear[x][y] != 0:
                plt.text(grid[0][x][y], grid[1][x][y], f'{"{:.2f}".format(shear[x][y], 2)}', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

    time = (str(data[0].time.values)).split('T')
    time = f'{time[0]} at {(time[1][:5])}z'

    ax.set_title(f'GEFS Vertical Wind Shear Distribution: AL95\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
    ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 
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
fcastHour = 48
fcastHour2 = 6
storm = 'AL02'
shearStrength = 15
p = 50

title = f'Correlation with FH{fcastHour2} Intensity'

# Collects requisite information from the A-Deck regarding the given storm for the specified hour and models
# Additionally retrieves the U and V wind data for the GEFS corresponding to the same time and run
adeckDF = adeck.filterData(storm, [f'{year}{str(month).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}'], ['AP01', 'AP02', 'AP03', 'AP04', 'AP05', 'AP06', 'AP07', 'AP08', 'AP09', 'AP10', 'AP11', 'AP12', 'AP13', 'AP14', 'AP15', 'AP16', 'AP17', 'AP18', 'AP19', 'AP20', 'AP21', 'AP22', 'AP23', 'AP24', 'AP25', 'AP26', 'AP27', 'AP28', 'AP29', 'AP30', 'AP31'], [fcastHour])
adeckDFFH = adeck.filterData(storm, [f'{year}{str(month).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}'], ['AP01', 'AP02', 'AP03', 'AP04', 'AP05', 'AP06', 'AP07', 'AP08', 'AP09', 'AP10', 'AP11', 'AP12', 'AP13', 'AP14', 'AP15', 'AP16', 'AP17', 'AP18', 'AP19', 'AP20', 'AP21', 'AP22', 'AP23', 'AP24', 'AP25', 'AP26', 'AP27', 'AP28', 'AP29', 'AP30', 'AP31'], [fcastHour2])
print(adeckDF, adeckDFFH)
intensities = np.array(adeckDFFH[8].astype('Float64'))

data, init = gefs.getData(['ugrdprs', 'vgrdprs'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
#init = '2024-06-29 at 12:00z'
print(init)
#data[0].to_netcdf(r"C:\Users\deela\Downloads\uData.nc")
#data[1].to_netcdf(r"C:\Users\deela\Downloads\vData.nc")
#data = [xr.open_dataset(r"C:\Users\deela\Downloads\uData629202412.nc")['ugrdprs'], xr.open_dataset(r"C:\Users\deela\Downloads\vData629202412.nc")['vgrdprs']]
print(data)

# Calculate wind shears for each member of the GEFS
shears = []
for x in range(1, 31):
    # Selects GEFS member from the A-Deck and retrieves latitudes and longitudes 
    member = adeckDF.iloc[x - 1]
    uData, vData = data[0].sel(ens = x + 1), data[1].sel(ens = x + 1)
    lon, lat = member[7], member[6]
    if lon < 0:
        lon = lon + 360
    
    # tU = uData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5), lev = 850)
    # tV = vData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5), lev = 850)
    # plt.imshow(tU)
    # plt.show()    

    # Subsets a 5x5 degree box centered on the storm and computes the average for all pressure levels
    # This data (both the zonal and meridional component of the wind vector) is then passed to the function to compute wind shears throughout the column
    # The values returned are then appended to lists to form the 3D matrices     
    grid, shear = allShear(uData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, vData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438)
    shears.append(shear)

# Simple average of all ensemble members
if title == f'Correlation with FH{fcastHour2} Intensity':
    shears = np.array(shears)
    shearsShape = shears.shape
    shears = shears.reshape(shearsShape[0], shearsShape[1] * shearsShape[2])

    corrData = []
    signData = []
    for x in range(shears.shape[1]):
        shears[:, x] = np.nan_to_num(shears[:, x])
        corr, sig = stats.pearsonr(shears[:, x], intensities)
        corrData.append(corr)
        signData.append(sig)

    corrData = np.nan_to_num(np.array(corrData))
    shears = np.array(corrData).reshape(shearsShape[1], shearsShape[2])

# Runs program
finalPlot(grid, shears, init, title)