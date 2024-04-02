import xarray as xr
import numpy as np
from scipy.signal import detrend
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

np.set_printoptions(suppress=True)
forecast_months = [7, 8, 9]


def detrend_data(data):
    """
    Detrends variable data to remove the skewing that gobal warming causes
    :param data: the variable DataArray to be detrended
    :return: the detrended variable DataArray
    """
    data = data.fillna(0)
    reshaped_data = data.stack(combined=('lat', 'lon'))
    detrended_data = detrend(reshaped_data, axis=0)

    detrended_map_data = detrended_data.reshape(data.shape)
    detrended_map_data = xr.DataArray(
        data=detrended_map_data,
        dims=('time', 'latitude', 'longitude'),
        coords=dict(
            time=(["time"], data.time.values),
            latitude=(["latitude"], data.lat.values),
            longitude=(["longitude"], data.lon.values)
        ))
    return detrended_map_data


def get_zscores(data, months):
    filtered_data = []
    for month in months:
        month = format(month, '02d')
        month_data = []
        for year in range(1854, 2023):
            date = np.datetime64(f'{year}-{month}', 'D')
            month_data.append(data.sel(time=date))
        filtered_data.append(month_data)
    filtered_data = dict(zip(forecast_months, filtered_data))

    all_zscores = []
    for month in forecast_months:
        month_data = filtered_data[month]
        all_means = np.mean(np.array(month_data), axis=0)
        all_stds = np.std(np.array(month_data), axis=0)

        for year in month_data:
            calc_year_data = data.sel(time=year.time.values)
            zscore_map = (calc_year_data - all_means) / all_stds
            all_zscores.append(zscore_map)
    all_zscores = np.array(all_zscores)

    all_zscores = xr.DataArray(
        data=all_zscores,
        dims=('time', 'latitude', 'longitude'),
        coords=dict(
            time=(["time"], data.time.values),
            latitude=(["latitude"], data.latitude.values),
            longitude=(["longitude"], data.longitude.values)
        ))
    return all_zscores


# open variable data
varDataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')
varData = varDataset['sst']
detrendedData = detrend_data(varData).isel(time=slice(-8))

# get anomaly data for given variable
months = []
for idx in range(len(detrendedData.time)):
    if idx % 12 + 1 in forecast_months:
        months.append(idx)
monthData = detrendedData.isel(time=months)
zscoreData = get_zscores(monthData, forecast_months)
zscoreData = zscoreData#.sel(latitude=slice(70, 0), longitude=slice(275, 360))
zscores = np.nan_to_num(zscoreData.to_numpy())
print(f"Initial shape: {zscores.shape}")

# Flatten the 3D array to a 2D matrix (time, space)
time_steps, lat_size, lon_size = zscores.shape
sst_reshaped = zscores.reshape(time_steps, lat_size * lon_size)
print(f"Flattened shape: {sst_reshaped.shape}")

# Perform PCA to get the most prevalent patterns (EOFs)
n_components = 10  # You can adjust this value based on your requirement
pca = PCA(n_components=n_components)
PCs = pca.fit_transform(sst_reshaped)
print(f"PC matrix shape: {PCs.shape}")

# Reshape the PCA results (EOFs) back to 3D (x, latitude, longitude)
EOFs = np.zeros((n_components, lat_size, lon_size))
for i in range(n_components):
    EOFs[i, :, :] = pca.inverse_transform(np.eye(n_components)[i]).reshape(lat_size, lon_size)
print(f"EOF matrix shape: {EOFs.shape}")

explained_variance = pca.explained_variance_ratio_
print(f"Explained variance: {explained_variance}")


for i in range(n_components):
    EOF = EOFs[i]

    print(PCs.T[i].shape)
    reshaped_array = PCs.T[i].reshape(len(forecast_months), -1)
    print(reshaped_array.shape)
    sums = []
    for j in range(len(reshaped_array[0])):
        sums.append(reshaped_array[0][j] + reshaped_array[1][j])
    print([len(list(range(1854, 2023))), len(sums)])
    contributions = np.array([list(range(1854, 2023)), sums]).T
    contributions = contributions[contributions[:, 1].argsort()]
    print(contributions)

    # plot cartopy map and various features
    plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.add_feature(cf.LAND)
    ax.add_feature(cf.STATES, linewidth=0.2, edgecolor="gray")
    ax.add_feature(cf.BORDERS, linewidth=0.3)
    ax.coastlines(linewidth=0.5, resolution='50m')

    # plot gridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude=0), draw_labels=True, linewidth=1, color='gray', alpha=0.5,
                      linestyle='--')
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = {'size': 7, 'weight': 'bold', 'color': 'gray'}
    gl.ylabel_style = {'size': 7, 'weight': 'bold', 'color': 'gray'}

    newcmp = LinearSegmentedColormap.from_list("", [
        (0 / 20, "#FF8C89"),
        (5 / 20, "#E12309"),
        (7.5 / 20, "#FEC024"),
        (10 / 20, "#FFFFFF"),
        (12.5 / 20, "#228DFF"),
        (15 / 20, "#104CE1"),
        (20 / 20, "#AF75FE")])
    newcmp = newcmp.reversed()

    # add data and colormap
    plt.contourf(zscoreData.longitude, zscoreData.latitude, EOF, np.arange(-0.05, 0.05, 0.001), extend='both',
                 transform=ccrs.PlateCarree(), cmap=newcmp)
    cbar = plt.colorbar(pad=0.015, aspect=25, shrink=1)
    cbar.set_ticks(np.arange(-0.05, 0.06, 0.01))
    cbar.ax.tick_params(labelsize=8)

    # add titling
    mainTitle = f"EOF{i + 1} With Detrended and Normalized SST Data for JAS"
    subTitle = f"\nExplained variance: {round(float(explained_variance[i]), 3)}"
    subTitle2 = "\nERSSTv5 Data (1854-2023)"
    plt.title(mainTitle + subTitle + subTitle2, fontsize=10, weight='bold', loc='left')
    plt.title("DCAreaWx", fontsize=10, weight='bold', loc='right', color='gray')

    # save and display map
    #plt.savefig(r"C:/Nikhil Stuff/Coding Stuff/EofMap.png", dpi=300, bbox_inches='tight')
    plt.show()