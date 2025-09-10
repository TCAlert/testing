
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
newFile = r"C:\Users\deela\Downloads\NSIDC-0630-EASE2_T25km-NIMBUS7_SMMR-1979242-37H-A-GRD-JPL-v1.3.nc"

with open(newFile, 'rb') as data:
    decoded_data = data.read()

    with open(file, 'w', encoding="utf-8") as f:
        f.write(decoded_data.decode('utf-8', errors='ignore'))
    print(np.frombuffer(decoded_data, dtype='>u2').shape)
    decoded_data = np.frombuffer(decoded_data, dtype='>u2')#.reshape(3052, 155)

    # Assuming blocks are full-sized, estimate expected shape
    block_size = 28000 // 2  # 28000 bytes → 14000 2-byte words
    header_footer_size = 4 // 2  # 4 bytes → 2 words
    record_size = 560 // 2  # 560 bytes → 280 words

    # Extracting data while skipping headers/footers
    blocks = []
    i = 0
    while i < len(decoded_data):
        if i + block_size > len(decoded_data):  # Handle partial block
            break
        block = decoded_data[i + header_footer_size : i + block_size - header_footer_size]
        blocks.append(block)
        i += block_size

    # Convert to numpy array
    decoded_data = np.concatenate(blocks).reshape(-1, record_size)

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