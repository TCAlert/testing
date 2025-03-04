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
    x = dataset.lons.values
    y = dataset.lats.values
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
    vmax = dataset['vmax_ships'].sel(num_cases = case, num_ships_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, level = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, num_ships_times = 0).values
    print("Case: ", case)
    print('Shear direction', shd)
    print('Radius of Max Wind:', rmw, '\n')
    data = []
    for x in range(len(var)):
        allLevels = []
        for y in levels:
            temp = dataset[var[x]].sel(num_cases = case, level = y)

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

            allLevels.append(temp)   
        temp = xr.concat(allLevels, dim = xr.DataArray(levels, dims = ['level'])) 
        data.append(temp)
    return data, vmax

def makeComposites(dataset, list):
    dataset = dataset.assign_coords(lons=((dataset.lons - 100)).sortby('lons'))
    dataset = dataset.assign_coords(lats=((dataset.lats - 100)).sortby('lats'))

    refl = []
    winds = []
    for x in range(len(list)):
        dat, vmax = getData(dataset, ['swath_vertical_velocity'], np.arange(0.5, 10.5, .5), list[x])

        refl.append(dat[0])
        winds.append(vmax)

    return refl, winds

def CFAD(data):
    refl = np.arange(-10, 10.5, .5)#np.arange(0, 55, 5)
    hgts = np.arange(0.5, 10.5, 0.5)
    grid = np.meshgrid(refl, hgts)

    bins = []
    for x in range(len(hgts)):
        temp = data.sel(level = hgts[x])

        for y in range(len(refl)):
            try:
                test = np.count_nonzero((temp > refl[y]) & (temp < refl[y + 1])) / np.count_nonzero(~np.isnan((temp.values)))
            except:
                test = np.nan
                pass
            bins.append(test)
    
    cfad = np.array(bins).reshape(grid[0].shape)
    # print(grid[0].shape, grid[1].shape, cfad.shape)
    # c = plt.pcolormesh(grid[0], grid[1], cfad, vmin = 0, vmax = 1, cmap = cmap.probs2())
    # cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    # plt.savefig(r"C:\Users\deela\Downloads\testcfad.png", dpi = 400, bbox_inches = 'tight')
    # plt.show()

    return grid[0], grid[1], cfad

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_2020_2022_xy_rel_swath_ships.nc")
t = 'difference'

d1 = [155.0, 167.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 451.0, 510.0, 524.0, 681.0]
d2 = [10.0, 18.0, 29.0, 35.0, 55.0, 61.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0] 
    # Increase 10km (all storms)
i1 = [99.0, 168.0, 220.0, 284.0, 308.0, 312.0, 313.0, 345.0, 375.0, 402.0, 422.0, 425.0, 545.0, 561.0]
i2 = [21.0, 26.0, 32.0, 37.0, 58.0, 129.0, 142.0, 149.0, 164.0, 226.0, 349.0, 358.0, 464.0, 474.0]

inc1, wind1 = makeComposites(dataset1, i1)
inc2, wind2 = makeComposites(dataset2, i2)
inc = inc1 + inc2
valid_nums = np.count_nonzero(~np.isnan(inc), axis = 0)

cfadComposite = []
for x in range(len(inc)):
    temp = inc[x]
    temp.values = np.where(valid_nums > (np.nanmax(valid_nums) / 2), temp.values, np.nan)

    grid1, grid2, data = CFAD(temp)
    cfadComposite.append(data)
incCFAD = np.nanmean(cfadComposite, axis = 0)

dec1, wind1 = makeComposites(dataset1, d1)
dec2, wind2 = makeComposites(dataset2, d2)
dec = dec1 + dec2
valid_nums = np.count_nonzero(~np.isnan(dec), axis = 0)

quad = 'OuterRadii'
cfadComposite = []
for x in range(len(dec)):
    temp = dec[x]
    temp.values = np.where(valid_nums > (np.nanmax(valid_nums) / 2), temp.values, np.nan)
    #temp = temp.sortby('theta')
    temp = temp.sel(r = slice(1, 4))
    # print(temp, np.nanmin(temp.theta.values), np.nanmax(temp.theta.values))

    # fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
    # c = plt.pcolormesh(temp.theta, temp.r, temp.sel(level = 3), cmap = cmap.tempAnoms())
    # labels(ax)
    # plt.show()

    grid1, grid2, data = CFAD(temp)
    cfadComposite.append(data)
decCFAD = np.nanmean(cfadComposite, axis = 0)

data = incCFAD - decCFAD

#data = gaussian_filter(data, sigma = 3)
fig, ax = plt.subplots(figsize = (8, 12))
c = plt.pcolormesh(grid1, grid2, data, cmap = cmap.tempAnoms(), vmin = -0.10, vmax = 0.10)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt Increase - Decrease2 {quad} CFAD\nVertical Velocity (>50% Valid Points)', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\tdrcfaddiff_vvel_" + t + quad + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()

# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
# c = plt.pcolormesh(tCoords, refl[0].r, valid_nums, cmap = cmap.probs2(), vmin = 0, vmax = np.nanmax(valid_nums))
# cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
# ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite\nNumber of Valid Datapoints', fontweight='bold', fontsize=9, loc='left')
# ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
# plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_validcounts_" + t + ".png", dpi = 400, bbox_inches = 'tight')

