import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
from datetime import datetime 
import cartopy.feature as cfeature
import urllib.request as urllib
from helper import strip, numToMonth

def retrieveData(year, month):
    link = 'https://www.psl.noaa.gov/mjo/mjoindex/omi.era5.1x.webpage.4023.txt'
    data = (urllib.urlopen(link).read().decode('utf-8')).split('\n')

    PC1 = []
    PC2 = []
    for x in range(len(data)):
        data[x] = data[x].split(' ')
        data[x] = strip(data[x])

        try:
            if int(data[x][0]) == year and int(data[x][1]) == month:
                PC1.append(float(data[x][3]))
                PC2.append(float(data[x][4]))
        except:
            pass

    return PC1, PC2

def plot(year, month):
    PC1, PC2 = retrieveData(year, month)

    fig = plt.figure(figsize=(12, 12))
    ax = plt.axes()
    ax.set_frame_on(False)
    c = plt.Circle((0, 0), radius = 1, facecolor = "None", edgecolor = '#404040', linestyle = '--')
    ax.add_patch(c)

    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('RMM2',  weight = 'bold', size = 9)
    ax.set_xlabel('RMM1', weight = 'bold', size = 9)
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)

    plt.plot(PC1, PC2)

    plt.title(f'ERA5 OLR-Derived RMM Plot\nData from PSL', fontweight='bold', fontsize=9, loc='left')
    plt.title(f'{numToMonth(month)} {year}', fontsize=9)
    plt.title('Deelan Jariwala', fontsize=9, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\rmmtest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

#plot(2015, 3)