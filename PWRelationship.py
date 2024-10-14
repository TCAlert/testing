import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import math 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import warnings 
import cmaps as cmap 
from matplotlib import rcParams
import bdeckFormatter as bdeck 
import matplotlib.patheffects as pe 

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None

rcParams['font.family'] = 'Courier New'

basin = 'AL'

if basin == 'EP':
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
else:
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

try:
    link = urlopen(link)
except:
    if basin == 'EP':
        link = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-042624.txt'
    else:
        link = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt'

    link = urlopen(link)
soup = BeautifulSoup(link, 'html.parser')
lines = soup.get_text().split('\n')

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

wind = []
pres = [] 
for x in range(len(lines)):
    temp = lines[x].split(',')
    if len(temp) > 5 and temp[3].strip() in ['TD', 'TS', 'HU', 'SD', 'SS'] and temp[7].strip() != '-999':
        wind.append(int(temp[6]))
        pres.append(int(temp[7]))

fig = plt.figure(figsize=(14, 7))
fig.set_facecolor('#252525')

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)

# Add state boundaries to plot
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False, colors = '#d9d9d9')
ax.grid(linestyle = '--', alpha = 0.5, color = '#d9d9d9', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Sea Level Pressure (mb)', weight = 'bold', color = '#d9d9d9', size = 9)
ax.set_xlabel('Maximum Wind (kt)', weight = 'bold', color = '#d9d9d9', size = 9)

ax.scatter(wind, pres, color = 'black', zorder = 10)
ax.scatter(wind, pres, c = wind, cmap = cmap.sshws(), vmin = 0, vmax = 140, zorder = 10, alpha = 0.35)

test = bdeck.getStorms('AL')
bPres = []
bWind = []
times = []
for x in range(len(test)):
    if test[x][0].strip() == 'AL022024' and test[x][4].strip() in ['TD', 'TS', 'HU', 'SD', 'SS']:
        bWind.append(int(test[x][7]))
        bPres.append(int(test[x][8]))
        times.append(f'{test[x][1].strip()} at {test[x][2].strip()}z')

ax.plot(bWind, bPres, linewidth = 2.5, color = '#002600', zorder = 15, path_effects=[pe.withStroke(linewidth=3.25, foreground="white")])
ax.scatter(bWind, bPres, s = 68, color = 'green', linewidth = .5, edgecolor = 'white', zorder = 15, path_effects=[pe.withStroke(linewidth=1.25, foreground="white")])

plt.title(f'HURDAT2 Atlantic Pressure and Wind Scatterplot\nYears Plotted: 1851-2023', color = '#d9d9d9', fontweight='bold', fontsize=10, loc='left')
plt.title(f'Hurricane BERYL Overlaid (As Of: {times[-1]})', color = '#d9d9d9', fontsize=9, loc='center')  
plt.title('Deelan Jariwala', color = '#d9d9d9', fontsize=10, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\wprscatterberyl.png", dpi = 400, bbox_inches = 'tight')

plt.show()
