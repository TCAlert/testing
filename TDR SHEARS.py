import scipy.ndimage
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
from matplotlib import patheffects
from scipy.ndimage import gaussian_filter
from matplotlib import rcParams
warnings.filterwarnings("ignore")
rcParams['font.family'] = 'Courier New'
labelsize = 9

def getNearestBDeckTime(dataset, cases):
    atcfTimes = []
    atcfIDs = []
    for x in range(len(cases)):
        data = dataset.sel(num_cases = cases[x])
        year = str(data['swath_year'].values)
        if int(year) < 2022:
            month = str(data['swath_month'].values).zfill(2)
            day = data['swath_day'].values
            time = data['swath_hour'].values + (data['swath_min'].values / 60)

            newTime = str(6 * round(time / 6)).zfill(2) 
            if int(newTime) == 24:
                newTime = '00'
                day = day + 1
            day = str(day).zfill(2)

            if int(day) > 31:
                month = str(int(month) + 1).zfill(2)
                day = '01'

            atcfTimes.append(np.datetime64(f'{year}-{month}-{day}T{newTime}'))
            atcfIDs.append(str(data['tcid_ships'].sel(num_ships_times = 0).values).upper())
        else:
            pass
    return atcfTimes, atcfIDs

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

times1, IDs1 = getNearestBDeckTime(dataset1, list1)
times2, IDs2 = getNearestBDeckTime(dataset2, list2)
times = times1 + times2
IDs = IDs1 + IDs2
print(len(times))

shears = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = shears.where(shears.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)

shears = shears.where(shears.time.isin(times), drop = True)
sTimes = shears['time'].values
sATCF = shears['atcf'].values
newATCF = []
for x in range(len(sTimes)):
    newATCF.append(f'{sATCF[x]}{str(sTimes[x])[:4]}')
shears['atcf'].values = newATCF
shears = shears.where(shears.atcf.isin(IDs), drop = True)
print(shears)

shears = shears.mean('case')
ushear = (shears['u_shrs'] - dataset['u_shrs'].mean()) * 1.944
vshear = (shears['v_shrs'] - dataset['v_shrs'].mean()) * 1.944
shrmag = 2.5 * (ushear**2 + vshear**2)**0.5
shears = (shears['sh_mag'] - dataset['sh_mag'].mean()) * 1.944

fig = plt.figure(figsize=(15, 12))
ax = plt.axes()
ax.invert_xaxis()
ax.invert_yaxis()   
ax.set_ylabel('Pressure (Upper Bound)')
ax.set_xlabel('Pressure (Lower Bound)')
ax.grid() 
c = plt.contourf(shears.upper, shears.lower, shears, cmap = cmap.tempAnoms(), levels = np.arange(-20, 20.1, 0.1))
ax.quiver(shears.upper, shears.lower, ushear / shrmag, vshear / shrmag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = 'black', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")])

cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cb.set_ticks(np.arange(-20, 20, 10))

plt.title(f'SHEARS: TDR-Derived Tilt Increase Cases\nShear Magnitude (kt)', fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSTDRAnom" + t + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()