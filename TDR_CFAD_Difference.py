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
        ax.text(1 * np.pi / 4, 2, 'Downtilt\nRight', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(3 * np.pi / 4, 2, 'Uptilt\nRight', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(5 * np.pi / 4, 2, 'Uptilt\nLeft', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        ax.text(7 * np.pi / 4, 2, 'Downtilt\nLeft', size = 12, color = 'black', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center')
        
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
    # shd = 360 - dataset['sddc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    shd = 180 - np.nanmax(dataset['tc_tilt_direction'].sel(num_cases = case, height = [5, 5.5, 6.0, 6.5]).values) * (180 / np.pi)
    print("Case: ", case)
    print('Shear direction', shd)
    print('Radius of Max Wind:', rmw, '\n')
    data = []
    for x in range(len(var)):
        allLevels = []
        for y in levels:
            temp = dataset[var[x]].sel(num_cases = case, height = y)

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
    dataset = dataset.assign_coords(longitude=((dataset.longitude - 100)).sortby('longitude'))
    dataset = dataset.assign_coords(latitude=((dataset.latitude - 100)).sortby('latitude'))

    refl = []
    winds = []
    for x in range(len(list)):
        dat, vmax = getData(dataset, ['swath_upward_air_velocity'], np.arange(0.5, 10.5, .5), list[x])

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

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")
t = 'difference'
quad = 'Uptilt Left'

# if t == 'Alignment':
d1 = [225,251,252,253,254,333,334,347,374,376,377,407,408,409,410,413,414,603,604,605,672]
list2 = [719,752,765,767,794,878,879,939,941,957,968,969,970,971,1057,1073,1101,1131,1148,1177,1178,1179,1180,1191,1192,1220,1222,1223,1224,1226,1227,1228,1301,1302,1305]
d2 = [x - 710 for x in list2]
# elif t == 'Misalignment':
i1 = [148,149,222,224,339,340,341,342,343,344,382,383,384,402,423,424,425,426,427,429,430,431,545,600,601]
list2 = [742,744,745,747,869,898,899,918,919,930,934,935,936,1040,1049,1175,1195,1197,1201,1217,1218]
i2 = [x - 710 for x in list2]
# else:
#     list1 = [488, 489]
#     list2 = []
    
inc1, wind1 = makeComposites(dataset1, i1)
inc2, wind2 = makeComposites(dataset2, i2)
inc = inc1 + inc2
valid_nums = np.count_nonzero(~np.isnan(inc), axis = 0)

cfadComposite = []
for x in range(len(inc)):
    temp = inc[x]
    temp.values = np.where(valid_nums > (np.nanmax(valid_nums) / 3), temp.values, np.nan)
    temp = temp.sortby('theta')
    # temp = temp.sel(theta = slice(np.pi / 2, np.pi)) # Upshear Right
    # temp = temp.sel(theta = slice(-np.pi / 2, 0))    # Downshear Left
    # temp = temp.sel(theta = slice(0, np.pi / 2))     # Downshear Right
    temp = temp.sel(theta = slice(-np.pi, -np.pi / 2)) # Upshear Left
    # temp = temp.sel(theta = slice(-np.pi, 0)) # Left of Shear/Tilt
    # temp = temp.sel(theta = slice(0, np.pi))    # Right of Shear/Tilt

    # temp = temp.sel(r = slice(0, 1))

    grid1, grid2, data = CFAD(temp)
    cfadComposite.append(data)
incCFAD = np.nanmean(cfadComposite, axis = 0)

dec1, wind1 = makeComposites(dataset1, d1)
dec2, wind2 = makeComposites(dataset2, d2)
dec = dec1 + dec2
valid_nums = np.count_nonzero(~np.isnan(dec), axis = 0)

cfadComposite = []
for x in range(len(dec)):
    temp = dec[x]
    temp.values = np.where(valid_nums > (np.nanmax(valid_nums) / 3), temp.values, np.nan)
    temp = temp.sortby('theta')
    # temp = temp.sel(theta = slice(np.pi / 2, np.pi)) # Upshear Right
    # temp = temp.sel(theta = slice(-np.pi / 2, 0))    # Downshear Left
    # temp = temp.sel(theta = slice(0, np.pi / 2))     # Downshear Right
    temp = temp.sel(theta = slice(-np.pi, -np.pi / 2)) # Upshear Left
    # temp = temp.sel(theta = slice(-np.pi, 0)) # Left of Shear/Tilt
    # temp = temp.sel(theta = slice(0, np.pi))    # Right of Shear/Tilt

    # temp = temp.sel(r = slice(0, 1))

    grid1, grid2, data = CFAD(temp)
    cfadComposite.append(data)
decCFAD = np.nanmean(cfadComposite, axis = 0)

data = decCFAD - incCFAD

#data = gaussian_filter(data, sigma = 3)
fig, ax = plt.subplots(figsize = (8, 12))
c = plt.pcolormesh(grid1, grid2, data, cmap = cmap.tempAnoms(), vmin = -0.10, vmax = 0.10)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Tilt Alignnment - Non-Aligning {quad} CFAD\nVertical Velocity (>33% Valid Points)', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\TCTiltProject\NEWtdrcfaddiff_vvel_" + t + quad + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()

# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
# c = plt.pcolormesh(tCoords, refl[0].r, valid_nums, cmap = cmap.probs2(), vmin = 0, vmax = np.nanmax(valid_nums))
# cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
# ax.set_title(f'TC-RADAR: Normalized Tilt {t} Composite\nNumber of Valid Datapoints', fontweight='bold', fontsize=9, loc='left')
# ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
# plt.savefig(r"C:\Users\deela\Downloads\tdrcomp_validcounts_" + t + ".png", dpi = 400, bbox_inches = 'tight')

