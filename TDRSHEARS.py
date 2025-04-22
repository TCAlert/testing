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
shears = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(shears.atcf.values)

def setUpHodo(ax, max, meanU, meanV):
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_frame_on(False)
    ax.grid(linewidth = 0.5, color = 'black', alpha = 0.5, linestyle = '--', zorder = 10)
    ax.axvline(x = 0, c = 'black', zorder = 0)
    ax.axhline(y = 0, c = 'black', zorder = 0)

    if max > 5:
        interval = 2
    elif max > 25:
        interval = 5
    elif max > 50:
        interval = 10
    elif max < 1:
        interval = 0.1    
    else:
        interval = 5
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in np.arange(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

def getData(t):
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

    data1 = dataset1.sel(num_cases = l1, ships_lag_times = 0)
    atcf = data1.tcid_ships.values
    time = [np.datetime64(f'{data1['swath_year'].values[x]}-{str(data1['swath_month'].values[x]).zfill(2)}-{str(data1['swath_day'].values[x]).zfill(2)}T{str(data1['swath_hour'].values[x]).zfill(2)}:{str(data1['swath_min'].values[x]).zfill(2)}') for x in range(len(l1))]
    data2 = dataset2.sel(num_cases = l2, ships_lag_times = 0)
    atcf = np.concatenate((atcf, data2.tcid_ships.values))
    time = np.concatenate((time, [np.datetime64(f'{data2['swath_year'].values[x]}-{str(data2['swath_month'].values[x]).zfill(2)}-{str(data2['swath_day'].values[x]).zfill(2)}T{str(data2['swath_hour'].values[x]).zfill(2)}:{str(data2['swath_min'].values[x]).zfill(2)}') for x in range(len(l2))]))
    rounded_time = []
    for dt in time:
        # Convert the datetime to minutes
        total_minutes = (dt - np.datetime64('1970-01-01T00:00:00')) // np.timedelta64(1, 'm')
        
        # Round to the nearest 6-hour (360 minutes) interval
        rounded_minutes = int(np.round(total_minutes / 360) * 360)
        print(rounded_minutes)
        
        # Convert back to datetime64
        rounded_dt = np.datetime64('1970-01-01T00:00:00') + np.timedelta64(rounded_minutes, 'm')
        rounded_time.append(rounded_dt)
    time = rounded_time

    uData = []
    vData = []
    validIDs = []
    for x in range(len(atcf)):
        temp = shears.where((shears.atcf == atcf[x]) & (shears.time == time[x]) ,drop=True)
        uData.append(temp['u_data'].values)
        vData.append(temp['v_data'].values)
        if atcf[x] not in validIDs:
            validIDs.append(atcf[x])
    print(validIDs)
    print(np.array(uData).shape)
    return np.nanmean(uData, axis = 0).squeeze(), np.nanmean(vData, axis = 0).squeeze(), shears['upper']


u1, v1, levels = getData('Alignment')
u2, v2, levels = getData('Misalignment')
u, v = np.array([u1, u2]), np.array([v1, v2])

c = ['#bf3030', '#bf9b30']
l = ['Alignment', 'Misalignment']

fig = plt.figure(figsize=(8, 8))
ax = plt.axes()
ax = setUpHodo(ax, np.nanmax((u**2 + v**2)**0.5), np.mean(u), np.mean(v))
for x in range(2):
    ax.plot(u[x], v[x], linewidth = 3, color = c[x], zorder = 11, alpha = .9, label = l[x])

ax.set_title(f'TC-RADAR Aligning vs. Misaligning Cases\nEnvironmental Wind Hodograph', fontweight='bold', fontsize=10, loc='left')
ax.set_title('\nDeelan Jariwala', fontsize=10, loc='right') 
ax.legend(loc = 'upper right')
# plt.savefig(r"C:\Users\deela\Downloads\tcradarhodo.png", dpi = 400, bbox_inches = 'tight')
plt.show()