import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
np.set_printoptions(suppress=True)

labelsize = 9
numOfEOFS = 12

def get_zscores(data):
    all_zscores = []
    tempData = data
    mean = tempData.mean(['case'])
    stdd = tempData.std(['case'])

    all_zscores = ((tempData - mean) / stdd)

    all_zscores = xr.DataArray(
        data=all_zscores,
        dims=('case', 'upper'),
        coords=dict(
            case=(["case"], data.case.values),
            upper=(["upper"], data.upper.values)
        ))

    return all_zscores

def constructEOF(data):
    zscoreData = data#get_zscores(data)
    zscores = np.nan_to_num(zscoreData.to_numpy())
    print(f"Initial shape: {zscores.shape}")

    # Flatten the 3D array to a 2D matrix (time, space)
    cases, levels = zscores.shape
    sst_reshaped = zscores.reshape(cases, levels)
    print(f"Flattened shape: {sst_reshaped.shape}")

    # Perform PCA to get the most prevalent patterns (EOFs)
    pca = PCA(n_components = numOfEOFS)
    PCs = pca.fit_transform(sst_reshaped)
    print(f"PC matrix shape: {PCs.shape}")

    # Reshape the PCA results (EOFs) back to 3D (x, latitude, longitude)
    EOFs = pca.components_
    print(f"EOF matrix shape: {EOFs.shape}")

    explained_variance = pca.explained_variance_ratio_
    print(f"Explained variance: {explained_variance}")

    return EOFs, PCs, explained_variance

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.lats > 0, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
climoMean = np.nanmean(dataset['u_data'].values, axis = 0)
climoStdd = np.nanstd(dataset['u_data'].values, axis = 0)

uData = dataset['u_data']
uEOFs, uPCs, uEV = constructEOF(uData)

pcseries = []
mean = []
std = []
for i in range(numOfEOFS):
    uEOF = uEOFs[i]
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(4, 12, wspace = 0, hspace = 0)
    axes = [fig.add_subplot(gs[3, 0:6]),
            fig.add_subplot(gs[0:3, 0:6]),
            fig.add_subplot(gs[0:4, 7:12])]

    test = uPCs[:, i]
    m, s = np.nanmean(test), np.nanstd(test)
    test = np.array([(x - m) / s for x in test])
    pcseries.append(test)
    mean.append(m)
    std.append(s)

    # Add the map and set the extent
    axes[0].set_frame_on(False)

    # Add state boundaries to plot
    axes[0].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[0].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[0].set_ylabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
    axes[0].set_xlabel('Case', weight = 'bold', size = 9)
    axes[0].axhline(color = 'black')
    axes[0].plot(dataset.case, test, linewidth = 2, color = '#404040', label = f'PC{i + 1} Series')

    axes[1].invert_yaxis()   
    axes[1].set_ylabel('Pressure (hPa)')
    axes[1].set_xlim(-3, 3)
    axes[1].grid()  
    axes[1].plot(uEOF, dataset.upper)
    axes[1].set_title(f'SHEARS TC Zonal Wind Profile EOF{i + 1} (Filters: SST >26C | 300-700mb RH > 40%)\nExplained variance: {round(float(uEV[i]) * 100, 1)}%' , fontweight='bold', fontsize=labelsize, loc='left')

    axes[2].set_frame_on(False)
    axes[2].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[2].set_xlabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
    axes[2].set_ylabel('Following 24hr Change in VMax (kt)', weight = 'bold', size = 9)
    axes[2].axvline(color = 'black')
    axes[2].axhline(color = 'black')
    s = axes[2].scatter(test, dataset.delta_vmax.values, c = dataset.vmax, cmap = cmap.probs2(), linewidth = 2, label = f'PC{i + 1} Series')
    cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.set_label('Maximum Sustained Wind (kt)')
    axes[2].set_title(f'1997-2021\nDeelan Jariwala', fontsize=labelsize, loc='right')  

    #plt.savefig(r"C:\Users\deela\Downloads\SHEARSUEOF" + str(i + 1) + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show()

ds = xr.Dataset({'eof'    : (["num", "upper"], uEOFs), 
                 'climoMean': (["upper"], climoMean),
                 'climoStdd': (["upper"], climoStdd),
                 'mean'   : (["num"], mean),
                 'stddev' : (["num"], std)}, 
    coords =   {"num"  : np.arange(1, numOfEOFS + 1, 1),
                "upper": dataset.upper.values})

ds.to_netcdf(r"C:\Users\deela\Downloads\SHEARS_EOF_u.nc")

# name = 'AL25'
# y = '2005'

# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
# dataset = dataset.where(dataset.atcf == name, drop = True)
# year = [str(x).split('-')[0] for x in dataset.time.values]
# dataset = dataset.assign(year = (['case'], year))
# dataset = dataset.where(dataset.year == y, drop = True)
# validCases = dataset['case']
# print(dataset)

# fig = plt.figure(figsize=(15, 12))
# ax = plt.axes()

# ax.set_frame_on(False)
# ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
# ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
# ax.set_xlabel(f'PC2 Series', weight = 'bold', size = 9)
# ax.set_ylabel('PC1 Series', weight = 'bold', size = 9)
# ax.axvline(color = 'black')
# ax.axhline(color = 'black')

# ax.plot(pcseries[1][int(validCases[0]):int(validCases[-1]) + 1], pcseries[0][int(validCases[0]):int(validCases[-1]) + 1], color = 'black', alpha = 0.5, linewidth = 0.5)
# stat = dataset['system_type']
# for x in range(len(stat)):
#     if stat[x] in ['SD', 'SS']:
#         ax.scatter(pcseries[1][int(validCases[0]):int(validCases[-1]) + 1][x], pcseries[0][int(validCases[0]):int(validCases[-1]) + 1][x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6, marker = 's')
#     elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
#         ax.scatter(pcseries[1][int(validCases[0]):int(validCases[-1]) + 1][x], pcseries[0][int(validCases[0]):int(validCases[-1]) + 1][x], c = dataset.vmax[x], cmap = cmap.sshws(), alpha = 0.375, vmin = 0, vmax = 140, linewidths=0.75, edgecolors='black', zorder = 6, marker = '^')
#     else:
#         s = plt.scatter(pcseries[1][int(validCases[0]):int(validCases[-1]) + 1][x], pcseries[0][int(validCases[0]):int(validCases[-1]) + 1][x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6)
# cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])
# cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])
# cbar.set_label('Maximum Sustained Wind (kt)')

# ax.set_title(f'SHEARS TC Vertical Wind Shear Distribution PC1/PC2 Scatterplot', fontweight='bold', fontsize=labelsize, loc='left')  
# ax.set_title(f'1997-2021\nDeelan Jariwala', fontsize=labelsize, loc='right')  
# plt.savefig(r"C:\Users\deela\Downloads\SHEARSUPCFull.png", dpi = 400, bbox_inches = 'tight')
# plt.show()
