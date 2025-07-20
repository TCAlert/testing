import xarray as xr 
import urllib.request as urllib
import helper 
import numpy as np 
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import matplotlib.patheffects as pe
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
from collections import deque

def find_two_nearest_non_nan(array, start):
    rows, cols = array.shape
    start_row, start_col = start
    
    # BFS initialization
    queue = deque([(start_row, start_col)])
    visited = set()
    visited.add((start_row, start_col))
    
    # Neighbor directions (up, down, left, right, and diagonals)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    found_values = []
    
    while queue and len(found_values) < 2:
        r, c = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                if not np.isnan(array[nr, nc]):
                    found_values.append(array[nr, nc])
                    if len(found_values) == 2:
                        break
                queue.append((nr, nc))
    
    return found_values

def interpolate(data, turns):
    if turns == 0:
        return data
    else:
        for x in range(len(data)):
            for y in range(len(data)):
                if np.isnan(data[x][y]):
                    try:
                        nearest_values = find_two_nearest_non_nan(data, (x, y))
                        if nearest_values:
                            data[x][y] = np.nanmean(nearest_values)
                    except:
                        pass
        
        turns = turns - 1
        return interpolate(data, turns)

def gridData(data, sLat, sLon, s = 5, res = 1):
    lats = np.arange(sLat - s, sLat + s, res)
    lons = np.arange(sLon - s, sLon + s, res)
    grid = np.meshgrid(lats, lons)

    us = []
    vs = []
    for x in range(len(lats)):
        for y in range(len(lons)):
            u = []
            v = []
            for z in range(len(data)):
                try:
                    if data[z][3] > lats[x] and data[z][3] < lats[x + 1] and data[z][4] > lons[y] and data[z][4] < lons[y + 1]:
                        u.append(data[z][1]) 
                        v.append(data[z][2])
                    else:
                        u.append(np.nan)
                        v.append(np.nan)
                except:
                    u.append(np.nan)
                    v.append(np.nan)
            us.append(u)
            vs.append(v)
    us = np.nanmean(us, axis = 1)
    vs = np.nanmean(vs, axis = 1)

    return grid, np.transpose(np.array(us).reshape(grid[0].shape)), np.transpose(np.array(vs).reshape(grid[0].shape))

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('longitude') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

# Retrieve most the A-Deck text file from SSD for the requested storm and open it in Python
def getData(storm, year, month, day, time, region = 'EM1'):
    link = f'https://tropic.ssec.wisc.edu/real-time/mesoamv/{year}/{storm}/text/AMV{year}{month.zfill(2)}{day.zfill(2)}{time}GOES{region}'
    print(link)
    # link = f'https://tropic.ssec.wisc.edu/archive/data/{region}/{year}{month.zfill(2)}{day.zfill(2)}/AllWindsText/{year}{month.zfill(2)}{day.zfill(2)}.{hour.zfill(2)}.{region}.AllWindsText'     
    file = urllib.urlopen(link).read().decode('utf-8')    

    return file

# Creates Cartopy map 
def map(lon, lat, s = 5, center = 0):
    plt.figure(figsize = (18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))
    
    ax.set_extent([lon - s, lon + s, lat - s, lat + s], crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.75)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)  
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False

    return ax

year = '2025'
month = '06'
day = '19'
time = '0015'

data = getData('05E', year, month, day, time, 'EM2')
sLat = 14.9
sLon = -96.7
s = 10

print(data)
data = data.split('\n')[1:-1]

bin14 = []
bin47 = []
bin710 = []
for x in range(len(data)):
    temp = data[x].split(' ')
    temp = helper.strip(temp)
    print(temp)
    lev = int(temp[7])
    u, v = helper.dirSpdToUV(270 - int(temp[6]), float(temp[5]))
    date = np.datetime64(f'{temp[1][0:4]}-01-01') + np.timedelta64(int(temp[1][4:6]), 'D') + np.timedelta64(int(temp[2][0:2]), 'h') + np.timedelta64(int(temp[2][2:4]), 'm')
    print(date)
    lat = float(temp[3])
    lon = float(temp[4]) * -1

    #
    # locCon = (lat > 20 and lat < 55 and lon > -120 and lon < -60)
    locCon = (lat > (sLat - s) and lat < (sLat + s)) and (lon > (sLon - s) and lon < (sLon + s))

    if lev < 400 and lev >= 100 and locCon:
        bin14.append([date, u, v, lat, lon])
    elif lev < 700 and lev > 400 and locCon:
        bin47.append([date, u, v, lat, lon])
    elif lev <= 1000 and lev > 700 and locCon:
        bin710.append([date, u, v, lat, lon])

data = np.nan_to_num(np.array(bin14))
ax = map(sLon, sLat)

for x in range(len(data)):
    try:
        ax.barbs(data[x, 4], data[x, 3], data[x, 1], data[x, 2], fill_empty = True, length = 6, sizes=dict(emptybarb = 0.25), zorder = 15, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
    except:
        pass
plt.title(f'GOES-16 AMVs\nTime: {year}-{month}-{day} at {time}z' , fontweight='bold', fontsize=10, loc='left')
plt.title(f'Deelan Jariwala', fontsize=10, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\amvtest2.png", dpi = 250, bbox_inches = 'tight')
plt.show()

res = .5
grid, u, v = gridData(data, sLat, sLon, s, res)
u = interpolate(u, 5)
v = interpolate(v, 5)

ds = xr.Dataset({'u' : (["latitude", "longitude"], u),
                 'v' : (["latitude", "longitude"], v)}, 
       coords = {"latitude": np.arange(sLat - s, sLat + s, res),
                 "longitude": np.arange(sLon - s, sLon + s, res)})

#ds.to_netcdf(r"C:\Users\deela\Downloads\amvtest.nc")

fxx, fxy = Gradient2D(ds['u'])
fyx, fyy = Gradient2D(ds['v'])
mag = fyx - fxy
# mag = fxx + fyy
mag = gaussian_filter(mag, sigma = 1)

ax = map(sLon, sLat)
ax.barbs(grid[1], grid[0], u, v, fill_empty = True, length = 5, sizes=dict(emptybarb = 0.15), zorder = 15, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
#plt.pcolormesh(ds['u'].longitude, ds['u'].latitude, mag, cmap = cmap.tempAnoms(), vmin = -10, vmax = 10)
plt.contourf(ds['u'].longitude[:-1], ds['u'].latitude[:-1], mag, cmap = cmap.tempAnoms(), levels = np.arange(-10, 10.1, .1), extend = 'both')

cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label('Divergence')
plt.title(f'GOES-16 Gridded AMV Attempt\nTime: {year}-{month}-{day} at {time}z' , fontweight='bold', fontsize=10, loc='left')
plt.title(f'0.5Deg\nDeelan Jariwala', fontsize=10, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\amvtestGridded2.png", dpi = 250, bbox_inches = 'tight')
plt.show()