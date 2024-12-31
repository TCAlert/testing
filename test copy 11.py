import xarray as xr 
import matplotlib.pyplot as plt
import satcmaps as cmap
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import pandas as pd 
from helper import greatCircle

csv = pd.read_csv(r"C:\Users\deela\Downloads\lorenzobuoy.csv")
print(csv)

lat = csv['latitude']
lon = csv['longitude']
slat = csv['SLAT']
slon = csv['SLON']

d = []
for x in range(len(lat)):
    try:
        value = greatCircle(float(lat[x]), float(lon[x]), float(slat[x]), float(slon[x]))
        print(value)
        d.append(value)
    except:
        pass
print(d)
