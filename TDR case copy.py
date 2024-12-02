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

list1 = [99.0, 105.0, 111.0, 134.0, 153.0, 167.0, 174.0, 193.0, 220.0, 222.0, 228.0, 255.0, 259.0, 282.0, 287.0, 306.0, 308.0, 311.0, 313.0, 319.0, 324.0, 332.0, 345.0, 347.0, 350.0, 374.0, 376.0, 402.0, 403.0, 413.0, 422.0, 425.0, 429.0, 450.0, 456.0, 509.0, 510.0, 521.0, 523.0, 545.0, 551.0, 554.0, 580.0, 600.0, 603.0, 606.0, 609.0, 673.0, 676.0]
list2 = [42.0, 10.0, 13.0, 18.0, 21.0, 25.0, 29.0, 32.0, 35.0, 55.0, 58.0, 61.0, 65.0, 84.0, 91.0, 123.0, 164.0, 166.0, 186.0, 187.0, 197.0, 201.0, 205.0, 208.0, 224.0, 226.0, 227.0, 229.0, 232.0, 236.0, 245.0, 248.0, 255.0, 265.0, 339.0, 341.0, 347.0, 349.0, 352.0, 357.0, 363.0, 391.0, 418.0, 420.0, 423.0, 426.0, 436.0, 458.0, 464.0, 466.0, 468.0, 471.0, 474.0, 484.0, 488.0, 499.0, 510.0, 516.0, 519.0, 586.0, 597.0, 611.0]

dtilt1 = [0.42, 0.83, 4.38, 5.34, 5.53, 0.0, 11.15, 0.83, -83.87, 17.89, -0.25, -7.37, 5.42, -9.77, -11.73, -16.71, 10.2, 2.41, 5.83, -10.0, -2.79, -16.8, 72.27, -126.31, 2.62, -34.92, -22.85, 96.31, -136.94, -33.49, 17.97, 22.8, 1.07, -1.73, -0.32, 16.68, -8.57, -2.0, 4.17, 42.44, -11.23, -4.38, 51.58, 0.61, -44.9, -10.09, 1.53, 0.39, -12.79]
dtilt2 = [-146.61, -20.17, 4.25, -8.89, 1.77, 163.04, -120.61, 11.56, -14.26, -16.8, -1.26, 0.0, -15.61, -103.16, -8.29, 1.21, -5.01, -33.78, -8.64, -16.12, -37.75, 71.46, -58.78, 15.07, 42.37, 7.97, -64.37, -19.5, -16.15, 19.8, 0.7, -20.5, -15.53, 0.0, 90.95, -78.98, -59.89, 15.95, -1.75, 0.67, -22.79, -57.29, -81.46, -23.61, 2.72, -8.83, -1.54, 18.41, -23.38, 28.12, -51.9, 2.48, 5.66, 90.91, -66.68, -2.32, -20.95, -44.33, -5.53, -22.73, 5.79, -17.36]
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
plt.hist(wind, bins = np.arange(-30, 32, 2), color = '#9f80ff', alpha = 0.75)
#plt.savefig(r"C:\Users\deela\Downloads\tdrcasedist" + t + "ctilt2.png", dpi = 400, bbox_inches = 'tight')
plt.show()