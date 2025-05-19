import xarray as xr 
import matplotlib.pyplot as plt
import cmaps as cmaps 
import satcmaps as cmaps2
import numpy as np 
from helper import helicity

def Gradient2D(data):
    lon = 'NX'
    lat = 'NY'

    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff(lon)[:, 1:]
    dAy = data.diff(lat)[1:, :]

    # Compute the derivative of both the x and y coordinates
    dx = data[lon].diff(lon) 
    dy = data[lat].diff(lat)

    # Return dA/dx and dA/dy, where A is the original dataset
    print(dAx.shape, dx.shape)
    return dAx / dx, dAy / dy

fig = plt.figure(figsize=(14, 12))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

time = '0342'

try:
    data = xr.open_dataset(r"C:\Users\deela\Downloads\harvey_dda\dda\eastern_lobe\DDA_" + time + "_1.0.nc")
except:
    data = xr.open_dataset(r"C:\Users\deela\Downloads\harvey_dda\dda\western_lobe\DDA_" + time + "_1.0.nc")

height = 0

NX = data['NX'].values
NY = data['NY'].values

x = data['X']
y = data['Y']
z = data['Z']
hgts = [0, 1, 2, 3]

uData = data['U'].sel(NZ = hgts) 
vData = data['V'].sel(NZ = hgts) 
uMotion = data['U'].sel(NZ = [0, 1, 2, 3, 4, 5, 6]).mean('NZ')
vMotion = data['V'].sel(NZ = [0, 1, 2, 3, 4, 5, 6]).mean('NZ')

# arr1 = []
# for i in range(len(NX)):
#     arr2 = []
#     for j in range(len(NY)):
#         temp = helicity(hgts, uData.sel(NX = NX[i], NY = NY[j]), vData.sel(NX = NX[i], NY = NY[j]), uMotion.sel(NX = NX[i], NY = NY[j]).values, vMotion.sel(NX = NX[i], NY = NY[j]))
#         arr2.append(temp)
#     arr1.append(arr2)
# srh = np.array(arr1)

fxx, fxy = Gradient2D(uData.sel(NZ = 0))
fyx, fyy = Gradient2D(vData.sel(NZ = 0))

srh = fxy + fyx#fyx - fxy

# c = ax.pcolormesh(x, y, srh.T, cmap = cmaps.tempAnoms3(), vmin = -20, vmax = 20)
c = ax.pcolormesh(x, y, data['MAXDBZ'].sel(NZ = 0).T, cmap = 'Greys_r', vmin = 20, vmax = 50)
l = ax.pcolormesh(x[1:], y[1:], srh.T, cmap = 'seismic', alpha = 0.25, vmin = -10, vmax = 10)#, vmin = -1, vmax = 1)
# plt.clabel(l, inline=1, fontsize=10, fmt='%1.0f')
ax.set_title(f'Hurricane Harvey Dual Doppler Analysis (0.5km Reflectivity)\n0.5-3.5km Storm-Relative Helicity Overlay', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'08/26/2017 at {time}z', fontsize=9, loc='center') 
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
plt.savefig(r"C:\Users\deela\Downloads\harveydowvort2" + time + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()