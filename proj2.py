# Project 2: Simple Pokemon Game
# Deelan Jariwala

import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import matplotlib.patheffects as pe
from matplotlib import rcParams
import pandas as pd 

rcParams['font.family'] = 'Courier New'

def dist(realMean, fakeMean, data):
    cf2 = []
    distFromReal = np.sqrt((data[0] - realMean[0])**2 + (data[1] - realMean[1])**2 + (data[2] - realMean[2])**2 + (data[3] - realMean[3])**2)
    distFromFake = np.sqrt((data[0] - fakeMean[0])**2 + (data[1] - fakeMean[1])**2 + (data[2] - fakeMean[2])**2 + (data[3] - fakeMean[3])**2)
    
    for x in range(len(distFromFake)):
        if distFromReal[x] < distFromFake[x]:
            cf2.append(0)
        else:
            cf2.append(1)

    return cf
 
def plot(param1, param2, cf, cf2):
    fig = plt.figure(figsize=(16, 8))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)

    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Temperature (\u00b0C)', weight = 'bold', size = 9)
    ax.set_xlabel('Year', weight = 'bold', size = 9)

    for x in range(len(cf)):
        ax.scatter(param1[x], param2[x], cf[x], color = 'black', zorder = 10)
    #ax.text(years[-1] + 5, sst[-1], f'{round(float(sst[-1]), 1)}C', size=10, color='#404040', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])

    plt.title(f'ERSSTv5 Sea Surface Temperatures\n-5S to 5N, 170 to 120W' , fontweight='bold', fontsize=10, loc='left')
    #plt.title(f'{helper.numToMonth(month)}', fontsize = 10, loc = 'center')
    plt.title('Deelan Jariwala', fontsize=10, loc='right')  
    #plt.savefig(r"C:\Users\deela\Downloads\ersstlineplot.png", dpi = 400, bbox_inches = 'tight')

    plt.show()

data = pd.read_csv(r"C:\Users\deela\Downloads\data_banknote_authentication.csv")
vari, skew, kurt, entr, cf = data['variance'], data['skewness'], data['kurtosis'], data['entropy'], data['counterfeit']

fake = [[], [], [], []]
real = [[], [], [], []]
for x in range(len(cf)):
    if cf[x] == 0:
        real[0].append(vari[x])
        real[1].append(skew[x])
        real[2].append(kurt[x])
        real[3].append(entr[x])
    else:
        fake[0].append(vari[x])
        fake[1].append(skew[x])
        fake[2].append(kurt[x])
        fake[3].append(entr[x])

cf2 = dist(np.array(fake).mean(axis = 1), np.array(fake).mean(axis = 1), [vari, skew, kurt, entr])
print(cf2)

plot(vari, skew, cf)