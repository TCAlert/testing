import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cmaps as cmap 
import cdsapi as cds 
import hurdatParser
import matplotlib.patheffects as pe
import metpy.interpolate as interp

USAGE = '```$era5wind [date] [hour] [level] [name (if in HURDAT2) | coordinate]```'
labelsize = 8 
c = cds.Client()

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('lon') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

def retrieve(type, level, date, lat, lon): 
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type'  : 'reanalysis',
            'variable'      : type,
            'pressure_level': level,
            'year'          : f'{date[0]}',
            'month'         : f'{date[1]}',
            'day'           : f'{date[2]}',
            'time'          : f'{date[3]}:00',
            'format'        : 'netcdf',                 # Supported format: grib and netcdf. Default: grib
            'area'          : [lat + 15, lon - 20, lat - 15, lon + 20], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

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

# Function to put together the whole plot
def momentumPlot(month, day, year, hour, level, name):
    print('test')
    if type(name) == str:
        # Retrieve storm data from HURDAT2
        database = hurdatParser.database()
        stormData = hurdatParser.retrieveStorm(database, [name, str(year)])['Storm Data']
        print(stormData)
        stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
        lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    else:
        lat, lon = name
    
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, lat, lon)

    # Requests GFS zonal and meridional wind data 
    #retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
    uData = (data['u']).squeeze()
    vData = (data['v']).squeeze()
    lons = uData.longitude
    lats = uData.latitude
    lons, lats = np.meshgrid(lons, lats)

    #First, we have to create lists
    ydist, xdist, tcdist, rlonfac, theta_ang = [np.zeros([lats.shape[0], lats.shape[1]]) for _ in range(5)]
    u_radial, v_azimuth, momentum, L            = [np.zeros([lats.shape[0], lats.shape[1], len(level)]) for _ in range(4)]
    
    lat_diffs = np.abs(lats - lat)
    min_index = np.unravel_index(np.argmin(lat_diffs, axis=None), lats.shape)

    # Get the row and column index
    lat_index, lon_index = min_index
    print(lat_index, lon_index)

    # compute distance from each grid point to storm center
    rlonfac[:,:] = 111000. * np.cos((np.pi/ 180) * lats[:, :])
    ydist[:,:]   = (lats[:, :] - lats[lon_index, lat_index]) * 111000
    plt.imshow(ydist)
    plt.show()
    xdist[:,:]   = (lons[:,:] - (lons[lon_index, lat_index])) * rlonfac
    plt.imshow(xdist)
    plt.show()
    tcdist  = (xdist**2 + ydist**2)**0.5
    plt.imshow(tcdist)
    plt.show()

    #cvalculate angle
    theta_ang = np.arctan2(ydist, xdist)

    # Pre-calculate cos and sin of theta_ang for use in vectorized calculations
    cos_theta = np.cos(theta_ang)
    sin_theta = np.sin(theta_ang)
    for k in range(len(level)):
        print(uData.shape, u_radial.shape)
        #print("The number loop we are in is", k)
        # Vectorized calculation of u_radial and v_azimuth
        u_radial[:, :, k] = uData[k, :, :].values * cos_theta + vData[k, :, :].values * sin_theta
        v_azimuth[:, :, k] = -uData[k, :, :].values * sin_theta + vData[k, :, :].values * cos_theta
        
        f = 2 * 7.292e-5 * np.sin(lats * (np.pi / 180))

        # Vectorized calculation of momentum
        momentum[:, : , k] = tcdist * v_azimuth[:,:,k] + (1/2) * f * (tcdist**2)
        L[:, :, k] = level[k]
    print(momentum.shape)
    momentum = interp.log_interpolate_1d(np.arange(700, 1005, 5), L, momentum, axis = 2)
    print(momentum.shape)
    surface = momentum[:, :, -1]#np.argmax(momentum == 1.5e8, axis = 2)
    print(surface.shape)

    # Creates the plot
    ax = map(5, 9)
    
    c = ax.contourf(uData.longitude, uData.latitude, surface, levels = 100, cmap = cmap.tempAnoms(), extend = 'both')
    #ax.streamplot(uData.longitude, vData.latitude, uData.sel(level = 850).values, vData.sel(level = 850).values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    ax.text(lon, lat, 'X', size = 30, color = '#bf3030', horizontalalignment = 'center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], verticalalignment = 'center', transform = ccrs.PlateCarree(central_longitude = 0))

    ax.set_title(f'1.5e8 Angular Momentum Surface\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    try:
        ax.set_title(f'{name.upper()}', fontsize = 10, loc = 'center')
    except:
        ax.set_title(f'{name}', fontsize = 10, loc = 'center')
    ax.set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\deela\Downloads\ERA5Wind.png", dpi = 200, bbox_inches = 'tight')    
    plt.show() 

print('test 1')
momentumPlot('9', '6', '2017', '00', [750, 775, 800, 825, 850, 875, 900, 925, 950, 1000], 'irma')