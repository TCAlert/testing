import scipy.ndimage
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
import matplotlib.patheffects as pe
from scipy.ndimage import gaussian_filter
from matplotlib import rcParams
warnings.filterwarnings("ignore")
rcParams['font.family'] = 'Courier New'
labelsize = 9

def getData(dataset, var, levels, case):
    vmax = dataset['vmax_ships'].sel(num_cases = case, num_ships_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, level = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, num_ships_times = 0).values
    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = case, level = [5, 5.5, 6.0, 6.5]).values)

    return tilt

def makeComposites(dataset, list):
    dataset = dataset.assign_coords(lons=((dataset.lons - 100)).sortby('lons'))
    dataset = dataset.assign_coords(lats=((dataset.lats - 100)).sortby('lats'))

    winds = []
    for x in range(len(list)):
        vmax = getData(dataset, ['swath_reflectivity', 'swath_vertical_velocity'], [3, [5, 5.5, 6, 6.5, 7, 7.5, 8]], list[x])
        print(vmax)

        winds.append(vmax)

    return winds

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_2020_2022_xy_rel_swath_ships.nc")
t = 'Increase'

if t == 'Decrease2':
    # Decrease, 10km, <75kt
    list1 = [155.0, 167.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 451.0, 510.0, 524.0, 681.0]
    list2 = [10.0, 18.0, 29.0, 35.0, 55.0, 61.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0] 
elif t == 'Decrease':
    # Decrease, 10km
    list1 = [155.0, 167.0, 176.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 438.0, 451.0, 465.0, 510.0, 524.0, 533.0, 536.0, 566.0, 570.0, 609.0, 655.0, 681.0]
    list2 = [10.0, 18.0, 24.0, 29.0, 35.0, 55.0, 61.0, 67.0, 87.0, 101.0, 108.0, 139.0, 148.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 364.0, 374.0, 404.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0]
elif t == 'Increase':
    # Increase, 10km
    list1 = [99.0, 168.0, 220.0, 284.0, 308.0, 312.0, 313.0, 345.0, 375.0, 402.0, 422.0, 425.0, 545.0, 561.0]
    list2 = [21.0, 26.0, 32.0, 37.0, 58.0, 129.0, 142.0, 149.0, 164.0, 226.0, 349.0, 358.0, 464.0, 474.0]
else:
    list1 = [488]
    list2 = []
wind1 = makeComposites(dataset1, list1)
wind2 = makeComposites(dataset2, list2)

wind = wind1 + wind2
mean = np.nanmean(wind)
medi = np.nanmedian(wind)
range = np.nanmax(wind) - np.nanmin(wind)
print(mean, medi, np.nanmax(wind), np.nanmin(wind), range)

windHisto = np.histogram(wind)
fig = plt.figure(figsize=(18, 9))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Number of Storms', weight = 'bold', size = 9)
ax.set_xlabel('Maximum Sustained Wind (kt)', weight = 'bold', size = 9)
ax.set_ylim(0, 15)
ax.set_xticks(np.arange(20, 135, 5))
ax.set_yticks(np.arange(0, 15, 1))

plt.title(f'TC-RADAR: Tilt {t} Maximum Sustained Wind Histogram\nNumber of Valid Datapoints: {len(wind)}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
plt.hist(wind, bins = np.arange(20, 135, 5), color = '#9f80ff', alpha = 0.75)
#plt.savefig(r"C:\Users\deela\Downloads\tdrcasedist" + t + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()