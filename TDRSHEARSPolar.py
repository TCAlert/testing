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

def density(pres, sphum, temp):
    EPSILON = 0.622
    RV = 461.5
    R = 287

    w = sphum / (1 - sphum)

    vpprs = (pres + w) / (EPSILON + w)

    moist = vpprs / (RV * temp)
    dry = (pres - vpprs) / (R * temp)

    return moist + dry

def rePoPolar(dataset, name):
    x = dataset.lon.values
    y = dataset.lat.values
    x, y = np.meshgrid(x, y)

    r = np.sqrt(x**2 + y**2)
    t = np.arctan2(y, x)

    rBins = np.linspace(np.nanmin(r), np.nanmax(r), 120)
    tBins = np.linspace(np.nanmin(t), np.nanmax(t), 360)

    # for i in range(len(tBins)):
    #         tBins[i] = tBins[i] + offset
    #         while tBins[i] <= (-1 * np.pi):
    #             tBins[i] = tBins[i] + (2 * np.pi)
    #         while tBins[i] >= np.pi:
    #             tBins[i] = tBins[i] - (2 * np.pi)

    R, T = np.meshgrid(rBins, tBins)
    newX, newY = R * np.cos(T), R * np.sin(T)
    gridded_data = scipy.interpolate.griddata((x.flatten(), y.flatten()), dataset.values.flatten(), (newX.flatten(), newY.flatten()), method='nearest')

    polar = xr.Dataset(
        {
            name: (('r', 'theta'), gridded_data.reshape(R.shape).transpose())
        },
        coords={
            'r': rBins,
            'theta': tBins
        }
    )

    return polar

height = 400
data = xr.open_dataset(r"C:\Users\deela\Downloads\TC_Tilt_TCPRIMED_ERA5_Files.nc")
data = data.sel(level = height)
thetae = helper.thetae(data['temperature'], data['level'], 1000, data['sphum'])
u = data['u_data'] - data['uspd']
v = data['v_data'] - data['vspd']
rho = density(height * 100, data['sphum'], data['temperature'])
print(rho)
plt.pcolormesh(rho.lon, rho.lat, rho.sel(case = 305), cmap = cmap.probs2())
plt.colorbar()
plt.show()

thetaList = []
uList = []
vList = []
rhoList = []
print(len(data.case))
for x in range(len(data.case)):
    print(x)
    thetaList.append(rePoPolar(thetae.isel(case = x), 'thetae'))
    uList.append(rePoPolar(u.isel(case = x), 'u'))
    vList.append(rePoPolar(v.isel(case = x), 'v'))
    rhoList.append(rePoPolar(rho.isel(case = x), 'rho'))

print(thetaList)

thetae = xr.concat(thetaList, dim = 'case')
u = xr.concat(uList, dim = 'case')
v = xr.concat(vList, dim = 'case')
rho = xr.concat(rhoList, dim = 'case')

dataset = xr.merge([thetae, u, v, rho, data.atcf, data.time])
print(dataset)
# dataset.to_netcdf(r"C:\Users\deela\Downloads\ventilation_data.nc")
