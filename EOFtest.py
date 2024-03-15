import xarray as xr
import numpy as np
from scipy.signal import detrend
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cmaps as cmap 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
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
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def detrend_data(data):
    """
    Detrends variable data to remove the skewing that global warming causes
    :param data: the variable DataArray to be detrended
    :return: the detrended variable DataArray
    """
    data = data.fillna(0)
    reshaped = data.stack(combined=('longitude', 'latitude'))
    detrended = detrend(reshaped, axis=0)

    newData = detrended.reshape(data.shape)
    newData = xr.DataArray(
        data=newData,
        dims=('time', 'longitude', 'latitude'),
        coords=dict(
            time=(["time"], data.time.values),
            longitude=(["longitude"], data.longitude.values),
            latitude=(["latitude"], data.latitude.values)
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
        dims=('time', 'longitude', 'latitude'),
        coords=dict(
            time=(["time"], data.time.values),
            latitude=(["latitude"], data.latitude.values),
            longitude=(["longitude"], data.longitude.values)
        ))
    return all_zscores

labelsize = 9
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
startYear = 1923
endYear = 2023
numOfEOFS = 4 
#extent = [20, 60, 120, 240]

for x in range(len(months)):
    months[x] = [np.datetime64(f'{y}-{str(months[x]).zfill(2)}-01') for y in range(startYear, endYear + 1)]
fMonths = np.array(months).flatten()

# open variable data
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\trackDensity.nc")
data = dataset['trackDensity'].sel(time = fMonths)#, lat=slice(extent[1], extent[0]), lon=slice(extent[2], extent[3]))
detrendedData = detrend_data(data)
zscoreData = get_zscores(detrendedData, months)
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

for i in range(numOfEOFS):
    EOF = EOFs[i]
    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(4, 1, wspace = 0, hspace = 0)
    axes = [fig.add_subplot(gs[3, 0]),
            fig.add_subplot(gs[0:3, 0], projection = ccrs.PlateCarree(central_longitude=180))]

    # Add the map and set the extent
    axes[0].set_frame_on(False)

    # Add state boundaries to plot
    axes[0].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[0].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[0].set_ylabel(f'PC{i + 1} Index', weight = 'bold', size = 9)
    axes[0].set_xlabel('Time', weight = 'bold', size = 9)
    axes[0].axhline(color = 'black')

    axes[0].plot(np.sort(fMonths), PCs[:, i], linewidth = 2.5, color = '#404040', label = f'PC{i + 1} Timeseries')
    axes[0].legend()

    axes[1] = map(axes[1], 10, 9) 
    c = axes[1].contourf(zscoreData.latitude, zscoreData.longitude, EOF, np.arange(-0.05, 0.05, 0.001), extend='both', transform=ccrs.PlateCarree(), cmap=cmap.tempAnoms())

    plt.title(f'HURDAT2 Atlantic Track Density EOF{i + 1} (Detrended and Normalized)\nExplained variance: {round(float(explained_variance[i]) * 100, 1)}%' , fontweight='bold', fontsize=labelsize, loc='left')
    plt.title(f'Full Year {startYear}-{endYear}', fontsize = labelsize, loc = 'center')
    plt.title(f'Deelan Jariwala\nCredit to Nikhil Trivedi', fontsize=labelsize, loc='right')  
    cbar = plt.colorbar(c, orientation = 'horizontal', aspect = 100, pad = .08)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    cbar.set_ticks(np.arange(-0.05, 0.06, 0.01))
    plt.savefig(r"C:\Users\deela\Downloads\trackEOF" + str(i + 1) + ".png", dpi = 400, bbox_inches = 'tight')
plt.show()