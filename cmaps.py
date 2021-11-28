from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt
from numpy.core.function_base import linspace  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import xarray as xr
import metpy 
import windclimo as wc
import datetime
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import goesRequest2 as goes2

def swir():
    num1 = 15
    num2 = 55
    num3 = 40

    top = cm.get_cmap('Blues', num1)
    mid = cm.get_cmap('plasma', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0, 1, num2)),
                           bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def spooky():
    num1 = 20
    num2 = 85
    num3 = 30

    top = cm.get_cmap('Greys', num1)
    mid = cm.get_cmap('CMRmap', num2)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0, 1, num2)),
                           bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def santa():
    num1 = 20
    num2 = 30
    num3 = 50
    num4 = 40

    top = LinearSegmentedColormap.from_list("", [(0.0, "#cfcfcf"), (1, "#d9c548")])
    mid = cm.get_cmap('PiYG', num2)
    mid2 = cm.get_cmap('Reds_r', num3)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0.5, 1, num2)),
                           mid2(np.linspace(0.2, 0.8, num3)),
                           bot(np.linspace(0.1, 0.9, num4))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def santa2():
    num1 = 20
    num2 = 30
    num3 = 50
    num4 = 40

    top = cm.get_cmap('hot_r', num1)
    mid = cm.get_cmap('Reds_r', num2)
    mid2 = cm.get_cmap('PiYG', num3)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 0.3, num1)),
                           mid(np.linspace(0.3, 1, num2)),
                           mid2(np.linspace(0.6, 1, num3)),
                           bot(np.linspace(0.1, 0.9, num4))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def dust():
    num1 = 40
    num2 = 10
    num3 = 50

    top = cm.get_cmap('Blues_r', num1)
    mid = cm.get_cmap('Greys', num2)
    bot = cm.get_cmap('afmhot', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0, 1, num2)),
                           bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def ssta():
    num1 = 45
    num2 = 50
    neut = 10
    num3 = 50
    num4 = 45

    top = cm.get_cmap('Reds_r', num1)
    sec = cm.get_cmap('YlOrRd', num2)
    mid = cm.get_cmap('binary', neut)
    frt = cm.get_cmap('PuBuGn_r', num3)
    bot = cm.get_cmap('BuGn', num4)

    newcolors = np.vstack((bot(np.linspace(0, 1, num1)),
                           frt(np.linspace(0, 1, num2)),
                           mid(np.linspace(0, 0.01, neut)),
                           sec(np.linspace(0, 1, num3)),
                           top(np.linspace(0, 1, num4))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def tddev():
    newcmp = LinearSegmentedColormap.from_list("", [(0.0, "gray"), (0.2, 'white'), (0.4, "#72aefc"), (1, "#141414")])
    return newcmp

def stddev():
    num1 = 40
    num2 = 160

    a = cm.get_cmap('Greys_r', num1)
    b = cm.get_cmap('OrRd', num2)

    newcolors = np.vstack((a(np.linspace(0, 0.75, num1)),
                           b(np.linspace(0, 1, num2))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def cmap(color1, num1, color2, num2):
    top = cm.get_cmap(color1, num1)
    bottom = cm.get_cmap(color2, num2)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                       bottom(np.linspace(0, 1, num2))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def pv():
    top = cm.get_cmap('BuPu_r', 3)
    bottom = cm.get_cmap('OrRd', 8)

    newcolors = np.vstack((top(np.linspace(0.5, 0.75, 3)),
                        bottom(np.linspace(0, 0.5, 8))))
    newcmp = ListedColormap(newcolors, name = 'temp')
    return newcmp

def pv2():
    bottom = cm.get_cmap('OrRd', 8)

    newcolors = np.vstack((bottom(np.linspace(0, 0.5, 8))))
    newcmp = ListedColormap(newcolors, name = 'temp')
    return newcmp

def pv3():
    top = cm.get_cmap('BuPu_r', 30)
    bottom = cm.get_cmap('OrRd', 80)

    newcolors = np.vstack((top(np.linspace(0.5, 0.75, 30)),
                        bottom(np.linspace(0, 0.5, 80))))
    newcmp = ListedColormap(newcolors, name = 'temp')
    return newcmp

def ir():
    color1 = 'twilight'
    num1 = 110
    color2 = 'Greys' 
    num2 = 40

    top = cm.get_cmap(color1, num1)
    bottom = cm.get_cmap(color2, num2)
    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                       bottom(np.linspace(0, 1, num2))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def wind():
    num1 = 34
    num2 = 30
    num3 = 19
    num4 = 13
    num5 = 17
    num6 = 24
    num7 = 43

    top = cm.get_cmap('Greys_r', num1)
    mid = cm.get_cmap('Blues', num2)
    bot = cm.get_cmap('Greens_r', num3)
    nex1 = cm.get_cmap('Purples', num4)
    nex2 = cm.get_cmap('Oranges_r', num5)
    nex3 = cm.get_cmap('pink_r', num6)
    nex4 = cm.get_cmap('Reds_r', num7)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3)), nex1(np.linspace(0, 1, num4)), nex2(np.linspace(0, 1, num5)), nex3(np.linspace(0, 1, num6)), nex4(np.linspace(0, 1, num7))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def oldir():
    num1 = 20
    num2 = 60
    num3 = 40
    num4 = 20
    num5 = 10
    top3 = cm.get_cmap('OrRd', num5)
    top2 = cm.get_cmap('BuPu_r', num4)
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top3(np.linspace(0, 1, num5)), top2(np.linspace(0, 1, num4)), top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def whaticouldvedone():
    num1 = 25
    num2 = 55
    num3 = 40
    num4 = 10
    num5 = 10
    top3 = cm.get_cmap('OrRd', num5)
    top2 = cm.get_cmap('BuPu_r', num4)
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top3(np.linspace(0, 1, num5)), top2(np.linspace(0, 1, num4)), top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def wv():
    num1 = 20
    num2 = 40
    num3 = 30
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('BuPu_r', num2)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def ref():
    num1 = 30
    num2 = 20
    num3 = 25
    top = cm.get_cmap('summer', num1)
    mid = cm.get_cmap('autumn_r', num2)
    bot = cm.get_cmap('hot_r', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0.5, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp
