import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import pandas as pd 

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

def anomalies(month, years, sd = False):
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']
    allData = []
    for year in years:
        climo = computeClimo(dataset, month, int(year))

        data = dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])
        if sd == True:
            sdata = std(climo, climo.mean(['time']))
            allData.append((data / sdata).values)
            title = 'Standardized Anomalies'
        else:
            globalMean = data.mean()
            allData.append((data - globalMean).values)
            title = 'Global Mean Anomalies'    
    allData = sum(allData) / len(allData)

    labelsize = 8 
    ax = map(20, labelsize)    

    plt.contourf(data.lon, data.lat, allData, origin='lower', levels = np.arange(-5, 5, .1), cmap = cmap.tempAnoms(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    plt.title(f'ERSSTv5 {title}\n30-Year Sliding Climatology' , fontweight='bold', fontsize=labelsize, loc='left')
    plt.title(f'{helper.numToMonth(month)} {str(years)}', fontsize = labelsize, loc = 'center')
    plt.title('Deelan Jariwala', fontsize=labelsize, loc='right')  
    cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\ersstComposite.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

ens = pd.read_csv(r"C:\Users\deela\Downloads\ensoni - Sheet 1.csv")
aso, ndj, y = ens['ASO'], ens['NDJ'], ens['Year']
ninos = []
ninas = []
warmn = []
cooln = []
for x in range(len(aso)):
    if aso[x] > 0.5 and ndj[x] > 0.5:
        ninos.append(y[x])
    elif aso[x] < -0.5 and ndj[x] < -0.5:
        ninas.append(y[x])
    elif (aso[x] > 0 and aso[x] < 0.5) and (ndj[x] > 0 and ndj[x] < 0.5):
        warmn.append(y[x])
    elif (aso[x] < 0 and aso[x] > -0.5) and (ndj[x] < 0 and ndj[x] > -0.5):
        cooln.append(y[x])
print('El Nino', ninos, '\nWarm Neutral', warmn, '\nCool Neutral', cooln, '\nLa Nina', ninas)

anomalies('9', ninas)#[2010, 1999, 2020, 1995, 1955, 2017, 2022, 2021, 1988, 1942, 1889, 1856, 1998])