import xarray as xr
import numpy as np
from scipy.signal import detrend
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cmaps as cmap 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import patheffects
np.set_printoptions(suppress=True)

# Create a map using Cartopy
def map(ax, interval, labelsize):
    # Add the map and set the extent
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, top = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def detrend_data(data):
    """
    Detrends variable data to remove the skewing that global warming causes
    :param data: the variable DataArray to be detrended
    :return: the detrended variable DataArray
    """
    data = data.fillna(0)
    reshaped = data.stack(combined=('lat', 'lon'))
    detrended = detrend(reshaped, axis=0)

    newData = detrended.reshape(data.shape)
    newData = xr.DataArray(
        data=newData,
        dims=('time', 'latitude', 'longitude'),
        coords=dict(
            time=(["time"], data.time.values),
            latitude=(["latitude"], data.lat.values),
            longitude=(["longitude"], data.lon.values)
        ))
    return newData

def get_zscores(data, months):
    all_zscores = []
    for x in range(len(months)):
        tempData = data.sel(time = months[x])
        mean = tempData.mean(['time'])
        stdd = tempData.std(['time'])

        for y in range(len(tempData)):
            all_zscores.append((tempData[y] - mean) / stdd)

    all_zscores = xr.DataArray(
        data=all_zscores,
        dims=('time', 'latitude', 'longitude'),
        coords=dict(
            time=(["time"], data.time.values),
            latitude=(["latitude"], data.latitude.values),
            longitude=(["longitude"], data.longitude.values)
        ))
    return all_zscores

labelsize = 9
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
title = 'Full Year'
startYear = 1854
endYear = 2023
numOfEOFS = 10 
extent = [0, 70, 275, 360]

for x in range(len(months)):
    months[x] = [np.datetime64(f'{y}-{str(months[x]).zfill(2)}-01') for y in range(startYear, endYear + 1)]
fMonths = np.array(months).flatten()

# open variable data
dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
data = dataset['sst'].sel(time = fMonths, lat=slice(extent[1], extent[0]), lon=slice(extent[2], extent[3]))
detrendedData = detrend_data(data)
print('Data detrended')
zscoreData = get_zscores(detrendedData, months)
print('Z-scores calculated')
zscores = np.nan_to_num(zscoreData.to_numpy())
print(f"Initial shape: {zscores.shape}")

# Flatten the 3D array to a 2D matrix (time, space)
time_steps, lat_size, lon_size = zscores.shape
sst_reshaped = zscores.reshape(time_steps, lat_size * lon_size)
print(f"Flattened shape: {sst_reshaped.shape}")

# Perform PCA to get the most prevalent patterns (EOFs)
pca = PCA(n_components = numOfEOFS)
PCs = pca.fit_transform(sst_reshaped)
print(f"PC matrix shape: {PCs.shape}")

# Reshape the PCA results (EOFs) back to 3D (x, latitude, longitude)
EOFs = np.zeros((numOfEOFS, lat_size, lon_size))
for i in range(numOfEOFS):
    EOFs[i, :, :] = pca.inverse_transform(np.eye(numOfEOFS)[i]).reshape(lat_size, lon_size)
print(f"EOF matrix shape: {EOFs.shape}")

explained_variance = pca.explained_variance_ratio_
print(f"Explained variance: {explained_variance}")

# Creates the plot
fig = plt.figure(figsize=(10.5, 9))
gs = fig.add_gridspec(2, 2, wspace = 0, hspace = 0)
axes = [fig.add_subplot(1, 1, 1),
        fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree(central_longitude=180)),
        fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree(central_longitude=180)),
        fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree(central_longitude=180)),
        fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree(central_longitude=180))]

axes[0].set_xticks([])
axes[0].set_yticks([])

for x in range(len(axes[1:])):
    axes[x + 1] = map(axes[x + 1], 15, 9)
    c = axes[x + 1].contourf(zscoreData.longitude, zscoreData.latitude, EOFs[x], np.arange(-0.1, 0.101, 0.001), extend='both', transform=ccrs.PlateCarree(), cmap=cmap.tempAnoms())
    axes[x + 1].text((extent[2] + 5) - 360, extent[1] - 5, f'Variance Explained: {round(float(explained_variance[x]) * 100, 1)}%', color = 'red', fontsize = 9, fontweight = 'bold', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))

axes[0].set_title(f'ERSSTv5 EOF Analysis (Data Detrended and Normalized)\nFirst 4 Modes Displayed' , fontweight='bold', fontsize=labelsize, loc='left')
axes[0].set_title(f'{title}', fontsize = labelsize, loc = 'center')
axes[0].set_title(f'{startYear}-{endYear}\nDeelan Jariwala', fontsize=labelsize, loc='right')  
cax = inset_axes(axes[0], width="1%", height="100%", loc='upper left', bbox_to_anchor=(1.01, 0, 1, 1), bbox_transform=axes[0].transAxes, borderpad = .02)
cbar = fig.colorbar(c, cax=cax, orientation="vertical")    
cbar.set_ticks(np.arange(-0.1, 0.12, 0.02))
plt.savefig(r"C:\Users\deela\Downloads\EOFPanelPlot.png", dpi = 400, bbox_inches = 'tight')
plt.show()