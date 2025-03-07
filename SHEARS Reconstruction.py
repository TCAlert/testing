import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmaps as cmap
from scipy.stats import pearsonr
import pandas as pd 

def setUpHodo(max, meanU, meanV):
    meanU, meanV = 0, 0
    max = 5
    fig = plt.figure(figsize=(10, 8))

    ax = plt.axes()
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_frame_on(False)
    ax.grid(linewidth = 0.5, color = 'black', alpha = 0.5, linestyle = '--', zorder = 10)
    ax.axvline(x = 0, c = 'black', zorder = 0)
    ax.axhline(y = 0, c = 'black', zorder = 0)

    if max > 10:
        interval = 5
    elif max > 50:
        interval = 10
    elif max > 100:
        interval = 20
    else:
        interval = 2
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in range(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

# cases = [4, 5, 6, 66, 82, 83, 101, 103, 104, 106, 107, 108, 109, 129, 136, 165, 166, 169, 176, 264, 265, 282, 285, 287, 1426, 1653, 1654, 1655, 1693, 1695, 1696, 1762, 1766, 1927, 1928, 1965, 1966, 2050, 2051, 2054, 2055, 3578, 3621, 3622, 3631, 3850, 4088, 4202, 4223, 4232, 4264, 6683, 6870, 6977, 7150, 7302, 7303, 7335, 7368, 7371, 7461, 7462, 7564, 7579, 7591, 10106, 10145, 10148, 10150, 10175, 10176, 10177, 10733, 10930, 10931, 13402, 13503, 13574, 13580, 13649, 13698, 13699, 13741, 13937, 13938, 14140, 14254, 17081, 17151, 17194, 17427, 20470, 20792, 20794, 20796, 20799, 20850, 20852, 20854, 20856, 23907, 23908, 23909, 24127, 24129, 24130, 24188, 24191, 26660, 26661, 26710, 26751, 26846, 26876, 26878, 26879, 26881, 26889, 26890, 26891, 30645, 30714, 30717, 30819, 30862, 31113, 31115, 31211, 31286, 31287, 31344, 31345, 31369, 31694, 31696, 31700, 35245, 35404, 35481, 35565, 35566, 35692, 38257, 38258, 38260, 38270, 38335, 38340, 38341, 38398, 38401, 38402, 38403, 40527, 40973, 41123, 41124, 41147, 41148, 41149, 41416, 41425, 41655, 41665, 42071, 43234, 43279, 43451, 43452, 43461, 43641, 43642, 43720, 43724, 44009, 45818, 45821, 45823, 45830, 45832, 45844, 45853, 46278, 46279, 46280, 46281, 46623, 46624, 46635, 46636, 46930, 46975, 47116, 48384, 48385, 48771, 49434, 49435, 49436, 49438, 49538, 50914, 50916, 50918, 51297, 51298, 51299, 51300, 51301, 51429, 51477, 51478, 51480, 51486, 51772, 51845, 51846, 51997, 52279, 52280, 52537, 53654, 53961, 53983, 53984, 54296, 54374, 54492, 54595, 55008, 55165, 55446, 55447, 55448, 56326, 56327, 56329, 56789, 57136, 57138, 57317, 57374, 57464, 57465, 57505, 57625, 58028, 58029, 58030, 58119, 58120, 58123, 58306, 58473, 58477, 59617, 59715, 59716, 59886, 59887, 59888, 59889, 60162, 61796, 61972, 62033, 62062, 62111, 62150, 62507, 62510, 62530, 63027, 64536, 64981, 65003, 65169, 65829, 66078, 67082, 67083, 67409, 67785, 69235, 69620, 69879, 69880, 69881, 70027, 70220, 71411, 71413, 71761, 71763, 71765, 71961, 71963, 71965, 71968, 71969, 72013, 72017, 72018, 72020, 72021, 72089, 72093, 72344, 72488, 72489, 72497, 74270, 74271, 74508, 74509, 74510, 74511, 74810, 74945, 74946, 74950, 74951, 75209, 75210, 75211, 75212, 75286, 75289, 75345, 77184, 77599, 77715, 77716, 77717, 77941, 77942, 77944, 78347, 78350, 79824, 79825, 79862, 80396, 80446, 80561, 80707, 80708, 80735, 80790, 80838, 80872, 80874, 80959, 81223, 81224, 81312, 81314, 81315, 81621, 81714, 81859, 81860, 81880, 82931, 82935, 82943, 82986, 82988, 82989, 83045, 83046, 83170, 83348, 83349, 83350, 83351, 83539, 83962, 83998, 84140, 84341, 85484, 85768, 85769, 85770, 85771, 85912, 86282, 86489, 86533, 86560, 86780, 87593, 87594, 87595, 87793, 88174, 88235, 88236, 88237, 88244, 88542, 88544, 88619, 88620, 88621, 89390, 89391, 89441, 89480, 89482, 89536, 89828, 90740, 90741, 90742, 90986, 90988, 90989, 91308, 91510, 91512, 91607, 91679, 91773, 91943, 92611, 92719, 92720, 92721, 92722, 94136, 94284, 94286, 94816, 94835, 94837, 94838, 94976, 95229, 95330, 95417, 95449, 95450, 95537, 95581, 95584, 96942, 96997, 96998, 97252, 97253, 97254, 97458, 97459, 97651, 97652, 97658, 97763, 97764, 98350, 98351, 98381, 98382, 98553, 100487, 100550, 100616, 100683, 100879, 101235, 101323, 102588, 103292, 103294, 103295, 103296, 103349, 103943, 104423]
# coords = '[-20, 5, 0]'
# mean = "13.56"

PC1 = 5
PC2 = 5
PC3 = 0
t = 'coord'
csv = pd.read_csv(r"C:\Users\deela\Downloads\bins - PCs.csv")

if t == 'coord':
    csv = csv[(csv['PC1'] == PC1) & (csv['PC2'] == PC2) & (csv['PC3'] == PC3) & (csv['# of Cases'] > 30)]
    coords = str([PC1, PC2, PC3])
elif t == 'min':
    csv = csv[(csv['DVMax'] == np.nanmin(csv['DVMax'])) & (csv['# of Cases'] > 30)]
    coords = str([csv['PC1'], csv['PC2'], csv['PC3']])
elif t == 'max':
    csv = csv[(csv['DVMax'] == np.nanmax(csv['DVMax'])) & (csv['# of Cases'] > 30)]
    coords = str([csv['PC1'], csv['PC2'], csv['PC3']])

cases = list(map(int, str(csv['Case List'].values[0][1:-1]).split(', ')))
mean = csv['DVMax'].values[0]
numCases = csv['# of Cases'].values[0]
print(cases)

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(dataset['atcf'].sel(case = cases).values)
# dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
# dataset = dataset.where(dataset.sst > 26, drop=True)
# dataset = dataset.where(dataset.dist_land != 0, drop=True)
# dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
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
plt.savefig(r"C:\Users\deela\Downloads\EOFs\reconstructedNeutral.png", dpi = 400, bbox_inches = 'tight')
plt.show() 
plt.close()