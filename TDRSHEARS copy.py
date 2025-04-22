import helper 
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
from matplotlib import rcParams
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
warnings.filterwarnings("ignore")

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")
shears = xr.open_dataset(r"C:\Users\deela\Downloads\TC_Tilt_TCPRIMED_ERA5_Files.nc")
print(shears.atcf.values)

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
        
        # Convert back to datetime64
        rounded_dt = np.datetime64('1970-01-01T00:00:00') + np.timedelta64(rounded_minutes, 'm')
        rounded_time.append(rounded_dt)
    time = rounded_time

    data = []
    validIDs = []
    for x in range(len(atcf)):
        temp = shears.where((shears.atcf == atcf[x]) & (shears.time == time[x]) ,drop=True)
        data.append(temp)
        if atcf[x] not in validIDs:
            validIDs.append(atcf[x])
    print(validIDs)

    return xr.concat(data, dim = 'case')

def shearInset(ax, uwnd, vwnd, x, y):
    lon, lat = 40, 40
    boxXCoords = [x - 15, x + 15, x + 15, x - 15, x - 15]
    boxYCoords = [y - 15, y - 15, y + 15, y + 15, y - 15]
    for y in range(len(boxXCoords)):
        try:
            ax.plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'red', zorder = 20)
        except:
            pass
    r = Rectangle((lon - 15, lat - 15), 30, 30, zorder = 19, color = '#bfbfbf', alpha = 0.4)
    ax.add_patch(r)

    uwnd = uwnd * 1.9438
    vwnd = vwnd * 1.9438
    print(uwnd)

    mU = uwnd.sel(lat = slice(-15, 15), lon = slice(-15, 15)).mean(['lat', 'lon'])
    mU = (mU.sel(level = 200) - mU.sel(level = 850)).values
    mV = vwnd.sel(lat = slice(-15, 15), lon = slice(-15, 15)).mean(['lat', 'lon'])
    mV = (mV.sel(level = 200) - mV.sel(level = 850)).values
    mMag = (mU**2 + mV**2)**0.5
    print(mMag)
    ax.text(lon, lat + 7, f'Wind Shear', color = 'black', ha = 'center', fontsize = 12, fontweight = 'bold', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20)
    ax.text(lon, lat - 9, f'{round(mMag, 1)} knots', color = 'black', ha = 'center', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20)
    ax.quiver(np.array([lon]), np.array([lat - 1]), mU / mMag, mV / mMag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = '#ff5959', zorder = 20, path_effects = [pe.withStroke(linewidth=1.25, foreground="black")])

    return c

dataA = getData('Alignment').mean('case', skipna=True)
dataA['thetae'] = helper.thetae(dataA['temperature'], dataA['level'], 1000, dataA['sphum'])
dataM = getData('Misalignment').mean('case', skipna=True)
dataM['thetae'] = helper.thetae(dataM['temperature'], dataM['level'], 1000, dataM['sphum'])

data = dataA - dataM
level = 200
print(data)

# plt.imshow(dataA['thetae'].sel(level = 850) - dataM['thetae'].sel(level = 850))
# plt.show()
fig = plt.figure(figsize=(10, 8))
ax = plt.axes()

x, y = np.meshgrid(dataA['lon'], dataM['lat'])

ax.streamplot(x, y, data['u_data'].sel(level = level).values - data['uspd'].values, data['v_data'].sel(level = level).values - data['vspd'].values, linewidth = 1, density = 1, color = '#1a1a1a')

c = ax.contourf(dataA['lon'], dataM['lat'], data['thetae'].sel(level = level).values, levels = np.arange(-5, 5.1, .1), cmap = cmap.tempAnoms3(), extend = 'both')
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_title(f'TC-RADAR Aligning vs. Misaligning Cases Environmental Diagnostics\nDifference in {level}mb Theta-E, {level}mb Wind', fontweight='bold', fontsize=10, loc='left')
ax.set_title('ERA5\nDeelan Jariwala', fontsize=10, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_ticks(np.arange(-5, 6, 1))
cbar.set_label('Theta-E Difference (K)')

shearInset(ax, data['u_data'], data['v_data'], 40, 40)

# plt.savefig(r"C:\Users\deela\Downloads\tcradarthetae.png", dpi = 400, bbox_inches = 'tight')
plt.show()