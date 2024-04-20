import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
from datetime import datetime 
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle
import cdsapi as cds 
import hurdatParser

c = cds.Client()

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
            'area'          : [lat + 15, lon - 15, lat - 15, lon + 15], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

labelsize = 8 
level = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
database = hurdatParser.database()

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(level = top) - u.sel(level = bot)
    vShear = v.sel(level = top) - v.sel(level = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

# Function that cleans up the plotting of the wind data
def windbarbs(ax, uwnd, vwnd, txt, lat, lon):
    uwnd = uwnd * 1.9438
    vwnd = vwnd * 1.9438
    mag = (uwnd**2 + vwnd**2)**0.5
    ax.streamplot(uwnd.longitude[::2], vwnd.latitude[::2], uwnd[::2, ::2].values, vwnd[::2, ::2].values, zorder = 11, linewidth = .5, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 360))
    c = ax.contourf(uwnd.longitude, vwnd.latitude, mag.values, cmap = cmap.shear(), zorder = 10, levels = np.arange(0, 80, .1), alpha = 1, extend = 'max', transform = ccrs.PlateCarree(central_longitude = 360))

    mU = uwnd.sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5)).mean(['latitude', 'longitude'])
    mV = vwnd.sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5)).mean(['latitude', 'longitude'])
    mMag = shearMag(mU, mV)
    ax.text(lon - 9, lat + 6, f'{txt}', color = 'black', fontsize = 14, fontweight = 'bold', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
    ax.text(lon, lat - 1, f'{round(mMag, 1)} knots', color = 'black', ha = 'center', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
    ax.quiver(np.array([lon]), np.array([lat + .5]), np.array([mU.values]) / mMag, np.array([mV.values]) / mMag, pivot = 'middle', scale = 15, minshaft = 2, minlength=0, headaxislength = 3, headlength = 3, color = '#ff5959', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="black")], transform = ccrs.PlateCarree(central_longitude = 360))
    return c

# Self explanatory
def makeMap(axes, lat, lon):
    # Remove the ticklabels from the main plot
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    
    # Loop through the four panels and create the map, as well as the red box in the center
    for x in range(1, 5):
        axes[x].tick_params(axis='both', direction='in')
        axes[x].add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 1, zorder = 20)
        axes[x].add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 1, zorder = 20)
        axes[x].add_feature(cfeature.STATES.with_scale('50m'), linewidth = 1, zorder = 20)
        gl = axes[x].gridlines(crs=ccrs.PlateCarree(central_longitude = 0), zorder = 20, draw_labels = True, linewidth = 0.5, color='black', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
        gl.xlabel_style, gl.ylabel_style = {'size': 8}, {'size': 8}
        gl.xlabels_top = False 

        if lon < 0:
            lon = 360 + lon
        axes[x].set_extent([lon - 10, lon + 10, lat - 7.5, lat + 7.5], crs = ccrs.PlateCarree())

        boxXCoords = [lon - 2.5, lon + 2.5, lon + 2.5, lon - 2.5, lon - 2.5]
        boxYCoords = [lat - 2.5, lat - 2.5, lat + 2.5, lat + 2.5, lat - 2.5]
        for y in range(len(boxXCoords)):
            try:
                axes[x].plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'red', zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
            except:
                pass
        r = Rectangle((lon - 2.5, lat - 2.5), 5, 5, zorder = 19, color = '#bfbfbf', alpha = 0.4, transform = ccrs.PlateCarree(central_longitude = 360))
        axes[x].add_patch(r)
        
# Helper function to calculate maximum shear
# Returns the upper and lower level that compose this shear vector as integers
def maxShear(u, v):
    #Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    levels = np.arange(200, 900, 50)

    ar1 = {}
    for x in levels:
        for y in levels:
            if y > x:
                uShear, vShear = calcShear(u, v, x, y)
                ar1[f'{x}-{y}'] = shearMag(uShear, vShear)
            else:
                pass
    return [int((max(ar1, key = ar1.get)).split('-')[0]), int((max(ar1, key = ar1.get)).split('-')[1])]

# Function to put together the whole plot
def finalPlot(year, month, day, hour, name):
    if type(name) == str:
        # Retrieve storm data from HURDAT2
        stormData = hurdatParser.retrieveStorm(database, [name, str(year)])['Storm Data']
        stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
        lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
    else:
        lat, lon = name
    
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, lat, lon)

    # Requests GFS zonal and meridional wind data 
    # Creates four tuples to hold the model data
    # Calculates the maximum shear vector using the above function
    retrieve(['u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")
    uData = (data['u']).squeeze()
    vData = (data['v']).squeeze()

    data = [uData, vData]
    deep, mid, upper, maxi = (), (), (), ()
    top, bot = maxShear(uData.sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5)).mean(['latitude', 'longitude']), vData.sel(latitude = slice(lat + 2.5, lat - 2.5), longitude = slice(lon - 2.5, lon + 2.5)).mean(['latitude', 'longitude']))

    # Calculates the shear layers and adds them to the tuples that were initialized above
    for x in range(len(data)):
        data[x] = data[x].sel(longitude = slice(lon - 11, lon + 11), latitude = slice(lat + 8, lat - 8))

        deep = deep + (data[x].sel(level = 200) - data[x].sel(level = 850),)
        mid = mid + (data[x].sel(level = 500) - data[x].sel(level = 850),)
        upper = upper + (data[x].sel(level = 200) - data[x].sel(level = 500),)
        maxi = maxi + (data[x].sel(level = top) - data[x].sel(level = bot),)
    shear = [deep, mid, upper, maxi]
    shearText = '200-850mb', '500-850mb', '200-500mb', f'{str(top)}-{str(bot)}mb'

    # Creates the plot
    fig = plt.figure(figsize=(11.9, 9))
    gs = fig.add_gridspec(2, 2, wspace = 0, hspace = 0)
    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree())]
    makeMap(axes, lat, lon)
    for x in range(len(axes[1:])):
        c = windbarbs(axes[x + 1], shear[x][0], shear[x][1], shearText[x], lat, lon)

    axes[0].set_title(f'Wind Shear Diagnostics\n{date} at {hour}:00z', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'IRMA', fontsize = 10, loc = 'center')
    axes[0].set_title('0.25\u00b0 ERA5\nDeelan Jariwala', fontsize=10, loc='right') 
    #axes[0].set_title('##L\nDeelan Jariwala', fontsize=10, loc='right') 

    # Since Matplotlib was being difficult, this is the colorbar 
    cax = inset_axes(axes[3], width="200%", height="3%", loc='lower right', bbox_to_anchor=(1, -0.1, 1, 1), bbox_transform=axes[3].transAxes, borderpad = .02)
    cb = fig.colorbar(c, cax=cax, orientation="horizontal")
    cb.set_ticks(range(0, 85, 5))
    plt.savefig(r"C:\Users\deela\Downloads\shearDiagnostics.png", dpi = 400, bbox_inches = 'tight')
    plt.show() 

# Sample Usage
finalPlot('2017', '09', '05', '18', 'irma')