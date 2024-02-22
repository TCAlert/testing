import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import matplotlib.patheffects as pe
from matplotlib import rcParams
rcParams['font.family'] = 'Courier New'

def computeClimo(data, month, year):
    if year - 30 < 1854:
        allYears = range(1854, 1883)
    else:
        allYears = range(year - 30, year - 1)
    allYears = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in allYears]
    data = data.sel(time = allYears)

    return data

def std(dataset, average):
    dev = []
    for x in range(29):
        temp = dataset.isel(time = x)
        dev.append((average.values - temp.values)**2)
    dataset = dataset.mean('time')
    dataset.values = np.sqrt(sum(dev) / len(dev))
    stddev = dataset
    return stddev

def timeseries(month, years, sd = False):
    dataset = ((xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']).sel(lat = slice(5, -5), lon = slice(190, 240))).mean(['lat', 'lon'])
    print(dataset)
    allData = []
    anomalies = []
    climos = []
    sst = []
    for year in years:
        climo = computeClimo(dataset, month, int(year))
        anomalies.append((dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])).values)
        climos.append((climo.mean(['time'])).values)
        sst.append(dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')).values)
        print(year, f"{(dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])).values}", dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')).values)
    e
    fig = plt.figure(figsize=(16, 8))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)

    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Temperature (\u00b0C)', weight = 'bold', size = 9)
    ax.set_xlabel('Year', weight = 'bold', size = 9)

    ax.plot(years[29:], climos[29:], linewidth = 2.5, color = '#404040', label = '30-Year Sliding Climatology')
    ax.plot(years[:], sst[:], linewidth = 2, color = '#bf3030', label = 'Sea Surface Temperature')
    ax.scatter(years[-1], sst[-1], color = 'black', zorder = 10)
    ax.text(years[-1] + 5, sst[-1], f'{round(float(sst[-1]), 1)}C', size=10, color='#404040', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])

    plt.legend()

    plt.title(f'ERSSTv5 Sea Surface Temperatures\n-5S to 5N, 170 to 120W' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{helper.numToMonth(month)}', fontsize = 10, loc = 'center')
    plt.title('Deelan Jariwala', fontsize=10, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\ersstlineplot.png", dpi = 400, bbox_inches = 'tight')

    plt.show()

timeseries(month='2', years=range(1854, 2024))