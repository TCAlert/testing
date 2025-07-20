import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cmaps as cmap
from scipy.stats import pearsonr
import pandas as pd 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature

def makeMap(ax, interval, labelsize):
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    ax.set_extent([-97.5, -42.5, 7.5, 37.5], crs = ccrs.PlateCarree(central_longitude=0))


    return ax 

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
    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = case, height = [5, 5.5, 6.0, 6.5]).values, axis = 1)

    lat = dataset['lat_ships'].sel(num_cases = case, ships_lag_times = 0).values
    lon = dataset['lon_ships'].sel(num_cases = case, ships_lag_times = 0).values

    hour = (dataset['swath_hour'] + ((360 - dataset['lon_ships']) / 15)) % 24
    dataset['solar_swath_hour'] = hour.where(hour < 24, hour - 24)

    hour = dataset['solar_swath_hour'].sel(num_cases = case, ships_lag_times = 0)
 

    return list(tilt), list(lat), list(-1 * lon)

def choose(t):
    if t == 'Alignment':
        list1 = [225,251,252,253,254,333,334,347,374,376,377,407,408,409,410,413,414,603,604,605,672]
        list2 = [719,752,765,767,794,878,879,939,941,957,968,969,970,971,1057,1073,1101,1131,1148,1177,1178,1179,1180,1191,1192,1220,1222,1223,1224,1226,1227,1228,1301,1302,1305]
        list2 = [x - 710 for x in list2]
    elif t == 'Misalignment':
        list1 = [148,149,222,224,339,340,341,342,343,344,382,383,384,402,423,424,425,426,427,429,430,431,545,600,601]
        list2 = [742,744,745,747,869,898,899,918,919,930,934,935,936,1040,1049,1175,1195,1197,1201,1217,1218]
        list2 = [x - 710 for x in list2]

    return list1, list2 

dataset1 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
dataset2 = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")

t = 'Alignment'
list1, list2 = choose(t)
data1, lat1, lon1 = getData(dataset1, list1)
data2, lat2, lon2 = getData(dataset2, list2)

adata = data1 + data2
alats = lat1 + lat2
alons = lon1 + lon2

t = 'Misalignment'
list1, list2 = choose(t)
data1, lat1, lon1 = getData(dataset1, list1)
data2, lat2, lon2 = getData(dataset2, list2)

mdata = data1 + data2
mlats = lat1 + lat2
mlons = lon1 + lon2

fig = plt.figure(figsize=(9, 12))
gs = fig.add_gridspec(4, 1, wspace = 0, hspace = 0)
axes = [fig.add_subplot(gs[2:3, 0]),
        fig.add_subplot(gs[0:2, 0], projection = ccrs.PlateCarree(central_longitude=180))]

axes[1] = makeMap(axes[1], 5, 8)
axes[1].scatter(alons, alats, c = 'C1', linewidth = 2, transform = ccrs.PlateCarree(central_longitude = 0))
axes[1].scatter(mlons, mlats, c = 'C0', linewidth = 2, transform = ccrs.PlateCarree(central_longitude = 0))

# Add the map and set the extent
axes[0].set_frame_on(False)
axes[0].tick_params(axis='both', labelsize=8, left = False, bottom = False)
axes[0].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
axes[0].set_ylabel('Number of Cases', weight = 'bold', size = 9)
axes[0].set_xlabel('Vortex Tilt (km)', weight = 'bold', size = 9)

plt.title(f'TC-RADAR: Aligning vs. Non-Aligning TC VMax Histogram and Distribution\nTotal Datapoints: {len(adata)} (A), {len(mdata)} (M)' , fontweight='bold', fontsize=9, loc='left')
print(f'{round(float(np.nanmean(mdata)), 1)}kt (M)')
plt.title(f'Mean Tilt: {round(float(np.nanmean(adata)), 1)}km (A)\n{round(float(np.nanmean(mdata)), 1)}km (M)', fontsize = 8, loc='right')  
axes[0].hist(adata, bins = np.arange(20, 205, 5), color = 'C1', alpha = 0.5, label = 'Aligning')
axes[0].hist(mdata, bins = np.arange(20, 205, 5), color = 'C0', alpha = 0.5, label = 'Non-Aligning')
axes[0].legend()
plt.savefig(r"C:\Users\deela\Downloads\tdr_dist_tilt.png", dpi = 400, bbox_inches = 'tight')

# wind = np.nan_to_num(mdata)
# print(f"01%: {percentile(wind, 1)}\n05%: {percentile(wind, 5)}\n10%: {percentile(wind, 10)}\n25%: {percentile(wind, 25)}\n33%: {percentile(wind, 33)}\n50%: {percentile(wind, 50)}\n66%: {percentile(wind, 66)}\n75%: {percentile(wind, 75)}\n90%: {percentile(wind, 90)}\n95%: {percentile(wind, 95)}\n99%: {percentile(wind, 99)}\n")
# print(f"Mean: {np.nanmean(wind)}\nMedian: {np.nanmedian(wind)}\nMax: {np.nanmax(wind)}\nMin: {np.nanmin(wind)}\nRange: {np.nanmax(wind) - np.nanmin(wind)}")

plt.show()

