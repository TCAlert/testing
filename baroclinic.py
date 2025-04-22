import helper 
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
from scipy.ndimage import gaussian_filter
from helper import thetae, theta
warnings.filterwarnings("ignore")

EPSILON = 0.622
RV = 461.5
R = 287

def density(pres, sphum, temp):
    w = sphum / (1 - sphum)

    vpprs = (pres + w) / (EPSILON + w)

    moist = vpprs / (RV * temp)
    dry = (pres - vpprs) / (R * temp)

    return moist + dry

def Gradient2D(data, short = False):
    if short == True:
        lon = 'lon'
        lat = 'lat'
    else:
        lon = 'longitude'
        lat = 'latitude'
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff(lon)[1:, :]
    dAy = data.diff(lat)[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data[lon].diff(lon) * np.cos(data[lat] * (np.pi / 180)) 
    dy = data[lat].diff(lat)

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

def Tv(t, q):
    w = q / (1 - q)

    return t * (1 + (0.61 * w))

#155 AL072022 20220923 1800

height = 500
storm = 'AL062022'
time = '2022-09-02T18'

data = xr.open_dataset(r"C:\Users\deela\Downloads\TCRADAR_ERA5_FULL.nc")
print(list(set(data.atcf.values)))
filtered = data.where(data['atcf'] == storm, drop=True)
filtered = data.where(data['time'] == np.datetime64(time), drop = True)
print(filtered.case)
print(filtered.time)
data = data.sel(level = height, case = filtered.case.values[0])#.mean('case')
sph = data['sphum']
tem = data['temperature']
rho = density(height * 100, data['sphum'], data['temperature'])
vtm = Tv(tem, sph)

drdx, drdy = Gradient2D(rho, short = True)
dtdx, dtdy = Gradient2D(tem, short = True)
dqdx, dqdy = Gradient2D(sph, short = True)
# dudx, dudy = Gradient2D(data['u_data'] * 1.94384, short = True)
# dvdx, dvdy = Gradient2D(data['v_data'] * 1.94384, short = True)

div = thetae(tem, height, 1000, sph)#dudx + dvdy#dvdx - dudy
#div = theta(tem, height, 1000)
#div = gaussian_filter(div, sigma = 3)

baroclinicity = -1 * (R / rho**2) * (
                               (drdx * (dtdy + (0.61 * (dtdy * (sph / (1 - sph))) + (tem / ((1 - sph)**2))) * dqdy) * rho)
                             - (drdy * (dtdx + (0.61 * (dtdx * (sph / (1 - sph))) + (tem / ((1 - sph)**2))) * dqdx) * vtm)
                               )
baroclinicity = gaussian_filter(baroclinicity, sigma = 3)

fig, axes = plt.subplots(2, 3, figsize=(18, 9))

c = axes[0, 0].pcolormesh(data.lon.values[1:], data.lat.values[1:], baroclinicity, cmap = cmap.tempAnoms3(), vmin = -300, vmax = 300)
print(data)
axes[0, 0].streamplot(data.lon.values, data.lat.values, data['u_data'].values, data['v_data'].values, linewidth = 1, density = 1, color=(0, 0, 0, 0.5))
axes[0, 0].set_title('Baroclinicity?')
plt.colorbar(c, ax = axes[0, 0])

c = axes[0, 1].pcolormesh(data.lon.values, data.lat.values, tem - 273.15, vmin = -80, vmax = 40, cmap = cmap.tempC())
axes[0, 1].set_title('Temperature (C)')
plt.colorbar(c, ax = axes[0, 1])

c = axes[0, 2].pcolormesh(data.lon.values, data.lat.values, div, cmap = cmap.probs2())
# axes[0, 2].streamplot(data.lon.values, data.lat.values, data['u_data'].values, data['v_data'].values, linewidth = 1, density = 1, color=(0, 0, 0, 0.5))
axes[0, 2].set_title('Theta-E (K)')
plt.colorbar(c, ax = axes[0, 2])

c = axes[1, 0].pcolormesh(data.lon.values, data.lat.values, rho, cmap = cmap.probs2())#, vmin = 0, vmax = 0.01)
axes[1, 0].set_title('Density')
plt.colorbar(c, ax = axes[1, 0])

c = axes[1, 1].pcolormesh(data.lon.values, data.lat.values, sph / (1 - sph), cmap = cmap.probs2())
axes[1, 1].set_title('Mixing Ratio')
plt.colorbar(c, ax = axes[1, 1])

c = axes[1, 2].pcolormesh(data.lon.values, data.lat.values, sph, cmap = cmap.dewp())#, vmin = 0, vmax = 0.01)
axes[1, 2].set_title('Specific Humidity')
plt.colorbar(c, ax = axes[1, 2])

plt.suptitle(f'{height}mb, {storm} {time}')

plt.savefig(r"C:\Users\deela\Downloads\baroclinicitylol" + storm + time + ".png", dpi = 250, bbox_inches = 'tight')
plt.show()