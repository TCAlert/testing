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
from helper import helicity 
import random 

warnings.filterwarnings("ignore")
rcParams['font.family'] = 'Courier New'

def labels(ax, flag = False):
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    if flag == False:
        ax.text(1 * np.pi / 4, 2, 'Downshear\nRight', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(3 * np.pi / 4, 2, 'Upshear\nRight', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(5 * np.pi / 4, 2, 'Upshear\nLeft', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(7 * np.pi / 4, 2, 'Downshear\nLeft', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        
        ax.annotate('', xy=(0, 0.5), xytext=(np.pi, 0.5),
                arrowprops=dict(facecolor='black', edgecolor='black', width=1, headwidth=8, headlength=10, path_effects=[pe.withStroke(linewidth=2.25, foreground="white")]))

    ax.set_yticklabels(['', '', 'RMW', '', '2xRMW', '', '3xRMW', '', ''], fontfamily = 'Courier New', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")])
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontfamily = 'Courier New', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")])

def rePoPolar(dataset, offset = 0):
    x = dataset.longitude.values
    y = dataset.latitude.values
    x, y = np.meshgrid(x, y)

    r = np.sqrt(x**2 + y**2)
    t = np.arctan2(y, x)

    rBins = np.linspace(np.nanmin(r), np.nanmax(r), 200)
    tBins = np.linspace(np.nanmin(t), np.nanmax(t), 2000)

    for i in range(len(tBins)):
            tBins[i] = tBins[i] + offset
            while tBins[i] <= (-1 * np.pi):
                tBins[i] = tBins[i] + (2 * np.pi)
            while tBins[i] >= np.pi:
                tBins[i] = tBins[i] - (2 * np.pi)

    R, T = np.meshgrid(rBins, tBins)
    newX, newY = R * np.cos(T), R * np.sin(T)
    gridded_data = scipy.interpolate.griddata((x.flatten(), y.flatten()), dataset.values.flatten(), (newX.flatten(), newY.flatten()), method='nearest')

    polar = xr.Dataset(
        {
            'data': (('r', 'theta'), gridded_data.reshape(R.shape).transpose())
        },
        coords={
            'r': rBins,
            'theta': tBins
        }
    )

    return polar

def computeHelicity(dataset):
    data = dataset.sel(height = slice(0.5, 3))
    umotion = dataset['swath_earth_relative_eastward_wind'].sel(height = slice(0.5, 6.5)).mean(['height']).astype('float32')
    vmotion = dataset['swath_earth_relative_northward_wind'].sel(height = slice(0.5, 6.5)).mean(['height']).astype('float32')

    hgts = data.height
    print(hgts.values)
    arr1 = []
    for x in range(len(dataset.longitude)):
        arr2 = []
        for y in range(len(dataset.latitude)):
            uM = umotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            vM = vmotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            uwnd = data['swath_earth_relative_eastward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).astype('float32').values
            vwnd = data['swath_earth_relative_northward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).astype('float32').values
            if np.isnan(uwnd).any():
                temp = np.nan
            else:
                temp = helicity(hgts, uwnd, vwnd, uM, vM)
            arr2.append(temp)
        arr1.append(arr2)
    srh = np.array(arr1)

    return srh.T

def getData(dataset, var, levels, case):
    vmax = dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, height = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    # shd = 180 - np.nanmax(dataset['tc_tilt_direction'].sel(num_cases = case, height = [5, 5.5, 6.0, 6.5]).values) * (180 / np.pi)

    print('Shear direction', shd)
    print('Radius of Max Wind:', rmw)
    data = []
    for x in range(len(var)):
        temp = dataset[var[x]].sel(num_cases = case, height = levels[x])
        temp.values = computeHelicity(dataset.sel(num_cases = case))
    
        try:
            temp = temp.max(axis = 2)
        except:
            pass

        offset = (np.pi / 2) + np.deg2rad(shd)
        temp = rePoPolar(temp, offset)
        temp['r'] = temp['r'] / rmw
        rad = 4
        temp = temp['data'].sel(r = slice(0, rad))
        temp.values = np.flip(temp.values, axis = 1)
        newR = np.linspace(0, rad, 200)
        temp = temp.interp(r = newR)

        # fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        # ax.set_theta_zero_location("N")
        # ax.set_theta_direction(-1)
        # plt.pcolormesh(temp.theta, temp.r, temp.values)
        # plt.show()

        data.append(temp)    
    return data, vmax

def makeComposites(dataset, list):
    dataset = dataset.assign_coords(longitude=((dataset.longitude - 100)).sortby('longitude'))
    dataset = dataset.assign_coords(latitude=((dataset.latitude - 100)).sortby('latitude'))

    refl = []
    winds = []
    for x in range(len(list)):
        print(x)
        try:
            dat, vmax = getData(dataset, ['swath_reflectivity'], [0.5], list[x])

            refl.append(dat[0])
            winds.append(vmax)
        except:
            pass

    return refl, winds

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc")
t = 'Sheared Intensification'

if t == 'Alignment':
    list1 = [225,251,252,253,254,333,334,347,374,376,377,407,408,409,410,413,414,603,604,605,672]
    list2 = [719,752,765,767,794,878,879,939,941,957,968,969,970,971,1057,1073,1101,1131,1148,1177,1178,1179,1180,1191,1192,1220,1222,1223,1224,1226,1227,1228,1301,1302,1305]
    list2 = [x - 710 for x in list2]
if t == 'Non-Aligning':
    list1 = [148,149,222,224,339,340,341,342,343,344,382,383,384,402,423,424,425,426,427,429,430,431,545,600,601]
    list2 = [742,744,745,747,869,898,899,918,919,930,934,935,936,1040,1049,1175,1195,1197,1201,1217,1218]
    list2 = [x - 710 for x in list2]
if t == 'Test':
    list1 = []
    list2 = [1101, 1131]
    list2 = [x - 710 for x in list2]
if t == 'RI':
    dataset1['RI'] = (dataset1['vmax_ships'].sel(ships_lag_times=24) - dataset1['vmax_ships'].sel(ships_lag_times=0)) >= 30
    dataset2['RI'] = (dataset2['vmax_ships'].sel(ships_lag_times=24) - dataset2['vmax_ships'].sel(ships_lag_times=0)) >= 30
    list1 = []#134.0, 135.0, 136.0, 228.0, 229.0, 230.0, 260.0, 261.0, 262.0, 336.0, 337.0, 338.0, 456.0, 457.0, 458.0, 459.0, 460.0, 461.0, 514.0, 515.0, 516.0, 517.0, 561.0, 562.0, 563.0]
    for x in range(len(dataset1['RI'].values)):
        if dataset1['RI'].values[x] and (60 < dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100):
            list1.append(dataset1.num_cases.values[x])

    list2 = []#124.0, 125.0, 201.0, 202.0, 203.0, 254.0, 255.0, 256.0, 257.0, 426.0, 427.0, 428.0, 429.0, 430.0, 523.0, 524.0, 525.0, 526.0, 527.0, 528.0]
    for x in range(len(dataset2['RI'].values)):
        if dataset2['RI'].values[x] and (60 < dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100):
            list2.append(dataset2.num_cases.values[x])
    print(list1)
    print(list2)
if t == 'SI':
    dataset1['SI'] = ((dataset1['vmax_ships'].sel(ships_lag_times=24) - dataset1['vmax_ships'].sel(ships_lag_times=0)) >= 10) & ((dataset1['vmax_ships'].sel(ships_lag_times=24) - dataset1['vmax_ships'].sel(ships_lag_times=0)) <= 25)
    dataset2['SI'] = ((dataset2['vmax_ships'].sel(ships_lag_times=24) - dataset2['vmax_ships'].sel(ships_lag_times=0)) >= 10) & ((dataset2['vmax_ships'].sel(ships_lag_times=24) - dataset2['vmax_ships'].sel(ships_lag_times=0)) <= 25)
    list1 = []#[672.0, 347.0, 339.0, 76.0, 213.0, 327.0, 223.0, 578.0, 675.0, 591.0, 422.0, 585.0, 84.0, 375.0, 350.0, 594.0, 460.0, 154.0, 196.0, 402.0, 211.0, 680.0, 671.0, 322.0, 346.0]
    for x in range(len(dataset1['SI'].values)):
        if dataset1['SI'].values[x] and ((60 < dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100)):
            list1.append(dataset1.num_cases.values[x])

    list2 = []#[257.0, 495.0, 513.0, 60.0, 82.0, 396.0, 385.0, 228.0, 57.0, 436.0, 262.0, 506.0, 600.0, 539.0, 496.0, 37.0, 174.0, 366.0, 546.0, 512.0, 360.0, 467.0, 355.0, 351.0, 36.0]
    for x in range(len(dataset2['SI'].values)):
        if dataset2['SI'].values[x] and ((60 < dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100)):
            list2.append(dataset2.num_cases.values[x])
    # list1 = random.sample(list1, 25)
    # list2 = random.sample(list2, 25)

    print(list1, len(list1))
    print(list2, len(list2))
if t == 'Sheared Intensification':
    dataset1['RI'] = (dataset1['vmax_ships'].sel(ships_lag_times=24) - dataset1['vmax_ships'].sel(ships_lag_times=0)) > 0
    dataset2['RI'] = (dataset2['vmax_ships'].sel(ships_lag_times=24) - dataset2['vmax_ships'].sel(ships_lag_times=0)) > 0

    list1 = []
    for x in range(len(dataset1['RI'].values)):
        if dataset1['RI'].values[x] and ((dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100) & (dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] > 60)) and (15 <= np.nanmin(dataset1['shdc_ships'].sel(ships_lag_times = slice(0, 24)).values, 1)[x] <= 25):
            list1.append(dataset1.num_cases.values[x])

    list2 = []
    for x in range(len(dataset2['RI'].values)):
        if dataset2['RI'].values[x] and ((dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100) & (dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] > 60)) and (15 <= np.nanmin(dataset2['shdc_ships'].sel(ships_lag_times = slice(0, 24)).values, 1)[x] <= 25):
            list2.append(dataset2.num_cases.values[x])
    
    print(list1)
    print(list2)
if t == 'Sheared Weakening':
    dataset1['RI'] = (dataset1['vmax_ships'].sel(ships_lag_times=24) - dataset1['vmax_ships'].sel(ships_lag_times=0)) < 0
    dataset2['RI'] = (dataset2['vmax_ships'].sel(ships_lag_times=24) - dataset2['vmax_ships'].sel(ships_lag_times=0)) < 0

    list1 = []
    for x in range(len(dataset1['RI'].values)):
        if dataset1['RI'].values[x] and ((dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100) & (dataset1['vmax_ships'].sel(ships_lag_times = 0).values[x] > 60)) and (15 <= np.nanmin(dataset1['shdc_ships'].sel(ships_lag_times = slice(0, 24)).values, 1)[x] <= 25):
            list1.append(dataset1.num_cases.values[x])

    list2 = []
    for x in range(len(dataset2['RI'].values)):
        if dataset2['RI'].values[x] and ((dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] < 100) & (dataset2['vmax_ships'].sel(ships_lag_times = 0).values[x] > 60)) and (15 <= np.nanmin(dataset2['shdc_ships'].sel(ships_lag_times = slice(0, 24)).values, 1)[x] <= 25):
            list2.append(dataset2.num_cases.values[x])
    
    print(list1)
    print(list2)


refl1, wind1 = makeComposites(dataset1, list1)
refl2, wind2 = makeComposites(dataset2, list2)

refl = refl1 + refl2
wind = wind1 + wind2
meanWind = np.nanmean(wind)
mediWind = np.nanmedian(wind)
print(meanWind, mediWind)
# test = xr.merge(refl, compat = 'override')
test = xr.concat(refl, dim='case')
test = test.interp(theta = np.linspace(-1 * np.pi, np.pi, 2000))
print(test)
tCoords = test.theta

valid_nums = np.count_nonzero(~np.isnan(refl), axis = 0)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, valid_nums, cmap = cmap.probs2(), vmin = 0, vmax = np.nanmax(valid_nums))
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Shear-Relative {t} Composite\nNumber of Valid Datapoints', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\NEWtdrcomp_validcounts_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanmean(refl, axis = 0)
#data = gaussian_filter(data, sigma = 3)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 3), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.tempAnoms3(), vmin = -25, vmax = 25)
labels(ax)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Shear-Relative {t} Composite (>33% Valid Points)\n0.5-3km Storm-Relative Helicity', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\NEWtdrcomp_hel_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanstd(refl, axis = 0)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 3), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.probs2(), vmin = 0, vmax = 30)
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Shear-Relative {t} Composite\n0.5-3km Storm-Relative Helicity Standard Deviation', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\NEWtdrcomp_helstd_" + t + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()