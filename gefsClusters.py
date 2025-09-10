import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import numpy as np
from datetime import datetime 
import gefsRetrieve as gefs
import cmaps as cmap 
from matplotlib import patheffects
from matplotlib.offsetbox import AnchoredText
import adeck 
import xarray as xr 
import matplotlib.patheffects as pe
from sklearn.cluster import KMeans
import cartopy.mpl.geoaxes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy import stats

def map(ax, interval, labelsize = 9):
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

# Create a map using Cartopy
def mapBig(interval, labelsize):
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

def findClusters(adeck, data, num):
    data = np.reshape(data, (len(data), 1))
    clusters = KMeans(n_clusters = num).fit(data)
    labels = clusters.labels_
    centroids = clusters.cluster_centers_

    clusters = []
    for x in range(num):
        clusters.append(adeck[labels == x])

    return clusters, centroids

# Function to put together the whole plot
def finalPlot(grid, init, title, clusterType, clusters, hs = None, hgt = 500):
    print(hs)

    ax = mapBig(10, 8)
    c = plt.contourf(grid[0], grid[1], hs, cmap = cmap.tempAnoms(), levels = np.arange(-50, 51, 1), extend = 'both')
    cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    cb.ax.text(-.5, 0.825, "Cluster 1 higher", fontsize=8, rotation = 90, fontweight = 'bold', ha='center', color='black', transform=cb.ax.transAxes)
    cb.ax.text(-.5, 0.025, "Cluster 1 lower", fontsize=8, rotation = 90, fontweight = 'bold', ha='center', color='black', transform=cb.ax.transAxes)

    inset = inset_axes(ax, width = "85%", height= "85%", borderpad = 1, bbox_to_anchor=(0.50, 0.05, 0.70, 0.35), bbox_transform=ax.transAxes, loc="lower right", 
                axes_class=cartopy.mpl.geoaxes.GeoAxes, 
                axes_kwargs=dict(map_projection=cartopy.crs.PlateCarree()))

    clusters, centroids = clusters
    lats, lons = [], []
    for x in range(len(clusters)):
        #print(f'Cluster {x + 1} Winds: {np.mean(clusters[x][8])}')
        lats += (list(clusters[x][6]))
        lons += (list(clusters[x][7]))
        inset.scatter(clusters[x][7], clusters[x][6], label = f'Cluster {x + 1}: {round(centroids[x][0], 1)}')
        inset.legend(fontsize = 7)
        inset.set_title('Spatial Map of Clusters', fontsize = 9)

    extent = np.nanmax([round(np.nanmax(lons) - np.nanmin(lons)), round(np.nanmax(lats) - np.nanmin(lats))]) * 1.5
    map(inset, extent / 4, 5)
    inset.set_extent([np.mean(lons) - (extent / 2), np.mean(lons) + (extent / 2), np.mean(lats) - (extent / 2), np.mean(lats) + (extent / 2)])

    time = (str(data[0].time.values)).split('T')
    print(time)
    time = f'{time[0]} at {(time[1][:5])}z'

    ax.set_title(f'GEFS {hgt}mb Geopotential Height Cluster Difference: AL05\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
    ax.set_title(f'Data split by {clusterType.upper()}: Cluster 1 - 2 Plotted\nDeelan Jariwala', fontsize=10, loc='right') 
    # at = AnchoredText("Inspired by Michael Fischer",
    #               prop=dict(size=8, color = 'gray'), frameon=False,
    #               loc=4)
    # at.patch.set_alpha(.1)
    # ax.add_artist(at)

    plt.savefig(r"C:\Users\deela\Downloads\ensembleDiagnostics_" + clusterType + title + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

# Sample usage
t = datetime.now()
year = t.year
month = t.month
day = 13#t.day
hr = 18
fcastHour = 120
storm = 'al05'
shearStrength = 15
p = 50
height = 500
numClusters = 2
clusterType = 'Longitude'
#title = f'Percent of Members with Shear Exceeding {shearStrength}kt'
#title = f'{p}th Percentile of Wind Shears'
title = 'Ensemble Mean'

# Collects requisite information from the A-Deck regarding the given storm for the specified hour and models
# Additionally retrieves the U and V wind data for the GEFS corresponding to the same time and run
adeckDF = adeck.filterData(storm, [f'{year}{str(month).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}'], ['AP01', 'AP02', 'AP03', 'AP04', 'AP05', 'AP06', 'AP07', 'AP08', 'AP09', 'AP10', 'AP11', 'AP12', 'AP13', 'AP14', 'AP15', 'AP16', 'AP17', 'AP18', 'AP19', 'AP20', 'AP21', 'AP22', 'AP23', 'AP24', 'AP25', 'AP26', 'AP27', 'AP28', 'AP29', 'AP30', 'AP31'], [fcastHour])
print(adeckDF)

if clusterType.lower() == 'intensity':
    clusters, centroids = findClusters(adeckDF, adeckDF[8], numClusters)
elif clusterType.lower() == 'latitude':
    clusters, centroids = findClusters(adeckDF, adeckDF[6], numClusters)
elif clusterType.lower() == 'longitude':
    clusters, centroids = findClusters(adeckDF, adeckDF[7], numClusters)

data, init = gefs.getData(['hgtprs'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
# init = '2025-08-13 at 12:00z'
print(init)
# data[0].to_netcdf(r"C:\Users\deela\Downloads\hData813202512.nc")
# data = [xr.open_dataset(r"C:\Users\deela\Downloads\hData813202512.nc")['hgtprs']]

cHS = []
cHSAll = []
sigHS = []
for c in range(len(clusters)):
    # Calculate wind shears for each member of the GEFS
    hs = []
    for member in clusters[c].iterrows():
        member = member[1]
        # Selects GEFS member from the A-Deck and retrieves latitudes and longitudes 
        x = int(member[4][2:])

        hgtData = data[0].sel(ens = x + 1, lev = height)
        lon, lat = member[7], member[6]
        if lon < 0:
            lon = lon + 360
        
        # Subsets a 5x5 degree box centered on the storm and computes the average for all pressure levels
        # This data (both the zonal and meridional component of the wind vector) is then passed to the function to compute wind shears throughout the column
        # The values returned are then appended to lists to form the 3D matrices     
        hgtData = hgtData.sel(lon = slice(240, 359), lat = slice(0, 70))
        hs.append(hgtData)

    # Simple average of all ensemble members
    if title == 'Ensemble Mean':
        hsMean = sum(hs) / len(hs)

    cHS.append(hsMean)
    cHSAll.append(hs)

t_stat, p_value = stats.ttest_ind(cHSAll[0], cHSAll[1], equal_var=False)
hs = cHS[0] - cHS[1]

# Runs program
grid = [hgtData.lon, hgtData.lat]
finalPlot(grid, init, title, clusterType, (clusters, centroids), hs)