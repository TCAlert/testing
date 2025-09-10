import xarray as xr
import numpy as np 
import pandas as pd 
import helper 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
from sklearn import linear_model

def coverage(data, isotherm = 26.):
    flattenedArray = data.values.reshape(-1)
    maskedArray = np.where(flattenedArray < isotherm, np.nan, flattenedArray)

    threshold = np.count_nonzero(~np.isnan(maskedArray))

    return (threshold / np.count_nonzero(~np.isnan(flattenedArray))) * 100

def timeseries(month, years, threshold = 26):
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']

    values = []
    for year in years:
        value = coverage(dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')), isotherm = threshold)
        values.append(value)
    values = np.array(values)

    # data = pd.DataFrame({'Year' : years, helper.numToMonth(month)[0:3] : values})
    fig = plt.figure(figsize=(16, 8))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)

    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Percent (%)', weight = 'bold', size = 9)
    ax.set_xlabel('Year', weight = 'bold', size = 9)

    # ax.plot(years[:], climos[:], linewidth = 2.5, color = '#404040', label = '30-Year Sliding Climatology')
    ax.plot(years[:], values[:], linewidth = 2, color = '#bf3030', label = f'% of World >{threshold}C')
    # ax.scatter(years[-1], values[-1], color = 'black', zorder = 10)
    # ax.text(years[-1] + 5, sst[-1], f'{round(float(sst[-1]), 1)}C', size=10, color='#404040', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])

    regr = linear_model.LinearRegression()
    regr.fit(years.reshape(-1, 1), values.reshape(-1, 1))
    coef, intr = regr.coef_[0][0], regr.intercept_[0]
    print(regr.coef_)

    print(np.nanmin(years), np.nanmax(years))
    bogusX = np.linspace(np.nanmin(years), np.nanmax(years))

    ax.plot(bogusX, (coef * bogusX) + intr, linewidth = 2, color = 'black')

    plt.legend()

    plt.title(f'ERSSTv5 Sea Surface Temperatures\n>{threshold}C Coverage (%)' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{helper.numToMonth(month)}', fontsize = 10, loc = 'center')
    plt.title(f'Slope: {round(coef, 2)}\nDeelan Jariwala', fontsize=10, loc='right')  
    # plt.savefig(r"C:\Users\deela\Downloads\ersstThreshold" + str(threshold) + ".png", dpi = 400, bbox_inches = 'tight')

    plt.show()
    
timeseries('9', np.arange(1995, 2025), 20)