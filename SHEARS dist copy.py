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
    ax.set_extent([0, 359, -10, 60], crs = ccrs.PlateCarree(central_longitude=180))

    
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

    # ax.set_extent([0, 359, -10, 60], crs = ccrs.PlateCarree(central_longitude=180))


    return ax 

def percentile(data, num):
    num = int(num / 100 * len(data))
    data = sorted(data)

    if num % 2 == 0:
        return ((data[num] + data[num - 1]) / 2)
    else:
        return data[num]

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(list(dataset.variables))
dataset = dataset
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
# dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
# dataset = dataset.where(dataset.sst > 26, drop=True)
# dataset = dataset.where(dataset.lats > 0, drop = True)
# dataset = dataset.where(dataset.fdelta_vmax >= 0, drop = True)
dataset = dataset.where(dataset.time > np.datetime64('2020-01-01T00'), drop = True)
dataset = dataset.where(dataset.atcf.astype(str).str.startswith('AL'), drop = True)
print(dataset['time'].values)
pres = dataset.upper

# print(dataset)

# uData = dataset['u_data'].sel(case = cases)
# vData = dataset['v_data'].sel(case = cases)

# uData = np.nan_to_num(uData.to_numpy())
# vData = np.nan_to_num(vData.to_numpy())
# print(f"Initial shape: {uData.shape}")

# newArray = np.stack([uData, vData], axis = 1)
# print(f"Initial shape: {newArray.shape}")


# ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
# EOFs = (ds['eof'].values).reshape(28, 28)
# print(ds['eof'])

# max_num = 4

# for i in range(1, max_num):
#     test = (newArray.reshape(len(cases), 28)).dot(EOFs[:i, :].T)
#     test = test.dot(EOFs[:i, :])

#     test = test.reshape(len(cases), 2, 14)

# uRM, vRM = np.mean(test[:, 0], axis = 0), np.mean(test[:, 1], axis = 0)

fig = plt.figure(figsize=(9, 12))
gs = fig.add_gridspec(4, 1, wspace = 0, hspace = 0)
axes = [fig.add_subplot(gs[2:3, 0]),
        fig.add_subplot(gs[0:2, 0], projection = ccrs.PlateCarree(central_longitude=180))]
axes[1] = makeMap(axes[1], 20, 8)
axes[1].scatter(dataset['lons'], dataset['lats'], c = 'black', linewidth = 2, transform = ccrs.PlateCarree(central_longitude = 0))

# Add the map and set the extent
axes[0].set_frame_on(False)
axes[0].tick_params(axis='both', labelsize=8, left = False, bottom = False)
axes[0].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
axes[0].set_ylabel('Number of Cases', weight = 'bold', size = 9)
axes[0].set_xlabel('DVMax (kt)', weight = 'bold', size = 9)

plt.title(f'SHEARS: NATL Future 24hr Intensity Change Distribution (+)\nTotal Datapoints: {len(dataset["fdelta_vmax"])}' , fontweight='bold', fontsize=9, loc='left')
plt.title(f'Mean DVMax: {np.nanmean(dataset["fdelta_vmax"].values)}kt\nDeelan Jariwala', fontsize = 9, loc='right')  
axes[0].hist(dataset['fdelta_vmax'], bins = np.arange(-50, 55, 5), color = '#9f80ff', alpha = 0.75)
#plt.savefig(r"C:\Users\deela\Downloads\IntensificationDistribution.png", dpi = 400, bbox_inches = 'tight')

wind = np.nan_to_num(dataset['fdelta_vmax'].values)
print(f"01%: {percentile(wind, 1)}\n05%: {percentile(wind, 5)}\n10%: {percentile(wind, 10)}\n25%: {percentile(wind, 25)}\n33%: {percentile(wind, 33)}\n50%: {percentile(wind, 50)}\n66%: {percentile(wind, 66)}\n75%: {percentile(wind, 75)}\n90%: {percentile(wind, 90)}\n95%: {percentile(wind, 95)}\n99%: {percentile(wind, 99)}\n")
print(f"Mean: {np.nanmean(wind)}\nMedian: {np.nanmedian(wind)}\nMax: {np.nanmax(wind)}\nMin: {np.nanmin(wind)}\nRange: {np.nanmax(wind) - np.nanmin(wind)}")

plt.show()

