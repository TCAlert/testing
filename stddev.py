import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy as np
import xarray as xr 
from datetime import datetime 
import cartopy.feature as cfeature
import cmaps as cmap
import bdeck as bdeck 
import cartopy.mpl.ticker as cticker

# Move GEFS functions to own file? 
# Suggest merger of GEFS and GFS code, make single clear function
# bounds() seems redundant, consider merging with basins()

def url(flag):
    #grabbing data from NOMADS

    t = datetime.now()

    year = str(t.year)
    month = str(t.month).zfill(2)
    if flag == False:
        day = str(t.day - 1).zfill(2)
    else:
        day = str(t.day).zfill(2)
    hour = str(t.hour).zfill(2)

    mdate = year + month + day

    def get_init_hr(hour):
        if hour <= 8:
            init_hour = '00'
        elif hour <= 14:
            init_hour = '06'
        elif hour <= 20:
            init_hour = '12'
        else:
            init_hour = '18'
        return init_hour

    init_hour = get_init_hr(int(hour))
    url = f'http://nomads.ncep.noaa.gov:80/dods/gefs/gefs{mdate}/gefs_pgrb2ap5_all_{init_hour}z'
    print(url)
    return init_hour, mdate, url

def data(request, hour):
    try:
        init_hour, mdate, link = url(True)
        dataset = xr.open_dataset(link).isel(time = hour)
    except:
        init_hour, mdate, link = url(False)
        dataset = xr.open_dataset(link).isel(time = hour)

    print("GEFS Initialization: ", init_hour, mdate)

    data = []
    for x in range(len(request)):
        data.append((dataset[request[x]]).squeeze())
    dataset.close()
    return data, init_hour, mdate

def bounds(basin):
    if basin.lower() == 'natl':
        bounds = [260, 359, 0, 60]
    elif basin.lower() == 'epac':
        bounds = [181, 280, 0, 60]
    elif basin.lower() == 'wpac':
        bounds = [79, 179, 0, 60]
    elif basin.lower() == 'watl':
        bounds = [260, 320, 0, 40]
    elif basin.lower() == 'us':
        bounds = [220, 310, 10, 60]
    elif (int(basin[2:]) > 0) == True:
        lat, lon = bdeck.latlon(basin.lower())
        bounds = [lon - 27.5, lon + 27.5, lat - 15, lat + 15]
    return bounds

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
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


def mean(dataset):
    data = []
    for x in range(1, 32):
        temp = dataset.sel(ens = x)
        data.append(temp.values)
    dataset = dataset.mean('ens')
    dataset.values = sum(data) / len(data)
    return dataset

def std(dataset, average):
    dev = []
    for x in range(1, 32):
        temp = dataset.sel(ens = x)
        dev.append((average.values - temp.values)**2)
    dataset = dataset.mean('ens')
    dataset.values = np.sqrt(sum(dev) / len(dev))
    stddev = dataset
    return stddev

def run(basin):
    requests = ['hgtprs']
    hour = 28
    bound = bounds(basin)
    height = 500

    dat, init_hour, mdate = data(requests, hour)

    for x in range(len(dat)):
        dat[x] = dat[x].sel(lon = slice(bound[0], bound[1]), lat = slice(bound[2], bound[3]), lev = height) 
    
    dat[0] = dat[0] / 10
    q1 = np.percentile(dat[0], 25, axis = 0)
    q3 = np.percentile(dat[0], 75, axis = 0)
    avg = mean(dat[0])
    dev = std(dat[0], avg)
    qcod = (q3 - q1)**2 / (q3 + q1)
    print(qcod)

    ax = map(4, 8)
    ax.set_extent(bound, crs = ccrs.PlateCarree())

    plt.contourf(dev.lon, dev.lat, qcod, levels = np.arange(0, 1, 0.001), cmap = cmap.probs(), extend = 'both')#, transform = ccrs.PlateCarree(central_longitude = 0))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    c = plt.contour(avg.lon, avg.lat, avg.values, levels = np.arange(500, 600, 4), linewidths = 1, colors = '#1a1a1a')
    plt.clabel(c, fontsize = 10, inline = 1, fmt = '%1.0f')

    mdate = f'{mdate[:4]}-{mdate[4:6]}-{mdate[6:8]}'
    time = (str(dev.time.values)).split('T')
    time = f'{time[0]} at {(time[1][:5])}z'

    plt.title(f'0.5\u00b0 GEFS Mean 500mb Height Contours (dam) and IQR * QCOD \nInitialization: {mdate} at {init_hour}:00z', fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Forecast Hour: {str(hour * 6)} ({time})', fontsize = 10, loc = 'center')
    plt.title('Deelan Jariwala\nData from NOMADS', fontsize=10, loc='right') 
    plt.savefig(r"C:\Users\deela\Downloads\stddevplot.png", dpi = 150, bbox_inches = 'tight')
    #print("Saving complete")
    plt.show()
    plt.close() 
run('natl')
