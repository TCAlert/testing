import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap 
np.set_printoptions(suppress=True)

labelsize = 9
numOfEOFS = 3

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
    zscoreData = get_zscores(data)
    zscores = np.nan_to_num(zscoreData.to_numpy())
    print(f"Initial shape: {zscores.shape}")

    # Flatten the 3D array to a 2D matrix (time, space)
    time_steps, lat_size = zscores.shape
    sst_reshaped = zscores.reshape(time_steps, lat_size)
    print(f"Flattened shape: {sst_reshaped.shape}")

    # Perform PCA to get the most prevalent patterns (EOFs)
    pca = PCA(n_components = numOfEOFS)
    PCs = pca.fit_transform(sst_reshaped)
    print(f"PC matrix shape: {PCs.shape}")

    # Reshape the PCA results (EOFs) back to 3D (x, latitude, longitude)
    EOFs = np.zeros((numOfEOFS, lat_size))
    for i in range(numOfEOFS):
        EOFs[i, :] = pca.inverse_transform(np.eye(numOfEOFS)[i]).reshape(lat_size)
        #EOFs[i, :, :] = EOFs[i, :, :] / np.linalg.norm(EOFs[i, :, :], axis=1)[:, np.newaxis]
    print(f"EOF matrix shape: {EOFs.shape}")

    explained_variance = pca.explained_variance_ratio_
    print(f"Explained variance: {explained_variance}")

    return EOFs, PCs, explained_variance

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
    print(max)
    max = int(max + interval * 7)
    print(max)
    remainder = max % interval
    max = max - remainder
    print(max)

    for x in np.arange(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
pres = dataset.upper
climoMean = np.nanmean(dataset['sh_mag'].values, axis = 0)
climoStdd = np.nanstd(dataset['sh_mag'].values, axis = 0)

uData = dataset['u_data']
vData = dataset['v_data']
uEOFs, uPCs, uEV = constructEOF(uData)
vEOFs, vPCs, vEV = constructEOF(vData)

pcseries = []
mean = []
std = []
for i in range(numOfEOFS):
    uEOF = uEOFs[i]
    vEOF = vEOFs[i]
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(4, 12, wspace = 0, hspace = 0)
    axes = [fig.add_subplot(gs[3, 0:6]),
            fig.add_subplot(gs[0:3, 0:6]),
            fig.add_subplot(gs[0:4, 7:12])]

    uTest, vTest = uPCs[:, i], vPCs[:, i]
    m, s = np.nanmean(uTest), np.nanstd(uTest)
    uTest = np.array([(x - m) / s for x in uTest])
    m, s = np.nanmean(vTest), np.nanstd(vTest)
    vTest = np.array([(x - m) / s for x in vTest])
    test = (uTest**2 + vTest**2)**0.5
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

    axes[1] = setUpHodo(axes[1], np.nanmax((uEOF**2 + vEOF**2)**0.5), np.mean(uEOF), np.mean(vEOF))
    c = axes[1].scatter(uEOF, vEOF, c = pres, linewidth = .5, vmin = 0, vmax = 1000, cmap = cmap.pressure(), zorder = 12)
    colors = [cmap.pressure()(pres[l] / 850) for l in range(len(pres))]
    [axes[1].plot([u1, u2], [v1, v2], linewidth = 3, color = c, zorder = 11) for (u1, u2, v1, v2, c) in zip(uEOF[:-1], uEOF[1:], vEOF[:-1], vEOF[1:], colors)]

    axes[1].set_title(f'SHEARS TC Hodograph EOF{i + 1} (Filters: SST >26C | 300-700mb RH > 40%)\nExplained variance: {round(float(vEV[i]) * 100, 1)}%' , fontweight='bold', fontsize=labelsize, loc='left')

    axes[2].set_frame_on(False)
    axes[2].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[2].set_xlabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
    axes[2].set_ylabel('Following 24hr Change in VMax (kt)', weight = 'bold', size = 9)
    #axes[2].yaxis.set_label_position("right")
    #axes[2].yaxis.tick_right()
    axes[2].axvline(color = 'black')
    axes[2].axhline(color = 'black')
    s = axes[2].scatter(test, dataset.delta_vmax.values, c = dataset.vmax, cmap = cmap.probs2(), linewidth = 2, label = f'PC{i + 1} Series')
    cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.set_label('Maximum Sustained Wind (kt)')
    axes[2].set_title(f'1997-2021\nDeelan Jariwala', fontsize=labelsize, loc='right')  

    cbar = plt.colorbar(c, orientation = 'horizontal', aspect = 100, pad = .08)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    #cbar.set_ticks(np.arange(-1, 1.1, 0.1))
    plt.savefig(r"C:\Users\deela\Downloads\SHEARSHODOEOF" + str(i + 1) + ".png", dpi = 400, bbox_inches = 'tight')
    #plt.show()

# ds = xr.Dataset({'eof'    : (["num", "upper", "lower"], EOFs), 
#                  'climoMean': (["upper", "lower"], climoMean),
#                  'climoStdd': (["upper", "lower"], climoStdd),
#                  'mean'   : (["num"], mean),
#                  'stddev' : (["num"], std)}, 
#     coords =   {"num"  : np.arange(1, numOfEOFS + 1, 1),
#                 "upper": dataset.upper.values,
#                 "lower": dataset.lower.values})

# ds.to_netcdf(r"C:\Users\deela\Downloads\SHEARS_EOF_u.nc")

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
