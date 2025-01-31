import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import cmaps as cmap 
import boto3
from botocore import UNSIGNED
from botocore.config import Config

def setUpHodo(ax, max, meanU, meanV):
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_frame_on(False)
    ax.grid(linewidth = 0.5, color = 'black', alpha = 0.5, linestyle = '--', zorder = 10)
    ax.axvline(x = 0, c = 'black', zorder = 0)
    ax.axhline(y = 0, c = 'black', zorder = 0)

    if max > 50:
        interval = 10
    elif max > 100:
        interval = 20
    elif max < 1:
        interval = 0.1    
    else:
        interval = 5
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in np.arange(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
# dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
# dataset = dataset.where(dataset.landfall == False, drop=True)
# print(dataset)
# test = dataset['sh_mag'].mean('case')

# # Creates the plot
# fig = plt.figure(figsize=(15, 12))
# ax = plt.axes()
# ax.invert_xaxis()
# ax.invert_yaxis()
# ax.set_ylabel('Pressure (Upper Bound)')
# ax.set_xlabel('Pressure (Lower Bound)')
# ax.grid()

# # Plots the data using the pressure level grid created before
# # Note that the vectors in the plot are normalized by the magnitude of the shear
# c = ax.contourf(test.upper, test.lower, test.values * 1.944, cmap = cmap.shear(), levels = np.arange(0, 80, .1), extend = 'max')

# ax.set_title(f'SHEARS Mean TC Wind Shear (kts)\nClimatology: 1987-2023', fontweight='bold', fontsize=10, loc='left')
# ax.set_title('Deelan Jariwala', fontsize=10, loc='right') 

# cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# cb.set_ticks(range(0, 85, 5))

# plt.savefig(r"C:\Users\deela\Downloads\shearDiagnosticsClimo.png", dpi = 400, bbox_inches = 'tight')
# plt.show()

# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
# dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
# dataset = dataset.where(dataset.lats > 0, drop = True)
# dataset = dataset.where(dataset.landfall == False, drop=True)
# dataset = dataset.where(dataset.dist_land >= 0, drop=True)
# dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
# dataset = dataset.where(dataset.sst > 26, drop=True)
# # dataset = dataset.where(dataset.atcf.astype(str).str.startswith('WP'), drop = True)
# print(len(dataset.case.values))

# u = dataset['u_data'] * 1.944
# v = dataset['v_data'] * 1.944
# pres = dataset.upper 

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
print(dataset)
u = dataset['eof'].sel(component = 0)
v = dataset['eof'].sel(component = 1)

c = ['#bf3030', '#bf9b30', '#78bf30']

fig = plt.figure(figsize=(8, 8))
ax = plt.axes()
ax = setUpHodo(ax, np.nanmax((u**2 + v**2)**0.5), np.mean(u), np.mean(v))
for x in range(3):
    ax.plot(u.isel(num = x), v.isel(num = x), linewidth = 3, color = c[x], zorder = 11, alpha = .9, label = f'EOF #{x + 1}')

ax.set_title(f'First 3 Hodograph EOFs', fontweight='bold', fontsize=10, loc='left')
ax.set_title('\nDeelan Jariwala', fontsize=10, loc='right') 
ax.legend(loc = 'upper right')
plt.savefig(r"C:\Users\deela\Downloads\shearshodomean6.png", dpi = 400, bbox_inches = 'tight')
plt.show()