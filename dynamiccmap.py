import numpy as np
from datetime import datetime 
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import cgfs as gfs
import bdeck as bdeck 

# Retrieve relevant GFS Data
def getGFSData(storm):
    requests = ['tmpprs', 'tmptrop']
    t = datetime.utcnow()
    hour = xr.Dataset({"time": datetime(t.year, t.month, t.day, t.hour)})['time'].values
    dat = gfs.data(requests, hour)
    time = dat[0].time.values

    lat, lon = bdeck.latlon(storm)
    
    tmp500 = int((dat[0].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5), lev = 500).mean() - 273).values)
    tmptro = int((dat[1].sel(lon = slice(lon - 2.5, lon + 2.5), lat = slice(lat - 2.5, lat + 2.5)).mean() - 273).values)

    return tmp500, tmptro, lat, lon, time

# Create dynamic colormap off of GFS data
def dynamicCMAP(storm):
    tmp500, tmptro, lat, lon, time = getGFSData(storm)

    num1 = 40 - tmp500
    num2 = abs(tmptro - tmp500)
    num3 = 150 - num1 - num2

    top = cm.get_cmap('bone_r', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('PuRd', num3)

    newcolors = np.vstack((bot(np.linspace(0, 1, num3)), mid(np.linspace(0, 1, num2)), top(np.linspace(0, 1, num1))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp, tmp500, tmptro, lat, lon, time

# Largely experimental, write up here: https://cdn.discordapp.com/attachments/843292360275394610/915342804715208744/Regarding_the_Usage_of_a_Dynamic_Colormap_for_Deep_Convection.pdf
