
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

def interleave(data):
    sizeX, sizeY = np.shape(data)
    half1, half2 = data[:, :int(sizeY / 2)], data[:, int(sizeY / 2):]

    newArray = np.zeros((sizeX * 2, int(sizeY / 2)))
    newArray[0::2] = half1
    newArray[1::2] = half2 

    print(half1.shape, half2.shape)

    return newArray

file = r"C:\Users\deela\Downloads\VISSR_GMS5_199511010600\VISSR_19951101_0531_IR3.A.IMG.gz"
newFile = r"C:\Users\deela\Downloads\VISSR_GMS5_199511010600\VISSR_19951101_0531_IR3.A.IMG.txt"

with gzip.open(file, 'rb') as f:
    with open(newFile, 'wb') as nf:
        print(f'File {file} opened successfully.')
        nf.write(f.read())
    

with open(newFile, 'rb') as data:
    decoded_data = data.read()
    decoded_data = 255 + np.frombuffer(decoded_data, dtype=np.uint16) / -255
    #decoded_data = (conv(decoded_data.reshape(int(len(decoded_data) / 3504), 3504), 'IR') - 273.15)
    decoded_data = (conv(decoded_data.reshape(int(len(decoded_data) / 1832), 1832), 'WV') - 273.15)
    #decoded_data = interleave(decoded_data.reshape(5003, 13504))

    cmp, vmax, vmin = cmap.wvtables['wv14']
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