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
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
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
months = [7, 8, 9]
startYear = 2000
endYear = 2020
numOfEOFS = 10 
extent = [20, 60, 120, 240]

for x in range(len(months)):
    months[x] = [np.datetime64(f'{y}-{str(months[x]).zfill(2)}-01') for y in range(startYear, endYear + 1)]
fMonths = np.array(months).flatten()

# open variable data
dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
data = dataset['sst'].sel(time = fMonths, lat=slice(extent[1], extent[0]), lon=slice(extent[2], extent[3]))
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

    ax = map(7.5, 9)
    plt.contourf(zscoreData.longitude, zscoreData.latitude, EOF, np.arange(-0.05, 0.05, 0.001), extend='both', transform=ccrs.PlateCarree(), cmap=cmap.tempAnoms())

    plt.title(f'ERSSTv5 EOF{i + 1} (Detrended and Normalized)\nExplained variance: {round(float(explained_variance[i]), 3)}' , fontweight='bold', fontsize=labelsize, loc='left')
    plt.title(f'JAS', fontsize = labelsize, loc = 'center')
    plt.title(f'{startYear}-{endYear}\nDeelan Jariwala', fontsize=labelsize, loc='right')  
    cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    cbar.set_ticks(np.arange(-0.05, 0.06, 0.01))
    plt.savefig(r"C:\Users\deela\Downloads\ersstEOF" + str(startYear) + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show()