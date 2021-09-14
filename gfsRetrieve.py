import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import xarray as xr 
from datetime import datetime 
import cartopy.feature as cfeature

# Generate a URL that you will use to retrieve the data
def url():
    startTime=datetime.now()

    year = startTime.year

    if startTime.month <10:
        month = '0'+str(startTime.month)
    else:
        month = str(startTime.month)

    if startTime.day <10:
        day = '0'+str(startTime.day)
    else:
        day = str(startTime.day)

    if startTime.hour <10:
        hour = '0'+str(startTime.hour)
    else:
        hour = str(startTime.hour)

    mdate = str(year)+str(month)+str(day)

    def get_init_hr(hour):
        if int(hour) <6:
            init_hour = '00'
        elif int(hour) <12:
            init_hour = '06'
        elif int(hour) <17:
            init_hour = '12'
        elif int(hour) <22:
            init_hour = '18'
        else:
            init_hour = '00'
        return(init_hour)

    init_hour = get_init_hr(hour)
    url = 'http://nomads.ncep.noaa.gov:80/dods/gfs_0p25_1hr/gfs'+mdate+'/gfs_0p25_1hr_'+init_hour+'z'
    return init_hour, mdate, url

# Retrieve data for the requested parameters
# Variable "request" should be a list
def data(request, hour):
    init_hour, mdate, link = url()
    print("GFS Initialization: ", init_hour, mdate)
    dataset = xr.open_dataset(link).isel(time = hour)
    data = []
    for x in range(len(request)):
        data.append((dataset[request[x]]).squeeze())
    dataset.close()
    return data

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

# Function to plot windbarbs 
def windbarbs(lons, lats, uwnd, vwnd, lvl):
    uwnd = uwnd.sel(lev = lvl)
    vwnd = vwnd.sel(lev = lvl)
    plt.barbs(lons, lats, uwnd.values * 1.9438, vwnd.values * 1.94384, zorder = 10)

# Function to plot filled contours
def contourf(data, lvl, ranges, color):
    try:
        data = data.sel(lev = lvl)
    except:
        data = data
    plt.contourf(data.lon, data.lat, data.values, levels = ranges, cmap = color)    
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)

# Function to plot contours
def contour(data, lvl, value, color, linewidth):
    data = data.sel(lev = lvl)
    plt.contour(data.lon, data.lat, data.values, origin = 'upper', levels = value, colors = color, linewidths = linewidth)
