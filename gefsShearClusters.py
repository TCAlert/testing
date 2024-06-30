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
def finalPlot(grid, shear, init, title, clusterType, clusters, us = None, vs = None):
    # Creates the plot
    fig = plt.figure(figsize=(15, 12))
    ax = plt.axes()
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_ylabel('Pressure (Upper Bound)')
    ax.set_xlabel('Pressure (Lower Bound)')
    ax.grid()

    try:
        # Plots the data using the pressure level grid created before
        # This section plots probabilistic data
        if us == None:
            c = ax.pcolormesh(grid[0], grid[1], shear, cmap = cmap.probs(), vmin = 0, vmax = 100)
            cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
            cb.set_ticks(range(0, 105, 5))

            for x in range(len(grid[0])):
                for y in range(len(grid[1])):
                    if shear[x][y] != 0:
                        plt.text(grid[0][x][y], grid[1][x][y], f'{int(round(shear[x][y], 0))}%', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

    except:    
        # Plots the data using the pressure level grid created before
        # Note that the vectors in the plot are normalized by the magnitude of the shear
        mag = (2.5 * (us**2 + vs**2)**0.5)
        c = ax.contourf(grid[0], grid[1], shear, cmap = cmap.tempAnoms(), levels = np.arange(-5, 5.1, .1), extend = 'both')
        ax.quiver(grid[0], grid[1], us / mag, vs / mag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = 'black', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")])
        cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
        cb.set_ticks(range(-5, 6, 1))

        # colors = ['red', 'blue', 'green']
        # labels = ['Deep  (200-850mb)', 'Mid     (500-850mb)', 'Upper (200-500mb)']
        # xes = [0, 6, 0]
        # yes = [-1, -1, 6]
        # for x in range(len(colors)):
        #     m = (us[xes[x]][yes[x]]**2 + vs[xes[x]][yes[x]]**2)**0.5
        #     ax.quiver(grid[0][xes[x]][yes[x]], grid[1][xes[x]][yes[x]], us[xes[x]][yes[x]] / mag[xes[x]][yes[x]], vs[xes[x]][yes[x]] / mag[xes[x]][yes[x]], pivot = 'middle', scale = 10, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = colors[x], zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], label = f'{labels[x]}: {round(m, 1)}kt')

        # plt.legend(loc = 'lower left')

        inset = inset_axes(ax, width = "100%", height= "100%", borderpad = 1, bbox_to_anchor=(0.45, 0.05, 0.65, 0.35), bbox_transform=ax.transAxes, loc="lower right", 
                   axes_class=cartopy.mpl.geoaxes.GeoAxes, 
                   axes_kwargs=dict(map_projection=cartopy.crs.PlateCarree()))

        clusters, centroids = clusters
        lats, lons = [], []
        for x in range(len(clusters)):
            #print(f'Cluster {x + 1} Winds: {np.mean(clusters[x][8])}')
            lats += (list(clusters[x][6]))
            lons += (list(clusters[x][7]))
            inset.scatter(clusters[x][7], clusters[x][6], label = f'Cluster {x + 1}: {round(centroids[x][0], 1)}')
            inset.legend()
            inset.set_title('Spatial Map of Clusters')
    extent = np.nanmax([round(np.nanmax(lons) - np.nanmin(lons)), round(np.nanmax(lats) - np.nanmin(lats))]) * 1.5
    map(inset, extent / 5)
    inset.set_extent([np.mean(lons) - (extent / 2), np.mean(lons) + (extent / 2), np.mean(lats) - (extent / 2), np.mean(lats) + (extent / 2)])

    time = (str(data[0].time.values)).split('T')
    print(time)
    time = f'{time[0]} at {(time[1][:5])}z'

    ax.set_title(f'GEFS Vertical Wind Shear Distribution: AL02\nInitialization: {init}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'Forecast Hour: {time}', fontsize = 10, loc = 'center')
    ax.set_title(f'Data split by {clusterType.upper()}: Cluster 1 - 2 Plotted\nDeelan Jariwala', fontsize=10, loc='right') 
    at = AnchoredText("Inspired by Michael Fischer",
                  prop=dict(size=8, color = 'gray'), frameon=False,
                  loc=4)
    at.patch.set_alpha(.1)
    ax.add_artist(at)

    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics_" + clusterType + title + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

# Sample usage
t = datetime.now()
year = t.year
month = t.month
day = t.day
hr = 12
fcastHour = 84
storm = 'al02'
shearStrength = 15
p = 50
numClusters = 2
clusterType = 'Intensity'
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

#data, init = gefs.getData(['ugrdprs', 'vgrdprs'], np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hr).zfill(2)}') + np.timedelta64(fcastHour, 'h'))
init = '2024-06-29 at 12:00z'
print(init)
#data[0].to_netcdf(r"C:\Users\deela\Downloads\uData.nc")
#data[1].to_netcdf(r"C:\Users\deela\Downloads\vData.nc")
data = [xr.open_dataset(r"C:\Users\deela\Downloads\uData629202412.nc")['ugrdprs'], xr.open_dataset(r"C:\Users\deela\Downloads\vData629202412.nc")['vgrdprs']]

cShears = []
cUS = []
cVS = []
for c in range(len(clusters)):
    # Calculate wind shears for each member of the GEFS
    shears = []
    us = []
    vs = []
    for member in clusters[c].iterrows():
        member = member[1]
        # Selects GEFS member from the A-Deck and retrieves latitudes and longitudes 
        x = int(member[4][2:])

        uData, vData = data[0].sel(ens = x + 1), data[1].sel(ens = x + 1)
        lon, lat = member[7], member[6]
        if lon < 0:
            lon = lon + 360
        
        # Subsets a 5x5 degree box centered on the storm and computes the average for all pressure levels
        # This data (both the zonal and meridional component of the wind vector) is then passed to the function to compute wind shears throughout the column
        # The values returned are then appended to lists to form the 3D matrices     
        grid, shear, u, v = allShear(uData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438, vData.sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean(['lat', 'lon']) * 1.9438)
        shears.append(shear)
        us.append(u)
        vs.append(v)

    # Simple average of all ensemble members
    if title == 'Ensemble Mean':
        shears = sum(shears) / len(shears)
        us = sum(us) / len(us)
        vs = sum(vs) / len(vs)
    # Largely self explanatory, returns a 2D list containing probabilities of exceedance
    elif title == f'Percent of Members with Shear Exceeding {shearStrength}kt':
        for x in range(len(shears)):
            shears[x] = np.where(shears[x] > shearStrength, 1, 0)
        shears = (np.sum(shears, axis = 0) / len(shears)) * 100
        us = vs = None    
    # Flattens the 3D list into a 2D one where each value corresponds to a given percentile of each `depth` column
    # Note that this additionally plots the ensemble mean shear vectors; in the future this could change
    elif title == f'{p}th Percentile of Wind Shears':
        shears = percentile(shears, p)
        us = sum(us) / len(us)
        vs = sum(vs) / len(vs)

    cShears.append(shears)
    cUS.append(us)
    cVS.append(vs)

shears = cShears[0] - cShears[1]
us = cUS[0] - cUS[1]
vs = cVS[0] - cVS[1]

# Runs program
finalPlot(grid, shears, init, title, clusterType, (clusters, centroids), us, vs)