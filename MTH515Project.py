import xarray as xr
import matplotlib.pyplot as plt
import satcmaps as cmaps 
import numpy as np 
from matplotlib import rcParams  
import bdeck as bdeck 
import cmaps 
from matplotlib.colors import LogNorm

labelsize = 8
points = np.arange(0, 10.05, .05)
x, y = np.meshgrid(points, points)
A = np.arange(0, 100.5, 0.5)
B = np.arange(0, 100.5, 0.5)
allPoints = [(A / (2*B + 1)), ((2*B**2 + B) / A)]

def f(x, y):
    return a - ((b + 1) * x) - (x**2 * y)

def g(x, y):
    return (b * x) - (x**2 * y)

a = 5
b = 0.5
for j in range(204):
    eqPoint = [(a / (2*b + 1)), ((2*b**2 + b) / a)]

    fData = f(x, y)
    gData = g(x, y)

    fig = plt.figure(figsize=(12, 9))
    ax = plt.axes()

    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Concentration of Chemical 2', weight = 'bold', size = 9)
    ax.set_xlabel('Concentration of Chemical 1', weight = 'bold', size = 9)
    ax.axhline(0, linewidth = 2, color = '#000000', zorder = 100)
    ax.axvline(0, linewidth = 2, color = '#000000', zorder = 100)
    ax.set_ylim(-.5, 10)
    ax.set_xlim(-.5, 10)

    mag = np.sqrt(fData**2 + gData**2)
    
    plt.scatter(eqPoint[0], eqPoint[1], color = 'red', s = 50, zorder = 10, label = 'Equillibrium Point')
    plt.streamplot(x, y, fData / mag, gData / mag, color = "#c3c3c3", density = 2, linewidth = .5)
    c = plt.contourf(x, y, mag, cmap = cmaps.probs4(), levels = np.logspace(np.log10(1), np.log10(1000), 200), extend = 'both', norm = LogNorm(1, 1000))

    plt.legend(loc = 'upper right')
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02, label = 'Magnitude of Reaction Rate Vector', ticks = np.arange(0, 1100, 100))
    plt.title(f'MTH 515 Project 8 (Chemical Network Model) Phase Portrait\nParameters Chosen: a = {a}, b = {round(b, 1)}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
    # plt.savefig(r"C:\Users\deela\Downloads\phasePortrait\\" + str(j) + ".png", dpi = 200, bbox_inches = 'tight')
    plt.show()
    
    a = a + 1
    b = b + 0.1