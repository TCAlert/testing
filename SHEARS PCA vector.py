import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
np.set_printoptions(suppress=True)

class Normalizer:
    def __init__(self, data):
        self.data = data
        self.mean = data.mean(['case'])
        self.stdd = data.std(['case'])

    def normalize(self):
        all_zscores = ((self.data - self.mean) / self.stdd)
        return all_zscores.values

    def denormalize(self, data):
        return data * self.stdd + self.mean

def setUpHodo(ax, max, meanU, meanV):
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_frame_on(False)
    ax.grid(linewidth = 0.5, color = 'black', alpha = 0.5, linestyle = '--', zorder = 10)
    ax.axvline(x = 0, c = 'black', zorder = 0)
    ax.axhline(y = 0, c = 'black', zorder = 0)

    if max > .50:
        interval = .2
    elif max > 1.00:
        interval = .40
    else:
        interval = .1
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in np.arange(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

labelsize = 9
numOfEOFS = 28

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.lats > 0, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
pres = dataset.upper
case = dataset.case
print(dataset)

uData = dataset['u_data']
vData = dataset['v_data']

uData = np.nan_to_num(uData.to_numpy())
vData = np.nan_to_num(vData.to_numpy())
print(f"Initial shape: {uData.shape}")

newArray = np.stack([uData, vData], axis = 1)
norm = Normalizer(xr.DataArray(newArray, dims=('case', 'comp', 'upper')))
newArray = norm.normalize()
print(f"Stacked shape: {newArray.shape}")

# Flatten the 3D array to a 2D matrix (time, space)
time_steps, vector_size, vert_levs = newArray.shape
sst_reshaped = newArray.reshape(time_steps, vector_size * vert_levs)
print(f"Flattened shape: {sst_reshaped.shape}")

# Perform PCA to get the most prevalent patterns (EOFs)
pca = PCA(n_components = numOfEOFS)
PCs = pca.fit(sst_reshaped)

# Reshape the PCA results (EOFs) back to 4D (x, latitude, longitude)
EOFs = pca.components_.reshape(numOfEOFS, vector_size, vert_levs)
print(f"EOF matrix shape: {EOFs.shape}")

explained_variance = pca.explained_variance_ratio_
print(f"Explained variance: {explained_variance}")

pcseries = []
mean = []
std = []
# for i in range(numOfEOFS):
#     EOF = EOFs[i]
#     uEOF, vEOF = EOF[0], EOF[1]

#     fig = plt.figure(figsize=(15, 12))
#     gs = fig.add_gridspec(4, 12, wspace = 0, hspace = 0)
#     axes = [fig.add_subplot(gs[3, 0:6]),
#             fig.add_subplot(gs[0:3, 0:6]),
#             fig.add_subplot(gs[0:4, 7:12])]

#     test = PCs[:, i]
#     m, s = np.nanmean(test), np.nanstd(test)
#     test = np.array([(x - m) / s for x in test])
#     pcseries.append(test)
#     mean.append(m)
#     std.append(s)

#     # Add the map and set the extent
#     axes[0].set_frame_on(False)

#     # Add state boundaries to plot
#     axes[0].tick_params(axis='both', labelsize=8, left = False, bottom = False)
#     axes[0].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
#     axes[0].set_ylabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
#     axes[0].set_xlabel('Case', weight = 'bold', size = 9)
#     axes[0].axhline(color = 'black')
#     axes[0].plot(case, test, linewidth = 2, color = '#404040', label = f'PC{i + 1} Series')

#     axes[1] = setUpHodo(axes[1], np.nanmax((uEOF**2 + vEOF**2)**0.5), np.mean(uEOF), np.mean(vEOF))
#     c = axes[1].scatter(uEOF, vEOF, c = pres, linewidth = .5, vmin = 0, vmax = 1000, cmap = cmap.pressure(), zorder = 12)
#     colors = [cmap.pressure()(pres[l] / 1000) for l in range(len(pres))]
#     [axes[1].plot([u1, u2], [v1, v2], linewidth = 3, color = c, zorder = 11) for (u1, u2, v1, v2, c) in zip(uEOF[:-1], uEOF[1:], vEOF[:-1], vEOF[1:], colors)]

#     axes[1].set_title(f'SHEARS TC Hodograph EOF{i + 1} (Filters: SST >26C | 300-700mb RH > 40%)\nExplained variance: {round(float(explained_variance[i]) * 100, 1)}%' , fontweight='bold', fontsize=labelsize, loc='left')

#     axes[2].set_frame_on(False)
#     axes[2].tick_params(axis='both', labelsize=8, left = False, bottom = False)
#     axes[2].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
#     axes[2].set_xlabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
#     axes[2].set_ylabel('Following 24hr Change in VMax (kt)', weight = 'bold', size = 9)
#     #axes[2].yaxis.set_label_position("right")
#     #axes[2].yaxis.tick_right()
#     axes[2].axvline(color = 'black')
#     axes[2].axhline(color = 'black')
#     s = axes[2].scatter(test, dataset.delta_vmax.values, c = dataset.vmax, cmap = cmap.probs2(), linewidth = 2, label = f'PC{i + 1} Series')
#     cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
#     cbar.set_label('Maximum Sustained Wind (kt)')
#     axes[2].set_title(f'1997-2021\nDeelan Jariwala', fontsize=labelsize, loc='right')  

#     cbar = plt.colorbar(c, orientation = 'horizontal', aspect = 100, pad = .08)
#     cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
#     #cbar.set_ticks(np.arange(-1, 1.1, 0.1))
#     #plt.savefig(r"C:\Users\deela\Downloads\SHEARSVectorEOF" + str(i + 1) + ".png", dpi = 400, bbox_inches = 'tight')
#     #plt.show()

ds = xr.Dataset({'eof'    : (["num", "component", "level"], EOFs), 
                 'climoMean': (["component", "level"], norm.mean.values),
                 'climoStdd': (["component", "level"], norm.stdd.values)},
                 #'mean'   : (["num"], mean),
                 #'stddev' : (["num"], std)}, 
    coords =   {"num"  : np.arange(1, numOfEOFS + 1, 1),
                "component": [0, 1],
                "level": dataset.upper.values})

ds.to_netcdf(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")

name = 'All TCs'

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
#dataset = dataset.where(dataset.atcf == name, drop = True)
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.lats > 0, drop = True)
validCases = dataset['case']
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)

anom = np.nan_to_num((data - ds['climoMean'].values) / ds['climoStdd'].values)
pcseries = np.dot(anom.reshape(28167, 28), EOFs.reshape(28, 28).T)

fig = plt.figure(figsize=(15, 12))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'PC3 Series', weight = 'bold', size = 9)
ax.set_ylabel('PC2 Series', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')

s = plt.scatter(pcseries[:, 2], pcseries[:, 1], c = dataset.delta_vmax, s = 3, cmap = cmap.tempAnoms3(), linewidths=0, vmin = -60, vmax = 60, edgecolors='black', zorder = 6)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)#, ticks = [0, 34, 64, 83, 96, 113, 137])
cbar.set_label('Delta_VMax (kt)')

ax.set_title(f'SHEARS TC Hodograph PC2/PC3 Scatterplot\n{name.upper()}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSPC23.png", dpi = 400, bbox_inches = 'tight')
plt.show()
