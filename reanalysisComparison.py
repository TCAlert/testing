import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import math 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import warnings 
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib.dates as mdates

warnings.simplefilter(action='ignore', category=FutureWarning)

def ACE(data, status, time):
    wind = data.astype(int)
    status = status
    total = []
    for x in range(len(wind)):
        if status[x].strip() in ['SS', 'TS', 'HU'] and (int(time[x]) % 600 == 0):
            ace = wind[x]**2 / 10000
            total.append(round(ace, 2))
        else:
            total.append(0)
    return np.cumsum(total) 

def track(data, ax = None):    
    name = data['Name']
    year = data['Year']
    ace = round(data['ACE'].iloc[-1], 2)
    lons = np.where(data['Longitude'] > 0, data['Longitude'], data['Longitude'] + 360)
    lats = data['Latitude']
    wind = data['Wind']
    stat = data['Status']
    vm = max(wind)

    if ax == None:
        print('No axis found.')
        cbar = True
        fig = plt.figure(figsize=(18,5))

        if max(lons) >= 355 or min(lats) == 0:
            ax = plt.axes(projection = ccrs.PlateCarree(central_longitude = 20))
            gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
            gl.top_labels = gl.right_labels = False  
        else:
            ax = plt.axes(projection = ccrs.PlateCarree(central_longitude = 200))
            gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
            gl.top_labels = gl.right_labels = False
        ax.coastlines(resolution='10m', color='black', linewidth=0.8)
        ax.add_feature(cartopy.feature.LAND.with_scale('10m'), facecolor = 'lightgrey')
        ax.add_feature(cartopy.feature.OCEAN, facecolor = 'dimgray')
        ax.add_feature(cartopy.feature.LAKES, facecolor = 'dimgray')
        ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    else:
        cbar = False 

    if abs(max(lons) - min(lons)) < abs(max(lats) - min(lats)):
        ax.set_extent([min(lons) - 15, max(lons) + 15, min(lats) - 5, max(lats) + 5], crs=ccrs.PlateCarree())
    else:
        ax.set_extent([min(lons) - 5, max(lons) + 5, min(lats) - 5, max(lats) + 5], crs=ccrs.PlateCarree())

    cmap = LinearSegmentedColormap.from_list("", [
            (0/137, "#5ebaff"),
            (33/137, "#5ebaff"),
            (33/137, "#00faf4"),
            (64/137, "#00faf4"),
            (64/137, "#ffffcc"),
            (83/137, "#ffffcc"),
            (83/137, "#ffe775"),
            (96/137, "#ffe775"),
            (96/137, "#ffc140"),
            (113/137, "#ffc140"),
            (113/137, "#ff8f20"),
            (137/137, "#ff8f20"),
            (137/137, "#ff6060")])

    plt.plot(lons, lats, color = 'black', alpha = 0.5, linewidth = 0.5, transform = ccrs.PlateCarree(central_longitude = 0))
    for x in range(len(stat)):
        if stat[x] in ['SD', 'SS']:
            plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, linewidths=0.5, vmin = 0, vmax = 137, edgecolors='black', zorder = 500, marker = 's', transform = ccrs.PlateCarree(central_longitude = 0))
        elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
            plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, alpha = 0.375, vmin = 0, vmax = 137, linewidths=0.5, edgecolors='black', zorder = 500, marker = '^', transform = ccrs.PlateCarree(central_longitude = 0))
        else:
            plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, linewidths=0.5, vmin = 0, vmax = 137, edgecolors='black', zorder = 500, transform = ccrs.PlateCarree(central_longitude = 0))
    # plt.text(lons[0] - 3, lats[0] + 1, (str(data['Time'][0]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
    # plt.text(lons[-1] - 3, lats.iloc[-1] + 1, (str(data['Time'].iloc[-1]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
    plt.title(f"Hurricane Carmen 1974 Revised vs Original Track\nMax Winds: {str(vm)}kts" , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Total ACE: {ace}\nDeelan Jariwala', fontsize=10, loc='right')
    plt.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical')], loc = 'upper right')

    norm = mcolors.Normalize(vmin=0, vmax=140)
    p = cm.ScalarMappable(cmap=cmap, norm=norm)
    p.set_array([])

    if cbar == True:
        print('Adding colorbar!')
        cbar = plt.colorbar(p, ax = ax, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])    
        cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])

    plt.savefig(r"C:\Users\deela\Downloads\wpplot.png", bbox_inches='tight', dpi = 222)
    #plt.show()
    #plt.close()

    return ax 


def plot(og, ra):
    fig = plt.figure(figsize=(14, 11))
    ax = plt.axes()

    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_xlabel(f'Time', weight = 'bold', size = 9)
    ax.set_ylabel(f'Maximum Sustained Winds (kts)', weight = 'bold', size = 9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Tick every day
    fig.autofmt_xdate()  # Rotate for clarity if needed
    # ax.axvline(color = 'black')
    ax.axhline(color = 'black')

    df = pd.merge(og, ra, on="Time", how="inner")
    print(df)
    df["diff"] = df["Wind_y"] - df["Wind_x"]

    ax.plot(og['Time'], df['diff'], c = 'black', linewidth = 1)
    ax.fill_between(ra['Time'], ra['Wind'], 0, where=(ra['Wind'] > 0), color='blue', alpha=0.3)
    ax.fill_between(og['Time'], og['Wind'], 0, where=(og['Wind'] > 0), color='red', alpha=0.3)
    ax.set_title(f'Change in New (blue) and Old (red) Intensity of Hurricane Carmen\n1974 Hurricane Season Reanalysis', fontweight='bold', fontsize=9, loc='left')  
    ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right')  
    #plt.savefig(r"C:\Users\deela\Downloads\changesinCarmen.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

og = pd.read_csv(r"C:\Users\deela\Downloads\1974Original.txt", usecols = np.arange(0, 8), names = ['Date', 'Time', 'L', 'Status', 'Latitude', 'Longitude', 'Wind', 'MSLP'])
ra = pd.read_csv(r"C:\Users\deela\Downloads\1974Revised.txt", usecols = np.arange(0, 8),names = ['Date', 'Time', 'L', 'Status', 'Latitude', 'Longitude', 'Wind', 'MSLP'])

og['Name'] = 'Carmen (old)'
ra['Name'] = 'Carmen (new)'
og['Year'] = 1974
ra['Year'] = 1974

#for x in range(len(og['Wind'])):
og['ACE'] = ACE(og['Wind'], og['Status'], og['Time'])
og.Latitude = ((og.Latitude).str[:-1]).astype(float)
og.Longitude = ((og.Longitude).str[:-1]).astype(float) * -1
og['Date'] = og['Date'].astype(str)
og['Time'] = og['Time'].astype(str).str.zfill(4)
for y in range(len(og.Time)):
    og['Time'][y] = np.datetime64(f'{og["Date"][y][0:4]}-{og["Date"][y][4:6]}-{og["Date"][y][6:8]}T{og["Time"][y][0:2]}')

#for x in range(len(ra['Wind'])):
ra['ACE'] = ACE(ra['Wind'], ra['Status'], ra['Time'])
ra.Latitude = ((ra.Latitude).str[:-1]).astype(float)
ra.Longitude = ((ra.Longitude).str[:-1]).astype(float) * -1
ra['Date'] = ra['Date'].astype(str)
ra['Time'] = ra['Time'].astype(str).str.zfill(4)
for y in range(len(ra.Time)):
    ra['Time'][y] = np.datetime64(f'{ra["Date"][y][0:4]}-{ra["Date"][y][4:6]}-{ra["Date"][y][6:8]}T{ra["Time"][y][0:2]}')

print(og, '\n', ra)

# ax = track(og, None)

# track(ra, ax)

plot(og, ra)