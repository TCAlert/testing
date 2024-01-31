import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def temperature():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/200, "#f2bbd4"), 
    (5/200, "#5f0d2e"),
    (10/200, "#840f09"),
    (20/200, "#ce3f1b"),
    (28/200, "#e8b05f"),
    (35/200, "#e6d874"),
    (50/200, "#71b634"),
    (60/200, "#21843f"),
    (68/200, "#21432b"),
    (68/200, "#66b0db"),
    (75/200, "#206493"),
    (79/200, "#385484"),
    (81/200, "#434c7d"),
    (90/200, "#7970f0"),
    (100/200, "#e7dbfe"),
    (110/200, "#9053e6"),
    (120/200, "#661180"),
    (130/200, "#40162e"),
    (160/200, "#bf41b9"),
    (200/200, "#ffd9ee")])

    return newcmp.reversed()

def pwat():
    newcmp = LinearSegmentedColormap.from_list("",[
    (0/80, "#eeeeee"),
    (10/80, "#2e2e2e"),
    (15/80, "#6e3e04"),
    (30/80, "#c7ad8d"),
    (40/80, "#1f5725"),
    (50/80, "#5c9d8d"),
    (60/80, "#385472"),
    (70/80, "#a98dc3"),
    (80/80, "#e7e7e7")])

    return newcmp

def tempAnoms():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/20, "#f2b3b3"),
    (5/20, "#802525"),
    (7.5/20, "#faa44d"),
    (10/20, "#FFFFFF"),
    (12.5/20, "#4da4fa"),
    (15/20, "#252580"),
    (20/20, "#d3b3f2")])

    vmin = -5
    vmax = 5

    return newcmp.reversed()

def snow():
    newcmp = LinearSegmentedColormap.from_list("",[
    (0/96, "#F4F4F4"),
    (0.1/96, "#F4F4F4"),
    (0.1/96, "#BFD8EC"),
    (1/96, "#BFD8EC"),
    (1/96, "#6BAFD2"),
    (2/96, "#6BAFD2"),
    (2/96, "#2F7FBC"),
    (3/96, "#2F7FBC"),
    (3/96, "#08529B"),
    (4/96, "#08529B"),
    (4/96, "#082899"),
    (6/96, "#082899"),
    (6/96, "#FFFE94"),
    (8/96, "#FFFE94"),
    (8/96, "#FDC403"),
    (12/96, "#FDC403"),
    (12/96, "#FF8601"),
    (18/96, "#FF8601"),
    (18/96, "#D81501"),
    (24/96, "#D81501"),
    (24/96, "#980108"),
    (30/96, "#980108"),
    (30/96, "#6F0000"),
    (36/96, "#6F0000"),
    (36/96, "#320000"),
    (48/96, "#320000"),
    (48/96, "#CACBFB"),
    (60/96, "#CACBFB"),
    (60/96, "#A08BDA"),
    (72/96, "#A08BDA"),
    (72/96, "#7B509F"),
    (96/96, "#7B509F")])

    return newcmp

def wind():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/160, "#000000"), 
    (34/160, "#a6a6a6"),
    (34/160, "#4245a6"),
    (64/160, "#29a668"),
    (96/160, "#cccc33"),
    (113/160, "#cc3333"),
    (137/160, "#cc7acc"),
    (160/160, "#ffffff")])
    
    vmin = 0
    vmax = 160

    return newcmp

def wind2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/152, "#ffffff"),
    (20/152, "#74C9DA"), 
    (34/152, "#A8F39B"),
    (50/152, "#F9F797"),
    (64/152, "#f09571"),
    (83/152, "#F96B6B"),
    (96/152, "#F26EF5"),
    (113/152, "#7030A0"),
    (125/152, "#283B76"),
    (140/152, "#a28df0"),
    (152/152, "#d0cdfa")])

    return newcmp

def shear():
    newcmp = LinearSegmentedColormap.from_list("", [ 
    (0/80, "#f5f5f5"),
    (10/80, "#4245a6"),
    (15/80, "#29a668"),
    (25/80, "#cccc33"),
    (35/80, "#cc3333"),
    (50/80, "#cc7acc"),
    (80/80, "#ffffff")])

    vmin = 0
    vmax = 80
    
    return newcmp

# Shortwave Infrared
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

# "Halloween" IR Colortable
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

# "Christmas" IR Colortable
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

# Colormap for GEOS-5 and MERRA-2 Dust Extinction Data
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

# SSTA Colormap
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

# Standard Deviation Colormap for GEFS Data
def stddev():
    num1 = 40
    num2 = 160

    a = cm.get_cmap('Greys_r', num1)
    b = cm.get_cmap('OrRd', num2)

    newcolors = np.vstack((a(np.linspace(0, 0.75, num1)),
                           b(np.linspace(0, 1, num2))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

# Three PV Colormaps for GFS and Reanalysis Data
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

# Plain IR Colormap
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

# Older, More Detailed Colormap
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

# Update to "oldir"
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

# Water Vapor Colormap
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

# Reflectivity Data Colormap (MRMS Data)
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
