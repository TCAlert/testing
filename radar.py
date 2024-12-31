import bz2
import numpy as np 
import satcmaps as cmap 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
from datetime import datetime 
import cartopy.feature as cfeature

# Specify the input .bz2 file and output file
file = r"C:\Users\deela\Downloads\HS_H08_20150707_0200_B13_FLDK_R20_S0101.DAT.bz2"

# Decompress the .bz2 file
with bz2.BZ2File(file, 'rb') as data:
    decoded_data = data.read()
    print("Header (raw):", decoded_data)#np.frombuffer(decoded_data, dtype=np.uint8)[:64])

    decoded_data = np.frombuffer(decoded_data, dtype=np.uint8).reshape(20, 1480)
    # decoded_data = (conv(decoded_data, 'IR') - 273.15)#[:, 249:3424]

    cmp, vmax, vmin = cmap.irtables['irg']
    # lat = 760.8
    # lon = 1798.6
    # s = 200
    # labelsize = 8

    plt.figure(figsize = (18, 9))
    ax = plt.axes()
    c = ax.imshow(decoded_data, origin = 'upper', cmap = 'Greys_r')#, vmin = vmin, vmax = vmax)
    # # ax.set_xlim(lon - s, lon + s)
    # # ax.set_ylim(lat + s, lat - s)    
    # plt.title(f'GMS-2 VISSR Infrared Image\n10/04/1982 at 1800z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    # plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
    # cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    # plt.savefig(r"C:\Users\deela\Downloads\gmstest.png", dpi = 500, bbox_inches = 'tight')
    plt.show()