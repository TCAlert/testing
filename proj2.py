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

    return cf2
 
def plot(param1, param2, cf, cf2, realMean, fakeMean):
    name1, param1 = param1
    name2, param2 = param2
    fig = plt.figure(figsize=(15, 9))

    # Add the map and set the extent
    ax = plt.axes()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel(name2, weight = 'bold', size = 9)
    ax.set_xlabel(name1, weight = 'bold', size = 9)

    for x in range(len(cf)):
        if cf[x] == 1 and cf2[x] == 1:
            ax.scatter(param1[x], param2[x], color = '#ff8888', zorder = 10)
        elif cf[x] == 1 and cf2[x] == 0:
            ax.scatter(param1[x], param2[x], color = '#ffcccc', zorder = 10)
        elif cf[x] == 0 and cf2[x] == 1:
            ax.scatter(param1[x], param2[x], color = '#ccccff', zorder = 10)
        elif cf[x] == 0 and cf2[x] == 0:
            ax.scatter(param1[x], param2[x], color = '#8888ff', zorder = 10)
    ax.text(realMean[0], realMean[1] - 0.25, f'Real', size=14, color='black', horizontalalignment = 'center', verticalalignment = 'top', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")], zorder = 100)
    ax.scatter(realMean[0], realMean[1], s = 60, c = 'black', marker = 'x', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")], zorder = 100)
    ax.text(fakeMean[0], fakeMean[1] - 0.25, f'Counterfeit', size=14, color='black', horizontalalignment = 'center', verticalalignment = 'top', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")], zorder = 100)
    ax.scatter(fakeMean[0], fakeMean[1], s = 60, c = 'black', marker = 'x', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")], zorder = 100)

    plt.title(f'{name1} vs. {name2}\nAccuracy: 70.70%' , fontweight='bold', fontsize=10, loc='left')
    plt.title('Deelan Jariwala', fontsize=10, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\\" + name1 + name2 + ".png", dpi = 400, bbox_inches = 'tight')

    #plt.show()

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

realMean, fakeMean = np.array(real).mean(axis = 1), np.array(fake).mean(axis = 1)
cf2 = dist(realMean, fakeMean, [vari, skew, kurt, entr])

plot(('Variance', vari), ('Skewness', skew), cf, cf2, [realMean[0], realMean[1]], [fakeMean[0], fakeMean[1]])
plot(('Variance', vari), ('Kurtosis', kurt), cf, cf2, [realMean[0], realMean[2]], [fakeMean[0], fakeMean[2]])
plot(('Variance', vari), ('Entropy', entr), cf, cf2, [realMean[0], realMean[3]], [fakeMean[0], fakeMean[3]])
plot(('Skewness', skew), ('Kurtosis', kurt), cf, cf2, [realMean[1], realMean[2]], [fakeMean[1], fakeMean[2]])
plot(('Skewness', skew), ('Entropy', entr), cf, cf2, [realMean[1], realMean[3]], [fakeMean[1], fakeMean[3]])
plot(('Kurtosis', kurt), ('Entropy', entr), cf, cf2, [realMean[2], realMean[3]], [fakeMean[2], fakeMean[3]])

plt.show()