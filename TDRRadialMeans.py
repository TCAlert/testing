import scipy.ndimage
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
from matplotlib import rcParams
warnings.filterwarnings("ignore")
rcParams['font.family'] = 'Courier New'

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
print(list(dataset1.variables))
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")

def binFunc(t, height):
    if t == 'Alignment':
        l1 = [225,251,252,253,254,333,334,347,374,376,377,407,408,409,410,413,414,603,604,605,672]
        list2 = [719,752,765,767,794,878,879,939,941,957,968,969,970,971,1057,1073,1101,1131,1148,1177,1178,1179,1180,1191,1192,1220,1222,1223,1224,1226,1227,1228,1301,1302,1305]
        l2 = [x - 710 for x in list2]
    elif t == 'Misalignment':
        l1 = [148,149,222,224,339,340,341,342,343,344,382,383,384,402,423,424,425,426,427,429,430,431,545,600,601]
        list2 = [742,744,745,747,869,898,899,918,919,930,934,935,936,1040,1049,1175,1195,1197,1201,1217,1218]
        l2 = [x - 710 for x in list2]
    else:
        l1 = [488, 489]
        l2 = []

    data1 = dataset1['swath_relative_vorticity'].sel(num_cases = l1, height = height)
    rmw1 = dataset1['tc_rmw'].sel(num_cases = l1, height = 3)
    data2 = dataset2['swath_relative_vorticity'].sel(num_cases = l2, height = height)
    rmw2 = dataset2['tc_rmw'].sel(num_cases = l2, height = 3)

    data = xr.concat([data1, data2], dim="num_cases")
    rmw = xr.concat([rmw1, rmw2], dim = 'num_cases')
    data = data.assign_coords(longitude=((data.longitude - 100)).sortby('longitude'))
    data = data.assign_coords(latitude=((data.latitude - 100)).sortby('latitude'))

    print(data)

    # Get latitude and longitude values
    lats = data['latitude'].values
    lons = data['longitude'].values

    x, y = np.meshgrid(lons, lats)
    radii = np.sqrt(x**2 + y**2)
    bins = np.arange(0, 21, 1)
    print(bins)

    binsMean = []
    binsMin = []
    binsMax = []
    for x in range(len(bins) - 1):
        binContents = []
        for y in range(len(lons)):
            for z in range(len(lats)):
                if bins[x] <= radii[y, z] < bins[x + 1]:
                    print(data.sel(longitude = lons[y], latitude = lats[z]).values)
                    binContents.append(data.sel(longitude = lons[y], latitude = lats[z]).values)
        binsMean.append(np.nanmean(binContents))      
        binsMin.append(np.nanpercentile(binContents, 33))      
        binsMax.append(np.nanpercentile(binContents, 66))  

    return binsMean, binsMin, binsMax, range(len(bins) - 1)

    
t = 'Alignment'
height = 1

binsMean, binsMin, binsMax, bins = binFunc('Alignment', height)
binsMean2, binsMin2, binsMax2, bins = binFunc('Misalignment', height)

fig = plt.figure(figsize=(14, 7))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)

# Add state boundaries to plot
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Vorticity (1/s)', weight = 'bold', size = 9)
ax.set_xlabel('Distance in Kilometers', weight = 'bold', size = 9)
ax.set_ylim(0, 0.003)

ax.plot(bins, binsMean, linewidth = 2.5, color = '#202040')
ax.fill_between(bins, binsMin, binsMax, color='#8f8fbf', label = 'Aligning')    
ax.scatter(bins, binsMean, color = '#202040', zorder = 10)

ax.plot(bins, binsMean2, linewidth = 2.5, color = '#204020')
ax.fill_between(bins, binsMin2, binsMax2, color='#8fbf8f', label = 'Misaligning')    
ax.scatter(bins, binsMean2, color = '#204020', zorder = 10)

plt.legend()

ax.set_title(f'TC-RADAR: Radial Mean Relative Vorticity Profile\n{height} Kilometers', fontweight='bold', fontsize=10, loc='left')
ax.set_title('Deelan Jariwala', fontsize=10, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\windlineplot2.png", dpi = 400, bbox_inches = 'tight')

plt.show()