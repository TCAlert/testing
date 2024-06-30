import matplotlib.pyplot as plt  # Plotting library
import numpy as np
from datetime import datetime 
import gefsRetrieve as gefs
import cmaps as cmap 
from matplotlib import patheffects
from matplotlib.offsetbox import AnchoredText
import adeck 
import xarray as xr 
from matplotlib import rcParams
rcParams['font.family'] = 'Courier New'

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(lev = top) - u.sel(lev = bot)
    vShear = v.sel(lev = top) - v.sel(lev = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

def std(dataset):
    dev = []
    average = np.mean(dataset, axis = 0)
    for x in range(0, 30):
        temp = dataset[x]
        dev.append((average - temp)**2)
    stddev = np.sqrt(np.mean(dev, axis = 0))

    return stddev

# Calculates percentiles
# `data` is a 3D array containing the computed wind shears from each member of the GEFS 
# `num` is the desired percentile (Ex: 10, 25, 50, 75, 90)
def percentile(data, num):
    # Extracts dimensions of data and calculates the numeric value that the percentile best corresponds to
    depth = len(data)
    rows = len(data[0])
    cols = len(data[0][0])
    num = int(num / 100 * depth)
       
    listOfListOfDepths = []
    for z in range(cols):
        listOfDepths = []
        for y in range(rows):
            depths = []
            for x in range(depth):
                # Appends all data that belongs to a given depth slice to a list (`depths`) 
                depths.append(data[x][z][y])
            # Sorts each depth slice and selects the value that best corresponds to the given percentile
            if num % 2 == 0:
                listOfDepths.append((sorted(depths)[num] + sorted(depths)[num - 1]) / 2)
            else:
                listOfDepths.append(sorted(depths)[num])
        listOfListOfDepths.append(listOfDepths)
        # Remainder of loop reconstructs the 2D array (`rows` x `cols`), now containing percentile data

    return listOfListOfDepths

# Calculates all the possible shear layers
def allShear(u, v, levels):
    # Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    # Also define a grid of these levels -- will be used later

    # Calculate the shear magnitudes and append it to the blank list, as well as the U and V components of the vectors
    # Note that we are calculating shear as the difference between the upper and lower bound here (top - bottom)
    # To prevent redundancies, anything else is set to 0
    shear = []
    for x in range(len(levels)):
        uShear, vShear = calcShear(u, v, levels[x][0], levels[x][1])
        shear.append(shearMag(uShear, vShear))

    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using  the 2D grid  
    return shear

# Sample usage
t = datetime.now()
year = t.year
month = t.month
day = t.day 
hr = 6
fcastHour = 90
storm = 'al02'
levels = [[200, 850], [500, 850], [200, 500]]

# Collects requisite information from the A-Deck regarding the given storm for the specified hour and models
# Additionally retrieves the U and V wind data for the GEFS corresponding to the same time and run
adeckDF = adeck.filterData(storm, [f'{year}{str(month).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}'], ['AP01', 'AP02', 'AP03', 'AP04', 'AP05', 'AP06', 'AP07', 'AP08', 'AP09', 'AP10', 'AP11', 'AP12', 'AP13', 'AP14', 'AP15', 'AP16', 'AP17', 'AP18', 'AP19', 'AP20', 'AP21', 'AP22', 'AP23', 'AP24', 'AP25', 'AP26', 'AP27', 'AP28', 'AP29', 'AP30', 'AP31'], [fcastHour])
print(str(len(adeckDF)) + " Members Found.")
print(adeckDF)
data, init = gefs.getData(['ugrdprs', 'vgrdprs'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
#init = '2024-04-06 at 00:00z'
print(init)
#data[0].to_netcdf(r"C:\Users\deela\Downloads\uData627202418.nc")
#data[1].to_netcdf(r"C:\Users\deela\Downloads\vData627202418.nc")
#data = [xr.open_dataset(r"C:\Users\deela\Downloads\uData627202418.nc")['ugrdprs'], xr.open_dataset(r"C:\Users\deela\Downloads\vData627202418.nc")['vgrdprs']]

# Calculate wind shears for each member of the GEFS
shears = []
for x in range(1, 31):
    # Selects GEFS member from the A-Deck and retrieves latitudes and longitudes 
    member = adeckDF.iloc[x - 1]
    uData, vData = data[0].sel(ens = x + 1), data[1].sel(ens = x + 1)
    lon, lat = member[7], member[6]
    if lon < 0:
        lon = lon + 360
    
    # Subsets a 5x5 degree box centered on the storm and computes the average for all pressure levels
    # This data (both the zonal and meridional component of the wind vector) is then passed to the function to compute wind shears throughout the column
    # The values returned are then appended to lists to form the 3D matrices     
    shear = allShear(uData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, vData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, levels)
    shears.append(shear)

nShears = []
for x in range(len(shears[0])):
    temp = []
    for y in range(len(shears)):
        temp.append(shears[y][x])
    nShears.append(temp)
shears = np.array(nShears)
print(shears)

# Calculate histogram
hist = []
for x in range(len(shears)):
    h, bins = np.histogram(shears[x], bins = [x for x in range(0, 55, 5)])
    hist.append((h / len(shears[x])) * 100)

fig = plt.figure(figsize=(12, 8))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)

# Add state boundaries to plot
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Percent of GEFS Members', weight = 'bold', size = 9)
ax.set_xlabel('Wind Shear (kts)', weight = 'bold', size = 9)

plt.plot(bins[:-1], hist[0], color = 'red', label = 'Deep  (200-850mb)')
plt.fill_between(bins[:-1], hist[0], 0, color='red', alpha=.1)
plt.plot(bins[:-1], hist[1], color = 'blue', label = 'Mid   (500-850mb)')
plt.fill_between(bins[:-1], hist[1], 0, color='blue', alpha=.1)
plt.plot(bins[:-1], hist[2], color = 'green', label = 'Upper (200-500mb)')
plt.fill_between(bins[:-1], hist[2], 0, color='green', alpha=.1)
plt.legend()

time = (str(data[0].time.values)).split('T')
time = f'{time[0]} at {(time[1][:5])}z'

ax.set_title(f'GEFS Distribution of Vertical Wind Shear: {storm.upper()}\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

plt.savefig(r"C:\Users\deela\Downloads\gefsdist.png", dpi = 400, bbox_inches = 'tight')

plt.show()