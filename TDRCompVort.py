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

warnings.filterwarnings("ignore")
rcParams['font.family'] = 'Courier New'

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('longitude') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

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
    # shd = 180 - np.nanmax(dataset['tc_tilt_direction'].sel(num_cases = case, height = [5, 5.5, 6.0, 6.5]).values) * (180 / np.pi)

    print('Shear direction', shd)
    print('Radius of Max Wind:', rmw)
    data = []
    for x in range(len(var)):
        # Stretching Term
        # omega = 7.2921159e-5           
        # f = 2 * omega * np.sin(np.deg2rad(dataset['latitude']))
        # temp = dataset['swath_relative_vorticity'].sel(num_cases = case, height = levels[x]) + f
        # temp = temp.isel(latitude=slice(1, None), longitude=slice(1, None))

        # vert = dataset['swath_upward_air_velocity'].sel(num_cases = case).differentiate('height').sel(height = levels[x])
        vert = dataset['swath_upward_air_velocity'].sel(num_cases = case, height = levels[x])
        temp = vert

        u = dataset['swath_eastward_wind'].sel(num_cases = case, height = levels[x])
        ux, uy = Gradient2D(u)
        print(ux, uy)
        v = dataset['swath_northward_wind'].sel(num_cases = case, height = levels[x])
        vx, vy = Gradient2D(v)

        # temp = (ux + vy)

        # temp.values = -(temp.values*ux + temp.values*vy)

        # Vertical Advection Term
        # temp = dataset['swath_upward_air_velocity'].sel(num_cases = case, height = levels[x])
        # vort = dataset['swath_relative_vorticity'].sel(num_cases = case).differentiate('height').sel(height = levels[x])
        # temp.values = -temp.values * vort

        # temp = dataset['swath_relative_vorticity'].sel(num_cases = case, height = levels[x])



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
        print(x, '/', len(list))
        try:
            dat, vmax = getData(dataset, ['swath_reflectivity'], [2], list[x])

            refl.append(dat[0])
            winds.append(vmax)
        except:
            pass
    return refl, winds

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2023_xy_rel_swath_ships.nc")
t = 'Sheared Intensification'

# if t == 'Decrease2':
#     # Decrease 10km (<75kt)
#     list1 = [155.0, 167.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 451.0, 510.0, 524.0, 678.0]
#     list2 = [10.0, 18.0, 29.0, 35.0, 55.0, 61.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0, 510.0, 516.0, 586.0] 
# elif t == 'Decrease':
#     # Decrease 10km (all storms)
#     list1 = [155.0, 167.0, 176.0, 223.0, 255.0, 282.0, 287.0, 306.0, 311.0, 319.0, 332.0, 347.0, 374.0, 376.0, 407.0, 413.0, 424.0, 427.0, 431.0, 438.0, 451.0, 465.0, 510.0, 524.0, 533.0, 536.0, 566.0, 570.0, 606.0, 652.0, 678.0]
#     list2 = [10.0, 18.0, 24.0, 29.0, 35.0, 55.0, 61.0, 67.0, 87.0, 101.0, 108.0, 139.0, 148.0, 164.0, 166.0, 186.0, 187.0, 197.0, 205.0, 229.0, 232.0, 245.0, 249.0, 255.0, 347.0, 352.0, 358.0, 364.0, 374.0, 404.0, 420.0, 426.0, 464.0, 467.0, 468.0, 471.0, 510.0, 516.0, 540.0, 548.0, 565.0, 586.0, 604.0]        
# elif t == 'Increase':
#     # Increase 10km (all storms)
#     list1 = [99.0, 168.0, 220.0, 284.0, 308.0, 312.0, 313.0, 345.0, 375.0, 402.0, 422.0, 425.0, 545.0, 561.0, 580.0]
#     list2 = [21.0, 26.0, 32.0, 37.0, 58.0, 129.0, 142.0, 149.0, 164.0, 226.0, 349.0, 358.0, 464.0, 474.0, 487.0, 512.0, 529.0, 587.0, 605.0]
# else:
#     list1 = [488]
#     list2 = []

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
plt.savefig(r"C:\Users\deela\Downloads\TCTiltProject\NEWtdrcomp_validcounts_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanmean(refl, axis = 0)
#data = gaussian_filter(data, sigma = 3)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 3), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.tempAnoms3(), vmin = -2, vmax = 2)
labels(ax)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Shear-Relative {t} Composite (>33% Valid Points)\n2km Vertical Velocity', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\TCTiltProject\NEWtdrcomp_2vvel_" + t + ".png", dpi = 400, bbox_inches = 'tight')

data = np.nanstd(refl, axis = 0)
data = np.where(valid_nums > (np.nanmax(valid_nums) / 3), data, np.nan)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, refl[0].r, data, cmap = cmap.probs2(), vmin = 0, vmax = 5)
labels(ax, True)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
ax.set_title(f'TC-RADAR: Normalized Shear-Relative {t} Composite\n2km Vertical Velocity Standard Deviation', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Mean VMax: {str(int(meanWind))}kt\nDeelan Jariwala', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\TCTiltProject\NEWtdrcomp_2vvelstd_" + t + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()