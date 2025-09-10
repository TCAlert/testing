import xarray as xr
import numpy as np 
import pandas as pd 
import helper 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
from sklearn import linear_model
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import cmaps as cmaps 

def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]

    return ret[n - 1:] / n

bins = np.arange(20, 32, 0.05)
counts = np.arange(0, 751, 1)

def coverage(data):
    flattenedArray = data.values.reshape(-1)
    lat, lon = np.meshgrid(data.lon.values, data.lat.values, indexing = 'ij')
    # plt.imshow(lat)
    # plt.show()
    histogram, _ = np.histogram(flattenedArray, bins = bins, density = True, weights = np.abs(np.cos(lat.reshape(-1))))
    histogram = moving_average(histogram, n = 20)

    return flattenedArray, histogram

def timeseries(month, years):
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']

    values = []
    histograms = []
    for year in years:
        value, h = coverage(dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')))
        values.append(value)
        histograms.append(h)
    values = np.array(values)
    histograms = np.array(histograms)

    # data = pd.DataFrame({'Year' : years, helper.numToMonth(month)[0:3] : values})
    fig = plt.figure(figsize=(16, 8))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)

    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Percent of Pixels', weight = 'bold', size = 9)
    ax.set_xlabel('Degrees Celsius', weight = 'bold', size = 9)

    # Normalize years to range 0–1 for color mapping
    norm = mcolors.Normalize(vmin=min(years), vmax=max(years))
    cmap = cmaps.tempAnoms4() # You can change colormap here

    for x in range(len(values)):
        color = cmap(norm(years[x]))
        # plt.hist(values[x], bins = bins, color = color, alpha = 0.5)
        plt.plot(bins[:-20], histograms[x], color = color)

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Year', aspect = 50, pad = .02)

    plt.title(f'ERSSTv5 Sea Surface Temperatures\nHistogram Trend' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{helper.numToMonth(month)}', fontsize = 10, loc = 'center')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\ersstHistogram.png", dpi = 400, bbox_inches = 'tight')

    plt.show()
    
# timeseries('9', [1924, 2024])
timeseries('9', np.arange(1924, 2024))