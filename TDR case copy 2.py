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

def scatter(x, y, z = None):    
    fig = plt.figure(figsize=(14, 11))
    ax = plt.axes()

    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_xlabel(f'{x[0]}', weight = 'bold', size = 9)
    ax.set_ylabel(f'{y[0]}', weight = 'bold', size = 9)
    ax.axvline(color = 'black')
    ax.axhline(color = 'black')

    if z == None:
        ax.scatter(x[1], y[1], c = 'black', linewidth = 2)
    else:
        s = ax.scatter(x[1], y[1], c = z[1], cmap = cmap.probs2(), linewidth = 2)
        cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max')
        cbar.set_label(z[0])
    ax.set_title(f'TC-RADAR {x[0]}/{y[0]} Scatterplot\n1997-2023', fontweight='bold', fontsize=labelsize, loc='left')  
    ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\scattertest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()


def getData(dataset, var, levels, case):
    dvmax = dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 12).values - dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 0).values
    vmax = dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, height = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = case, height = [5, 5.5, 6.0, 6.5]).values)

    return dvmax, vmax, tilt

def makeComposites(dataset, list):
    dataset = dataset.assign_coords(longitude=((dataset.longitude - 100)).sortby('longitude'))
    dataset = dataset.assign_coords(latitude=((dataset.latitude - 100)).sortby('latitude'))

    winds = []
    winds2 = []
    winds3 = []
    for x in range(len(list)):
        dvmax, vmax, tilt = getData(dataset, ['swath_reflectivity', 'swath_vertical_velocity'], [3, [5, 5.5, 6, 6.5, 7, 7.5, 8]], list[x])

        winds.append(vmax)
        winds2.append(dvmax)
        winds3.append(tilt)

    return winds, winds2, winds3

def percentile(data, num):
    num = int(num / 100 * len(data))
    data = sorted(data)

    if num % 2 == 0:
        return ((data[num] + data[num - 1]) / 2)
    else:
        return data[num]
 

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")
#dataset = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')

t = 'ALL'

list1 = [220.0, 222.0, 282.0, 306.0, 311.0, 332.0, 345.0, 347.0, 374.0, 402.0, 403.0, 413.0, 422.0, 427.0, 510.0, 526.0, 545.0, 553.0, 600.0, 605.0]
list2 = [10.0, 18.0, 27.0, 29.0, 34.0, 36.0, 55.0, 62.0, 84.0, 94.0, 164.0, 169.0, 186.0, 197.0, 201.0, 206.0, 208.0, 224.0, 226.0, 227.0, 230.0, 245.0, 256.0, 339.0, 342.0, 347.0, 350.0, 356.0, 362.0, 391.0, 418.0, 422.0, 436.0, 464.0, 467.0, 485.0, 492.0, 510.0, 586.0, 599.0, 615.0]

dtilt1 = [-0.7331115, 0.5860064, -0.8836445, -0.77711403, 0.49372235, -0.73672867, 0.7709266, -0.76084834, -0.920009, 0.8705238, -0.7276519, -0.91235983, 1.7459958, -0.33612597, -0.32117432, -0.72268796, 0.88416666, -0.673586, -0.10602191, -0.8859232]
dtilt2 = [-0.83464056, 0.9586522, 3.2062068, -0.69993293, 1.7384574, -0.6833726, -0.82665294, -0.85921466, -0.8212267, -0.7520772, 0.75727105, -0.8676474, -0.44995874, -0.57170725, 4.123316, -0.7060517, 0.3993542, 0.8070842, 0.084011175, -0.72501194, -0.7000357, -0.87504464, -0.9166667, 1.6999773, -0.56248385, -0.7678205, 0.8028725, -0.6927933, -0.58774465, -0.7882524, -0.73927224, -0.69924337, -0.9998461, 0.8097343, -0.9060433, 2.30141, -0.70193857, -0.94692093, -0.64238775, 0.5959318, -0.7198928]      
dtilt = dtilt1 + dtilt2

vmax1, dvmax1, tilt1 = makeComposites(dataset1, list1)
vmax2, dvmax2, tilt2 = makeComposites(dataset2, list2)
vmax = vmax1 + vmax2
dvmax = dvmax1 + dvmax2
tilt = tilt1 + tilt2 

l1 = []
l2 = []
l3 = []
l4 = []
for x in range(len(vmax)):
    l1.append(dvmax[x])
    l2.append(dtilt[x])
    l3.append(vmax[x])
    l4.append(tilt[x])
print(f"Maximum Wind: {np.nanmax(l3)}kt\nNumber of Cases: {len(l3)}")
wind = l2

t1 = percentile(wind, 33)
t2 = percentile(wind, 66)

temp1 = []
temp2 = []
for x in range(len(wind)):
    if wind[x] < t1:
        temp1.append(wind[x])
    elif wind[x] > t2:
        temp2.append(wind[x])
print(f"Size of Lower Tercile: {len(temp1)}\nSize of Upper Tercile: {len(temp2)}")

scatter(["Change in Tilt (km)", l2], ["Initial Tilt (km)", l4], ["VMax (kt)", l3])
print(f"10%: {percentile(wind, 10)}\n25%: {percentile(wind, 25)}\n33%: {percentile(wind, 33)}\n50%: {percentile(wind, 50)}\n66%: {percentile(wind, 66)}\n75%: {percentile(wind, 75)}\n90%: {percentile(wind, 90)}\n")
print(f"Mean: {np.nanmean(wind)}\nMedian: {np.nanmedian(wind)}\nMax: {np.nanmax(wind)}\nMin: {np.nanmin(wind)}\nRange: {np.nanmax(wind) - np.nanmin(wind)}")

windHisto = np.histogram(wind)
fig = plt.figure(figsize=(14, 7))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Number of Storms', weight = 'bold', size = 9)
ax.set_xlabel('Change in Tilt (km)', weight = 'bold', size = 9)
# ax.set_ylim(0, 24)
# ax.set_xticks(np.arange(-30, 34, 4))
# ax.set_yticks(np.arange(0, 24, 2))

plt.title(f'TC-RADAR: Tilt {t} Change in Tilt Histogram\nNumber of Valid Datapoints: {len(wind)}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
plt.hist(wind, bins = np.arange(-5, 5, .1), color = '#9f80ff', alpha = 0.75)
#plt.savefig(r"C:\Users\deela\Downloads\tdrcasedist" + t + "ctilt2.png", dpi = 400, bbox_inches = 'tight')
plt.show()