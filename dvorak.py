from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import cmaps as cmap
from matplotlib import cm

eyenum = {"CDG" : 6.5,
          "CMG" : 6.5,
          "W"   : 6.0,
          "B"   : 5.5,
          "LG"  : 5.0, 
          "MG"  : 4.5,
          "DG"  : 4.5,
          "OW"  : 4.0,
          "WMG" : np.nan
         }

adjmat = {"OW"  : {"WMG" : 0,   "OW"  : -0.5},
          "DG"  : {"WMG" : 0,   "OW"  : 0    , "DG"  : -0.5},
          "MG"  : {"WMG" : 0,   "OW"  : 0    , "DG"  : -0.5, "MG"  : -0.5},
          "LG"  : {"WMG" : 0.5, "OW"  : 0    , "DG"  : 0,    "MG"  : -0.5, "LG"  : -0.5},
          "B"   : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0,    "MG"  : 0,    "LG"  : -0.5, "B"   : -0.5},
          "W"   : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0.5,  "MG"  : 0,    "LG"  : 0,    "B"   : -1,   "W"   : -1},
          "CMG" : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0.5,  "MG"  : 0,    "LG"  : 0,    "B"   : -0.5, "W"   : -1}
         }

def dvorak(emb, eye, surr):
    if surr.upper() == 'CDG':
        surr = 'CMG'
    #print((eyenum[emb.upper()], eyenum[surr.upper()]))

    if (emb.upper() == 'WMG' or (eyenum[emb.upper()] > eyenum[surr.upper()])) or (emb.upper() == 'MG' and surr.upper() == 'DG'):
        err = 'The embed shade cannot be colder than the surrounding color, and must be colder than WMG.'
    elif (eyenum[eye.upper()] > eyenum[surr.upper()]) or (eyenum[eye.upper()] >= eyenum[emb.upper()]):
        err = 'The eye must be warmer than the convection.'
    else:
        try:
            value = eyenum[emb.upper()] + adjmat[surr.upper()][eye.upper()]
            err = f'{emb.upper()} + {eye.upper()} surr {surr.upper()} is {value}'
        except:
            err = 'This is not possible.'
    return err

def bd():
    cdg = LinearSegmentedColormap.from_list("", ["#424242"])
    cmg = LinearSegmentedColormap.from_list("", ["#9E9E9E"])
    w = LinearSegmentedColormap.from_list("", ["#F8F8F8"])
    b = LinearSegmentedColormap.from_list("", ["#000000"])
    lg = LinearSegmentedColormap.from_list("", ["#B7B7B7"])
    mg = LinearSegmentedColormap.from_list("", ["#9A9A9A"])
    dg = LinearSegmentedColormap.from_list("", ["#5B5B5B"])
    ow = LinearSegmentedColormap.from_list("", [(0.0, "#C7C7C7"), (1, "#6D6D6D")])
    wmg = LinearSegmentedColormap.from_list("", [(0.0, "#F6F6F6"), (1, "#000000")])

    vmin = -110
    vmax = 30

    num1 = 29
    num2 = 5
    num3 = 6
    num4 = 6
    num5 = 10
    num6 = 12
    num7 = 12
    num8 = 39
    num9 = 21

    newcolors = np.vstack((cdg(np.linspace(0, 1, num1)),
                           cmg(np.linspace(0, 1, num2)),
                           w(np.linspace(0, 1, num3)),
                           b(np.linspace(0, 1, num4)),
                           lg(np.linspace(0, 1, num5)),
                           mg(np.linspace(0, 1, num6)),
                           dg(np.linspace(0, 1, num7)),
                           ow(np.linspace(0, 1, num8)),
                           wmg(np.linspace(0, 1, num9))))

    newcmp = ListedColormap(cdg, name='temp')

    return newcmp
