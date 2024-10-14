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

def getData(dataset, var, levels, case):
    vmax = dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, height = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    print('Shear direction', shd)
    print('Radius of Max Wind:', rmw)
    data = []
    for x in range(len(var)):
        temp = dataset[var[x]].sel(num_cases = case, height = levels[x])
    
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
    dataset = dataset.assign_coords(latitue=((dataset.latitude - 100)).sortby('latitude'))

    refl = []
    vvel = []
    winds = []
    for x in range(len(list)):
        dat, vmax = getData(dataset, ['swath_reflectivity', 'swath_upward_air_velocity'], [3, [5, 5.5, 6, 6.5, 7, 7.5, 8]], list[x])

        refl.append(dat[0])
        vvel.append(dat[1])
        winds.append(vmax)

    return refl, vvel, winds

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_2020_2022_xy_rel_swath_ships.nc")
t = 'Decrease'

if t == 'Decrease2':
    # Decrease 10km (75kt)
    list1 = [155.0, 167.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 451.0, 510.0, 524.0, 681.0]
    list2 = [10.0, 18.0, 29.0, 35.0, 55.0, 61.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0] 
elif t == 'Decrease':
    # Decrease 10km (all storms) 
    list1 = [155.0, 167.0, 176.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 438.0, 451.0, 465.0, 510.0, 524.0, 533.0, 536.0, 566.0, 570.0, 609.0, 655.0, 681.0]
    list2 = [10.0, 18.0, 24.0, 29.0, 35.0, 55.0, 61.0, 67.0, 87.0, 101.0, 108.0, 139.0, 148.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 364.0, 374.0, 404.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0]
elif t == 'Increase':
    # Increase 10km (all storms)
    list1 = [99.0, 168.0, 220.0, 284.0, 308.0, 312.0, 313.0, 345.0, 375.0, 402.0, 422.0, 425.0, 545.0, 561.0]
    list2 = [21.0, 26.0, 32.0, 37.0, 58.0, 129.0, 142.0, 149.0, 164.0, 226.0, 349.0, 358.0, 464.0, 474.0]
else:
    list1 = [488]
    list2 = []
refl1, vvel1, wind1 = makeComposites(dataset1, list1)
refl2, vvel2, wind2 = makeComposites(dataset2, list2)

refl = refl1 + refl2
vvel = vvel1 + vvel2
wind = wind1 + wind2
meanWind = np.nanmean(wind)
mediWind = np.nanmedian(wind)
print(meanWind, mediWind)
test = xr.merge(refl)
test = test.interp(theta = np.linspace(-1 * np.pi, np.pi, 2000))
test['data'].plot()
plt.show()
print(test)
tCoords = test.theta

valid_nums = np.count_nonzero(~np.isnan(refl), axis = 0)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, valid_nums, cmap = cmap.probs2(), vmin = 0, vmax = np.nanmax(valid_nums))
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite\nNumber of Valid Datapoints', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_validcounts_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanmean(refl, axis = 0)
#data = gaussian_filter(data, sigma = 3)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 2), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.reflectivity2(), vmin = 0, vmax = 50)
labels(ax)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite (>50% Valid Points)\n3km Reflectivity', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_refl_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanmean(vvel, axis = 0)
#data = gaussian_filter(data, sigma = 3)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 2), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.tempAnoms3(), vmin = -2, vmax = 2)
labels(ax)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite (>50% Valid Points)\n5-8km Max Vertical Velocity', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_vvel_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanstd(vvel, axis = 0)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 2), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.probs2(), vmin = 0, vmax = 6)
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite\n5-8km Max Vertical Velocity Standard Deviation', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_vvelstd_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanstd(refl, axis = 0)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 2), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.probs2(), vmin = 0, vmax = 30)
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite\n3km Reflectivity Standard Deviation', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_reflstd_" + t + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()