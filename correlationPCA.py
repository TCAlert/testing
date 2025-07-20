import xarray as xr
import numpy as np
from scipy.signal import detrend
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cmaps as cmap 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import pandas as pd
from helper import numToMonth
np.set_printoptions(suppress=True)

ALLMONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
for x in range(len(ALLMONTHS)):
    ALLMONTHS[x] = [np.datetime64(f'{y}-{str(ALLMONTHS[x]).zfill(2)}-01') for y in range(1854, 2023 + 1)]

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

def pcaSeries(startYear, endYear, lats, lons, mon, eofNum = 1, months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
    extent = [lats[0], lats[1], lons[0], lons[1]]
    for x in range(len(months)):
        months[x] = [np.datetime64(f'{y}-{str(months[x]).zfill(2)}-01') for y in range(startYear, endYear + 1)]
    fMonths = np.array(months).flatten()

    # open variable data
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
    if extent[3] > 360:
        extent[2] = extent[2] - 360
        extent[3] = extent[3] - 360
        dataset = dataset.assign_coords(lon=(((dataset.lon + 180) % 360) - 180)).sortby('lon')

    data = dataset['sst'] * np.cos(np.radians(dataset['lat']))
    data = data.sel(lat=slice(extent[1], extent[0]), lon=slice(extent[2], extent[3])) 
    # print(data)
    detrendedData = detrend_data(data)
    detrended = detrendedData.sel(time = fMonths)
    zscoreData = get_zscores(detrended, months)
    zscores = np.nan_to_num(zscoreData.to_numpy())
    print(f"Initial shape: {zscores.shape}")

    # Flatten the 3D array to a 2D matrix (time, space)
    time_steps, lat_size, lon_size = zscores.shape
    sst_reshaped = zscores.reshape(time_steps, lat_size * lon_size)
    print(f"Flattened shape: {sst_reshaped.shape}")

    # Perform PCA to get the most prevalent patterns (EOFs)
    pca = PCA(n_components = eofNum)
    PCs = pca.fit_transform(sst_reshaped)
    print(f"PC matrix shape: {PCs.shape}")

    # Reshape the PCA results (EOFs) back to 3D (x, latitude, longitude)
    EOFs = np.zeros((eofNum, lat_size, lon_size))
    for i in range(eofNum):
        EOFs[i, :, :] = pca.inverse_transform(np.eye(eofNum)[i]).reshape(lat_size, lon_size)
        EOFs[i, :, :] = EOFs[i, :, :] / np.linalg.norm(EOFs[i, :, :], axis=1)[:, np.newaxis]
    print(f"EOF matrix shape: {EOFs.shape}")

    explained_variance = pca.explained_variance_ratio_
    print(f"Explained variance: {explained_variance}")

    i = eofNum - 1
    test = PCs#[:, i]

    m, s = np.mean(test, axis = 0, keepdims=True), np.std(test, axis = 0, keepdims=True)
    data = (test - m) / s

    column_labels = list(range(1, data.shape[1] + 1))
    data = pd.DataFrame(data, columns=column_labels)

    data.insert(0, 'Year', np.arange(startYear, endYear + 1))
    
    return data

# pcaSeries(1951, 2025, [0, 70], [270, 359], '6', 2, months = [6])