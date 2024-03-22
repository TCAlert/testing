import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
from datetime import datetime, timedelta
import cartopy.feature as cfeature
import numpy as np 

# Generate a URL that you will use to retrieve the data
def url(flag):
    t = datetime.utcnow()
    hour = str(t.hour)

    def get_init_hr(hour):
        print(hour)
        if hour < 7:
            init_hour = '00'
        elif hour < 13:
            init_hour = '06'
        elif hour < 19:
            init_hour = '12'
        elif hour < 24:
            init_hour = '18'
        else:
            init_hour = '00'
        return(init_hour.zfill(2))

    init_hour = get_init_hr(int(hour))

    if not flag:
        t = t - timedelta(hours = 6)
        init_hour = get_init_hr(t.hour)

    mdate = f'{str(t.year).zfill(2)}{str(t.month).zfill(2)}{str(t.day).zfill(2)}'
    url1 = f'http://nomads.ncep.noaa.gov:80/dods/gefs/gefs{mdate}/gefs_pgrb2ap5_all_{init_hour}z'
    url2 = f'http://nomads.ncep.noaa.gov:80/dods/gefs/gefs{mdate}/gefs_pgrb2bp5_all_{init_hour}z'
    return init_hour, mdate, url1, url2

# Retrieve data for the requested parameters, as well as pertinent information regarding the run
# Variable "request" should be a list
def getData(request, hour):
    try:
        init_hour, mdate, link1, link2 = url(True)
        dataset1, dataset2 = xr.open_dataset(link1).sel(time = hour), xr.open_dataset(link2).sel(time = hour)
    except:
        init_hour, mdate, link1, link2 = url(False)
        dataset1, dataset2 = xr.open_dataset(link1).sel(time = hour), xr.open_dataset(link2).sel(time = hour)
    dataset1, dataset2 = dataset1[request], dataset2[request]
    dataset = xr.merge([dataset1, dataset2])
    print(dataset)

    init = f'{mdate[0:4]}-{mdate[4:6]}-{mdate[6:8]} at {init_hour}:00z'
    print("GEFS Initialization: ", init)

    data = []
    for x in range(len(request)):
        data.append(dataset[request[x]].squeeze())
    dataset.close()
    return data, init

# Create a map using Cartopy
def map(n, s, e, w):
    fig = plt.figure(figsize=(20, 10))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_extent([e, w, s, n])

    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 1)
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude=180), zorder = 9, draw_labels = True, linewidth = 0.5, color='white', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False 
    return n, s, e, w

#getData(['ugrdprs', 'vgrdprs'], np.datetime64('2024-03-12T12'))