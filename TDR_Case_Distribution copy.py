import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from scipy import stats

def percentile(data, num):
    num = int(num / 100 * len(data))
    data = sorted(data)

    if num % 2 == 0:
        return ((data[num] + data[num - 1]) / 2)
    else:
        return data[num]


def getData(dataset, case):
    dataset = dataset.assign_coords(longitude=((dataset.longitude - 100)).sortby('longitude'))
    dataset = dataset.assign_coords(latitude=((dataset.latitude - 100)).sortby('latitude'))

    vmax = dataset['vmax_ships'].sel(num_cases = case, ships_lag_times = 0).values
    rmw = dataset['tc_rmw'].sel(num_cases = case, height = 3).values / 2
    shd = 360 - dataset['sddc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(height = [5, 5.5, 6.0, 6.5]).values)

    shr = dataset['shdc_ships'].sel(num_cases = case, ships_lag_times = 0).values
    sst = dataset['sst_ships'].sel(num_cases = case, ships_lag_times = 0).values
    sst = sst[sst != 999.9]
    print(sst)
    rhm = dataset['rhmd_ships'].sel(num_cases = case, ships_lag_times = 0).values
    p200 = dataset['pw2m_ships'].sel(num_cases = case, ships_lag_times = 0).values
    s200 = dataset['pw5m_ships'].sel(num_cases = case, ships_lag_times = 0).values
    mpi = dataset['mpi_ships'].sel(num_cases = case, ships_lag_times = 0).values
    mshr = dataset['shrs_ships'].sel(num_cases = case, ships_lag_times = 0).values


    return list(vmax), list(shr), list(sst), list(rhm), list(mpi), list(mshr), list(p200), list(s200)

def choose(t):
    if t == 'Alignment':
        list1 = [225, 251, 252, 253, 254, 333, 334, 347, 374, 376, 377, 407, 408, 409, 410, 413, 414, 603, 604, 605, 672]
        list2 = [712, 719, 752, 765, 864, 878, 879, 939, 941, 957, 968, 969, 970, 971, 1057, 1073, 1101, 1128, 1131, 1148, 1177, 1178, 1179, 1180, 1191, 1192, 1220, 1221, 1222, 1223, 1224, 1226, 1227, 1228, 1302, 1379, 1380, 1391, 1405, 1406, 1445, 1446, 1447, 1448, 1453, 1471]
        list2 = [x - 710 for x in list2]
    elif t == 'Misalignment':
        list1 = [148, 149, 223, 224, 339, 340, 341, 342, 343, 344, 382, 383, 384, 386, 400, 402, 423, 424, 425, 426, 427, 429, 430, 431, 545, 600, 601]
        list2 = [742, 744, 745, 747, 757, 760, 869, 898, 899, 918, 919, 930, 934, 935, 936, 1042, 1052, 1174, 1175, 1195, 1197, 1201, 1217, 1218, 1372, 1373, 1376, 1377, 1408, 1410, 1418, 1419]
        list2 = [x - 710 for x in list2]

    return list1, list2 

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc")

t = 'Alignment'
list1, list2 = choose(t)
data1, shr1, sst1, rhm1, mpi1, mshr1, p2001, s2001 = getData(dataset1, list1)
data2, shr2, sst2, rhm2, mpi2, mshr2, p2002, s2002 = getData(dataset2, list2)

avmax = data1 + data2
ashrs = shr1 + shr2
assts = sst1 + sst2
arhms = rhm1 + rhm2 
ampi = mpi1 + mpi2 
amshr = mshr1 + mshr2 
ap200 = p2001 + p2002 
as200 = s2001 + s2002
ampi = ((100 - np.array(arhms)) * np.array(ashrs)) / np.array(ampi)
adata = [[avmax, ashrs, amshr, assts], [arhms, as200, ap200, ampi]]

t = 'Misalignment'
list1, list2 = choose(t)
data1, shr1, sst1, rhm1, mpi1, mshr1, p2001, s2001 = getData(dataset1, list1)
data2, shr2, sst2, rhm2, mpi2, mshr2, p2002, s2002 = getData(dataset2, list2)

bvmax = data1 + data2
bshrs = shr1 + shr2
bssts = sst1 + sst2
brhms = rhm1 + rhm2 
bmpi = mpi1 + mpi2 
bmshr = mshr1 + mshr2 
bp200 = p2001 + p2002 
bs200 = s2001 + s2002
bmpi = ((100 - np.array(brhms)) * np.array(bshrs)) / np.array(bmpi)
bdata = [[bvmax, bshrs, bmshr, bssts], [brhms, bs200, bp200, bmpi]]

names = [['a. Maximum Sustained Winds (kt)', 'b. Deep-Layer Wind Shear (kt)', 'c. Mid-Level Wind Shear (kt)', 'd. Sea Surface Temperature (C)'], ['e. Mid-Level Relative Humidity (%)', 'f. Mean PWAT 500km (mm)', 'g. Mean PWAT 200km (mm)', 'h. Ventilation Proxy']]
fig = plt.figure(figsize=(14, 12))
gs = fig.add_gridspec(2, 4, wspace = .2, hspace = .2)
axes = [fig.add_subplot(gs[0:1, 0:4]),
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[0, 2]),
        fig.add_subplot(gs[0, 3]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
        fig.add_subplot(gs[1, 2]),
        fig.add_subplot(gs[1, 3])]

axes[0].set_title(f'Aligning vs. Non-Aligning TC Environmental Violin Plots\nTotal Datapoints: {len(adata[0][0])} (A), {len(bdata[0][0])} (N)' , fontweight='bold', fontsize=9, loc='left')
axes[0].set_title(f'TC-RADAR\nBold = Statistically Significant', fontsize = 8, loc='right')  
axes[0].set_frame_on(False)
axes[0].set_xticks([])
axes[0].set_yticks([])

x = 0
for i in range(len(adata)):
    for j in range(len(adata[0])):
        print('\nname', 'type', 'range', 'iqr', 'median', 'mean')
        print(names[i][j], 'aligning', np.nanmax(adata[i][j]) - np.nanmin(adata[i][j]), np.nanpercentile(adata[i][j], 75) - np.nanpercentile(adata[i][j], 25), np.nanmean(adata[i][j]), np.nanmedian(adata[i][j]))
        print(names[i][j], 'misalign', np.nanmax(bdata[i][j]) - np.nanmin(bdata[i][j]), np.nanpercentile(bdata[i][j], 75) - np.nanpercentile(bdata[i][j], 25), np.nanmean(bdata[i][j]), np.nanmedian(bdata[i][j]))
        t_stat, p_value = stats.ttest_ind(adata[i][j], bdata[i][j], equal_var=False)
        print(f"t = {t_stat:.3f}, p = {p_value:.4f}")
        
        axes[x + 1].set_frame_on(False)
        axes[x + 1].tick_params(axis='both', labelsize=8, left = False, bottom = False)
        axes[x + 1].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

        if p_value < 0.05:
            axes[x + 1].set_xlabel(names[i][j], weight = 'bold', size = 9)
        else:
            axes[x + 1].set_xlabel(names[i][j], size = 9)
    
        axes[x + 1].set_xlim(0.5, 1.5)
        axes[x + 1].set_xticklabels([])

        axes[x + 1].scatter(1, np.nanmedian(adata[i][j]), c = 'C1', edgecolors = '#ff7f0e', marker = 'D', zorder = 10)
        axes[x + 1].scatter(1, np.nanmedian(bdata[i][j]), c = 'C0', edgecolors = '#1f77b4', marker = 'D', zorder = 10)

        violin = axes[x + 1].violinplot(bdata[i][j])
        for pc in violin['bodies']:
            pc.set_facecolor('C0')
        violin = axes[x + 1].violinplot(adata[i][j])
        for pc in violin['bodies']:
            pc.set_facecolor('C1')

        axes[x + 1].legend(handles=[mlines.Line2D([], [], color= 'C1', label='Aligning'), mlines.Line2D([], [], color= 'C0', label='Non-Aligning')], loc='upper left')
        x = x + 1
# plt.savefig(r"C:\Users\deela\Downloads\tdr_env_statsNEW.png", dpi = 400, bbox_inches = 'tight')

# wind = np.nan_to_num(mdata)
# print(f"01%: {percentile(wind, 1)}\n05%: {percentile(wind, 5)}\n10%: {percentile(wind, 10)}\n25%: {percentile(wind, 25)}\n33%: {percentile(wind, 33)}\n50%: {percentile(wind, 50)}\n66%: {percentile(wind, 66)}\n75%: {percentile(wind, 75)}\n90%: {percentile(wind, 90)}\n95%: {percentile(wind, 95)}\n99%: {percentile(wind, 99)}\n")
# print(f"Mean: {np.nanmean(wind)}\nMedian: {np.nanmedian(wind)}\nMax: {np.nanmax(wind)}\nMin: {np.nanmin(wind)}\nRange: {np.nanmax(wind) - np.nanmin(wind)}")

plt.show()

