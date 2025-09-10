import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy as np
import goesRequest as goes
import cmaps as cmaps 

l = [500]
satellite = '19'
loc = 1
sector = f'Mesoscale-{loc}'
bands = ['13']
flag = 'f'

threshold = -30

data, time, info, center = goes.getData(satellite.lower(), '13', sector)
data = data - 273.15
filteredData = np.where(data > threshold, np.nan, data)
data = data - np.nanmean(filteredData)
print(np.nanmean(filteredData))
data = np.where(data > 0, np.nan, data)
plt.figure(figsize = (18, 9))

if l[0] == 500:
    l[0] = '2km'
elif l[0] == 1000:
    l[0] = '1km'
else: 
    l[0] = '0.5km' 

ax = plt.axes(projection=ccrs.Geostationary(central_longitude=-75.0, satellite_height=35786023.0))
ax.set_frame_on(False)
c = ax.imshow(data, origin = 'upper', cmap = cmaps.probs().reversed(), vmin = -50, vmax = 0)
if 3 in bands and flag == 't':
    plt.title(f'GOES {satellite.capitalize()} Channel {bands} Mesoscale Sector {loc} w/ Modified Band 03 data\n{time}' , fontweight='bold', fontsize=10, loc='left')
else:
    plt.title(f'GOES {satellite.capitalize()} Channel {bands} Mesoscale Sector {loc}\n{time}' , fontweight='bold', fontsize=10, loc='left')
plt.title(f'Deelan Jariwala\nResolution: {l[0]}', fontsize=10, loc='right')
plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
plt.savefig(r"C:\Users\deela\Downloads\goesmeso.png", dpi = 400, bbox_inches = 'tight')
plt.show()
plt.close()
