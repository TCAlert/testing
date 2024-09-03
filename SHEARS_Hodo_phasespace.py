import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmaps as cmap 
np.set_printoptions(suppress=True)

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

labelsize = 9
storm = 'AL252005'
y = '2005'

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.atcf == storm, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))
uData = np.nan_to_num(dataset['u_data'].values)
vData = np.nan_to_num(dataset['v_data'].values)
pres = dataset.upper

data = np.stack([uData, vData], axis = 1)

eofData = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
anom = np.nan_to_num((data - eofData['climoMean'].values) / eofData['climoStdd'].values)

eofs = []
for x in range(len(eofData.eof.num.values)):
    eofs.append(np.nan_to_num(eofData['eof'].sel(num = x + 1).values))

pcseries1, pcseries2 = [], []
for x in range(len(data)):
    # temp = 0
    # for y in range(len(eofs)):
    #     proj = eofs[y].flatten() * np.dot(anom[x].flatten(), eofs[y].flatten().T)
    #     temp = temp + proj
    
    # temp = temp.reshape(2, 14)

    pc1 = np.dot(anom[x].flatten(), eofs[0].flatten().T)
    pc2 = np.dot(anom[x].flatten(), eofs[1].flatten().T)

    pcseries1.append(pc1)
    pcseries2.append(pc2)

fig = plt.figure(figsize=(14, 11))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'PC2 Series', weight = 'bold', size = 9)
ax.set_ylabel(f'PC1 Series', weight = 'bold', size = 9)
ax.axvline(color = 'black')
ax.axhline(color = 'black')
ax.plot(pcseries2, pcseries1, color = 'black', alpha = 0.5, linewidth = 0.5)

stat = dataset['system_type']
for x in range(len(stat)):
    if stat[x] in ['SD', 'SS']:
        ax.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6, marker = 's')
    elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
        ax.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), alpha = 0.375, vmin = 0, vmax = 140, linewidths=0.75, edgecolors='black', zorder = 6, marker = '^')
    else:
        s = plt.scatter(pcseries2[x], pcseries1[x], c = dataset.vmax[x], cmap = cmap.sshws(), linewidths=0.75, vmin = 0, vmax = 140, edgecolors='black', zorder = 6)
cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])
cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])
cbar.set_label('Maximum Sustained Wind (kt)')
ax.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical'), plt.Line2D([0], [0], marker = "^", markersize = 8, linewidth = 0, label = 'Non-TC')], loc = 'upper right')
ax.set_title(f'SHEARS TC Hodograph PC1/PC2 Scatterplot\n{storm.upper()}', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\SHEARSPCscatter.png", dpi = 400, bbox_inches = 'tight')
plt.show()
