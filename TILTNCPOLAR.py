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
    x = dataset.density_x.values
    y = dataset.density_y.values
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

def add_storm_dim(dataset):
    dataset = dataset.assign_coords(case=("case", dataset["case_number_global"].values))
    
    return dataset

def getAngles(dataset, caseList):
    l = []
    for x in range(len(caseList)):
        value = caseList[x]
        temp = dataset.isel(num_cases = value)
        l.append(temp.values)
    return np.array(l)

def getData(dataset, case):
    shd = case

    print('Shear direction', shd)
    temp = dataset

    try:
        temp = temp.max(axis = 2)
    except:
        pass

    offset = (np.pi / 2) + np.deg2rad(shd)
    temp = rePoPolar(temp, offset)
    # rad = 4
    temp = temp['data']#.sel(r = slice(0, rad))
    temp.values = np.flip(temp.values, axis = 1)
    # newR = np.linspace(0, rad, 200)
    # temp = temp.interp(r = newR)

    # fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    # ax.set_theta_zero_location("N")
    # ax.set_theta_direction(-1)
    # plt.pcolormesh(temp.theta, temp.r, temp.values)
    # plt.show()

    return temp

def makeComposites(dataset, list):
    data = []
    for x in range(len(list)):
        dat = getData(dataset.isel(case = x), list[x])
        data.append(dat)

    return data

data = xr.open_mfdataset([r"C:\Users\deela\Downloads\split" + str(x) +"_analysis.nc" for x in range(1, 5)], preprocess = add_storm_dim)
print(list(data.variables))

tcradar = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')
sddc = tcradar["sddc_ships"].sel(ships_lag_times=0)
angles = 360 - getAngles(sddc, data.case_number_global.values)

tilt = data['density_model']
print(tilt)
clim = data['density_climosv']

tilt = makeComposites(tilt, angles)
clim = makeComposites(clim, angles)

print(tilt)

test = xr.concat(tilt, dim='case')
test = test.interp(theta = np.linspace(-1 * np.pi, np.pi, 2000))
tCoords = test.theta

data = np.nanmean(tilt, axis = 0) - np.nanmean(clim, axis = 0)
data = gaussian_filter(data, sigma = 1)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (12, 9))
c = plt.pcolormesh(tCoords, test[0].r, data, cmap = cmap.tempAnoms3(), vmin = -25, vmax = 25)
labels(ax)
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.title(f'TILT RF Climatology Prediction Density\nAverage of Splits' , fontweight='bold', fontsize=9, loc='left')
plt.title(f'TC-RADAR', fontsize=9, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\TILTVerificationCompositeOld.png", dpi = 400, bbox_inches = 'tight')
plt.show()