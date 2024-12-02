import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmaps as cmap
from scipy.stats import pearsonr

def setUpHodo(max, meanU, meanV):
    fig = plt.figure(figsize=(10, 8))

    ax = plt.axes()
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
    else:
        interval = 5
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in range(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

cases = [1589, 3963, 6752, 6753, 6754, 6815, 6818, 6982, 17366, 27109, 27340, 27341, 27342, 30712, 30713, 31224, 37918, 37919, 37923, 37924, 37925, 38370, 40554, 40560, 40861, 40864, 40870, 41668, 41883, 41884, 44609, 46080, 47953, 47954, 48063, 48520, 49535, 49536, 50801, 50803, 56271, 61711, 61713, 61714, 61715, 61717, 61718, 61719, 61720, 62008, 62009, 64965, 66001, 66002, 66004, 66005, 69038, 69040, 69683, 75757, 75758, 77429, 83322, 85178, 85179, 87448, 89467, 91418, 91456, 91457, 92388, 92616, 97699, 100044, 100046, 100050, 103103, 103104, 103105, 103106, 103122]
coords = '[-30, 10, 5]'
mean = "19.2"

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(dataset['atcf'].sel(case = cases).values)
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
pres = dataset.upper
# dataset['case'] = np.arange(0, len(dataset.case.values))

print(dataset)

uData = dataset['u_data'].sel(case = cases)
vData = dataset['v_data'].sel(case = cases)

uData = np.nan_to_num(uData.to_numpy())
vData = np.nan_to_num(vData.to_numpy())
print(f"Initial shape: {uData.shape}")

newArray = np.stack([uData, vData], axis = 1)
print(f"Initial shape: {newArray.shape}")


ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
EOFs = (ds['eof'].values).reshape(28, 28)
print(ds['eof'])

max_num = 4

for i in range(1, max_num):
    test = (newArray.reshape(len(cases), 28)).dot(EOFs[:i, :].T)
    test = test.dot(EOFs[:i, :])

    test = test.reshape(len(cases), 2, 14)

uRM, vRM = np.mean(test[:, 0], axis = 0), np.mean(test[:, 1], axis = 0)

ax = setUpHodo(np.nanmax((uRM**2 + vRM**2)**0.5), np.mean(uRM), np.mean(vRM))
c = ax.scatter(uRM, vRM, c = pres, linewidth = .5, vmin = 0, vmax = 1000, cmap = cmap.pressure(), zorder = 12)
colors = [cmap.pressure()(pres[l] / 1000) for l in range(len(pres))]
[ax.plot([u1, u2], [v1, v2], linewidth = 3, color = c, zorder = 11) for (u1, u2, v1, v2, c) in zip(uRM[:-1], uRM[1:], vRM[:-1], vRM[1:], colors)]

ax.set_title(f'SHEARS Reconstructed PC1/PC2/PC3 Hodograph\n{coords}', fontweight='bold', fontsize=10, loc='left')

ax.set_title(f'N = {str(len(cases))}', fontsize = 10, loc = 'center')
ax.set_title(f'Avg DVMax: {mean}kt\nDeelan Jariwala', fontsize=10, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02, ticks = [200, 500, 700, 850, 1000])    
cbar.ax.set_yticklabels([200, 500, 700, 850, 1000])
cbar.ax.invert_yaxis()
#plt.savefig(r"C:\Users\deela\Downloads\EOFs\reconstructedLargest.png", dpi = 400, bbox_inches = 'tight')
plt.show() 
plt.close()