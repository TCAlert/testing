
import matplotlib.pyplot as plt
import numpy as np 
import gzip 
import satcmaps as cmap 
import pandas as pd

def conv(dat, t = "IR"):
    conv = pd.read_csv(r"C:\Users\deela\Downloads\\gms_conversions - " + t + ".csv")
    mapping = dict(zip(conv['BRIT'], conv['TEMP']))
    for x in range(len(dat)):
        for y in range(len(dat[x])):
            try:
                dat[x][y] = mapping[round(dat[x][y])]
            except:
                dat[x][y] = 0
    
    return dat

file = r"C:\Users\deela\Downloads\check.txt"
newFile = r"C:\Users\deela\Downloads\sms01.1974.199.0730.AREA_IR"

with open(newFile, 'rb') as data:
    decoded_data = data.read()

    with open(file, 'w', encoding="utf-8") as f:
        f.write(decoded_data.decode('utf-8', errors = 'ignore'))
    decoded_data = 255 + np.frombuffer(decoded_data, dtype=np.uint8)[256:].reshape(1393, 2193) / -255
    decoded_data = (conv(decoded_data, 'IR') - 273.15)#[:, 249:3424]

    cmp, vmax, vmin = cmap.irtables['irg']
    lat = 760.8
    lon = 1798.6
    s = 200
    labelsize = 8

    plt.figure(figsize = (18, 9))
    ax = plt.axes()
    c = ax.imshow(decoded_data, origin = 'upper', cmap = cmp, vmin = vmin, vmax = vmax)
    # ax.set_xlim(lon - s, lon + s)
    # ax.set_ylim(lat + s, lat - s)    
    plt.title(f'GMS-2 VISSR Infrared Image\n10/04/1982 at 1800z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\deela\Downloads\gmstest.png", dpi = 500, bbox_inches = 'tight')
    plt.show()