import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmaps as cmap 
import scipy.stats as stats
import matplotlib.patheffects as pe
labelsize = 9

np.set_printoptions(suppress=True)

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['SD', 'TD', 'SS', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
print(dataset)

shears = dataset['sh_mag'].values
dtvmax = dataset['delta_vmax'].values
shears = np.nan_to_num(shears)
dtvmax = np.nan_to_num(dtvmax)
shearsShape = shears.shape
shears = shears.reshape(shearsShape[0], shearsShape[1] * shearsShape[2])

corrData = []
signData = []
for x in range(shears.shape[1]):
    shears[:, x] = np.nan_to_num(shears[:, x])
    corr, sig = stats.pearsonr(shears[:, x], dtvmax)
    corrData.append(corr)
    signData.append(sig)

corrData = np.nan_to_num(np.array(corrData))
shears = np.array(corrData).reshape(shearsShape[1], shearsShape[2])

fig = plt.figure(figsize=(15, 12))
ax = plt.axes()
ax.invert_xaxis()
ax.invert_yaxis()   
ax.set_ylabel('Pressure (Upper Bound)')
ax.set_xlabel('Pressure (Lower Bound)')
ax.grid() 
c = plt.pcolormesh(dataset.upper, dataset.lower, shears, cmap = cmap.tempAnoms3(), vmin = -.5, vmax = .5)
cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cb.set_ticks(np.arange(-.5, .55, .05))

for x in range(len(dataset.upper)):
    for y in range(len(dataset.lower)):
        if shears[x][y] != 0:
            plt.text(dataset.upper[y], dataset.lower[x], f'{"{:.2f}".format(shears[x][y], 2)}', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

plt.title(f'SHEARS Global TC Wind Shear Correlation to Intensification Rate\nClimatology: 1997-2021', fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARScorr.png", dpi = 400, bbox_inches = 'tight')
plt.show()