import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import math 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import cmaps as cmap 
import xarray as xr 
from helper import numToMonth

pd.options.mode.chained_assignment = None

basin = 'AL'
climoYears = np.arange(1851, 2024)
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
bounds = [-120, 0, 0, 70]
interval = 3

if basin == 'EP':
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
else:
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

link = urlopen(link)
soup = BeautifulSoup(link, 'html.parser')
lines = soup.get_text().split('\n')

# Helper Functions
class helper():
    def distance(a, b):
        try:
            R = 3443.92
            latA = a[0] * math.pi / 180 
            lonA = a[1] * math.pi / 180
            latB = b[0] * math.pi / 180
            lonB = b[1] * math.pi / 180
            d = R * math.acos(math.cos(latA) * math.cos(latB) * math.cos(lonA - lonB) + (math.sin(latA) * math.sin(latB)))
        except:
            d = 0

        return d 

    def ACE(data, status):
        wind = data.astype(int)
        status = status
        total = []
        for x in range(len(wind)):
            if status[x].strip() in ['SS', 'TS', 'HU']:
                ace = wind[x]**2 / 10000
                total.append(round(ace, 2))
            else:
                total.append(0)
        return total#np.cumsum(total) 

# Loop through HURDAT2 and separate it into a list of lists containing storm data
def getData(year):
    storms = []
    for x in range(len(lines)):
        temp = lines[x].split(',')
        if basin in temp[0] and int(temp[0][4:8]) in year:
            advNum = int(temp[2])
            stormData = lines[x + 1 : x + advNum]
            for y in range(len(stormData)):
                stormData[y] = (f'{temp[0]},' + (stormData[y][:71])).split(',')
            storms.append(stormData)
            x += advNum
    return storms 

# Filter storm data by month
def filterByMonth(storms, months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']):
    stormsToReturn = []
    for x in range(len(storms)):
        try:
            if storms[x][0][1][4:6] in months:
                stormsToReturn.append(storms[x])
        except:
            pass
    return stormsToReturn

# Convert each array to a Pandas Dataframe for ease of use, as well calculating additional parameters
def stormObjects(l):
    for x in range(len(l)):
        l[x] = pd.DataFrame(l[x], columns = ['ID', 'Date', 'Time', 'L', 'Status', 'Latitude', 'Longitude', 'Wind', 'MSLP', 'R34NE', 'R34SE', 'R34NW', 'R34SW'])        
        l[x] = l[x].drop(l[x][l[x].Time.astype(int) % 600 != 0].index)
        l[x] = l[x].drop('L', axis = 1)
        l[x].index = range(len(l[x]))
        l[x].Latitude = ((l[x].Latitude).str[:-1]).astype(float)
        l[x].Longitude = ((l[x].Longitude).str[:-1]).astype(float) * -1
        l[x].Wind = (l[x].Wind).astype(int)
        l[x].MSLP = (l[x].MSLP).astype(int)
        l[x].Status = (l[x].Status).str.strip()
        l[x].R34NE = (l[x].R34NE).astype(int)
        l[x].R34SE = (l[x].R34SE).astype(int)
        l[x].R34NW = (l[x].R34NW).astype(int)
        l[x].R34SW = (l[x].R34SW).astype(int)

        change = []
        ri = []
        r34 = []
        speed = []
        for y in range(len(l[x]['Wind'])):
            l[x]['ID'][y] = f'{l[x]["ID"][y][0:4]}{l[x]["Date"][y][0:4]}'
            l[x]['Time'][y] = np.datetime64(f'{l[x]["Date"][y][0:4]}-{l[x]["Date"][y][4:6]}-{l[x]["Date"][y][6:8]}T{l[x]["Time"][y][1:3]}')
            #try:
            if l[x]['Wind'][y] > 34:
                r34.append((l[x]['R34NE'][y] + l[x]['R34SE'][y] + l[x]['R34NW'][y] + l[x]['R34SW'][y]) / 4)
            else:
                r34.append(0)
            
            if (y - 4 >= 0) and ((l[x]['Wind'][y] - l[x]['Wind'][y - 4]) >= 30):
                ri.append(True)
            else:
                ri.append(False)
            
            if (y - 1) >= 0:
                d = helper.distance([l[x]['Latitude'][y], l[x]['Longitude'][y]], [l[x]['Latitude'][y - 1], l[x]['Longitude'][y - 1]])
                speed.append(round(d / 6, 1))
            else:
                speed.append(np.nan)

            if (y - 4) >= 0:
                change.append(l[x]['Wind'][y] - l[x]['Wind'][y - 4])
            else:
                change.append(0)
            #except:
            #    speed.append(np.nan)
            #    change.append(0)
            #    ri.append(False)

        l[x] = l[x].drop('Date', axis = 1)
        l[x]['Speed'] = speed
        l[x]['24hrChange'] = change
        l[x]['RI'] = ri
        l[x]['R34'] = r34
        l[x]['VR'] = l[x]['Wind'] / l[x]['R34']
        l[x]['ACE'] = helper.ACE(l[x]['Wind'], l[x]['Status'])
    return l

def database(climo, months):
    storms = getData(climo)
    storms = filterByMonth(storms, months)
    storms = stormObjects(storms)
    print(len(storms))

    return storms

# Calculates all the possible shear layers
def gridData(data, bounds):
    # Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    # Also define a grid of these levels -- will be used later
    lats = np.arange(bounds[2], bounds[3] + interval, interval)
    lons = np.arange(bounds[0], bounds[1] + interval, interval)
    grid = np.meshgrid(lats, lons)

    # Place HURDAT2 datapoints into latitude/longitude bins to compute density
    bins = []
    for x in range(len(lons)):
        for y in range(len(lats)):
            binStorm = 0
            for z in range(len(data)):
                temp = data[z]
                for w in range(len(temp)):
                    try:
                        if temp['Latitude'][w] > lats[y] and temp['Latitude'][w] < lats[y + 1] and temp['Longitude'][w] > lons[x] and temp['Longitude'][w] < lons[x + 1]:
                            #binStorm += temp['ACE'][w]
                            #binStorm += 1
                            #if temp['RI'][w] == True:
                            #    binStorm += 1            
                            binStorm += temp['24hrChange'][w]
                        else:
                            binStorm += 0
                    except:
                        pass
            bins.append(binStorm)

    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using  the 2D grid  
    return grid, np.array(bins).reshape(grid[0].shape)

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

# Sample Usage:
# Pass processed database to retrieveStorm function with necessary inputs
# Returns dictionary with storm information and a few basic charts
dataset = []
times = []
for x in range(len(climoYears)):
    for y in range(len(months)):
        print(months[y], climoYears[x])
        climo = database([climoYears[x]], [months[y]])
        grid, climo = gridData(climo, bounds)
        climo = climo / (interval**2)
        dataset.append(climo)
        times.append(np.datetime64(f'{climoYears[x]}-{months[y]}-01T00'))

        #ax = map(6, 9)
        #c = plt.contourf(grid[1], grid[0], climo, cmap = cmap.probs(), levels = np.arange(0, 1, .01), extend = 'both')
        #ax.set_title(f'HURDAT2 Track Density\n{numToMonth(int(months[y]))} {climoYears[x]}', fontweight='bold', fontsize=9, loc='left')
        #ax.set_title(f'{interval}\u00b0x{interval}\u00b0 Bins\nDeelan Jariwala', fontsize=9, loc='right') 
        #cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
        #cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
        #plt.savefig(r"C:\Users\deela\Downloads\density\\" + months[y] + "_" + str(climoYears[x]) + ".png", dpi = 400, bbox_inches = 'tight')
        #plt.show()
        #plt.close()

print(np.array(dataset).shape)
ds = xr.DataArray(dataset,coords={"time": times, "latitude": (["x","y"], grid[0]),
                          "longitude": (["x","y"], grid[1])},
                  dims=["time", "x","y"], name = '24hrChangeDensity')

ds.to_netcdf(r"C:\Users\deela\Downloads\\24hrChangeDensity.nc")

