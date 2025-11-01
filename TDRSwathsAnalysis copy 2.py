import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from helper import helicity, helicityv2
import matplotlib.patheffects as pe
from helper import trapezoidalRule
from file import getGZ 
import urllib.request
from scipy.ndimage import gaussian_filter

index = 6

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

def spmap(ax, interval, labelsize, dark = False):
    ax.set_frame_on(False)

    # Add state boundaries to plot
    if dark == False:
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
        ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
        ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
        ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
        ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
        ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    else:
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
        ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor = 'white', linewidth = 0.5)
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), color = 'black')
        ax.add_feature(cfeature.LAND.with_scale('50m'), color = 'black')
        ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
        ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
        ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
        ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
        ax.grid(linestyle = '--', alpha = 0.5, color = 'white', linewidth = 0.5, zorder = 9)

    return ax 

def updraftHelicity(dataset, level):
    vort = dataset['swath_relative_vorticity'].sel(level = slice(2, 5))
    vert = dataset['swath_upward_air_velocity'].sel(level = slice(2, 5))
    temp = vort.mean('height')
    temp.values = np.trapz((vort * vert), vort.height, axis=vort.get_axis_num('height'))

    return temp

def computeStretching(dataset, level):
    # Stretching Term
    # omega = 7.2921159e-5           
    # f = 2 * omega * np.sin(np.deg2rad(dataset['latitude']))
    # temp = dataset['swath_relative_vorticity'].sel(height = level) + f
    # temp = temp.isel(latitude=slice(1, None), longitude=slice(1, None))

    # u = dataset['swath_eastward_wind'].sel(height = level)
    # ux, uy = Gradient2D(u)
    # v = dataset['swath_northward_wind'].sel(height = level)
    # vx, vy = Gradient2D(v)

    # temp.values = (temp.values*ux + temp.values*vy)

    omega = 7.2921159e-5           
    f = 2 * omega * np.sin(np.deg2rad(dataset['LATITUDE']))
    temp = (dataset['VORT'].sel(level = level) / 1000) + f
    # temp = temp.isel(latitude=slice(1, None), longitude=slice(1, None))

    vert = dataset['W'].differentiate('level').sel(level = level)

    temp = (temp * vert)

    return temp

def computeVerticalAdvection(dataset, level):
    # Vertical Advection Term
    temp = dataset['swath_upward_air_velocity'].sel(level = level)
    vort = dataset['swath_relative_vorticity'].differentiate('height').sel(level = level)
    temp.values = -temp.values * vort

    return temp

def computeHelicity(dataset):
    data = dataset.sel(level = slice(0.5, 3))
    umotion = dataset['U'].sel(level = slice(0.5, 6.5)).mean(['level']).squeeze().astype('float32')
    vmotion = dataset['V'].sel(level = slice(0.5, 6.5)).mean(['level']).squeeze().astype('float32')

    hgts = data.level
    print(hgts.values)
    arr1 = []
    for x in range(len(dataset.x)):
        arr2 = []
        for y in range(len(dataset.y)):
            uM = umotion.sel(x = dataset.x[x], y = dataset.y[y]).values
            vM = vmotion.sel(x = dataset.x[x], y = dataset.y[y]).values
            uwnd = data['U'].sel(x = dataset.x[x], y = dataset.y[y]).astype('float32').squeeze().values
            vwnd = data['V'].sel(x = dataset.x[x], y = dataset.y[y]).astype('float32').squeeze().values
            if np.isnan(uwnd).any():
                temp = np.nan
            else:
                temp = helicity(hgts, uwnd, vwnd, uM, vM)
            arr2.append(temp)
        arr1.append(arr2)
    srh = np.array(arr1)

    return srh, umotion, vmotion

def computeHelicityv2(dataset):
    data = dataset.sel(level = slice(0.5, 3))
    umotion = dataset['U'].sel(level = slice(0.5, 6.5)).mean(['level']).squeeze().astype('float32')
    vmotion = dataset['V'].sel(level = slice(0.5, 6.5)).mean(['level']).squeeze().astype('float32')


    uM = umotion#.sel(x = dataset.x[x], y = dataset.y[y]).values
    vM = vmotion#.sel(x = dataset.x[x], y = dataset.y[y]).values
    uwnd = data['U']#.sel(x = dataset.x[x], y = dataset.y[y]).astype('float32').squeeze().values
    vwnd = data['V']#.sel(x = dataset.x[x], y = dataset.y[y]).astype('float32').squeeze().values
    
    temp = helicityv2(uwnd, vwnd, uM, vM)

    print(temp)

    return temp.squeeze().values, umotion, vmotion

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = (data['longitude'].diff('longitude') * np.cos(data['latitude'] * (np.pi / 180)))[:, 1:]
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

def panelPlot(dataset, mission, height):
    # clon = dataset['tc_center_longitudes'].sel(height = height).values
    # clat = dataset['tc_center_latitudes'].sel(height = height).values

    # clon2 = dataset['tc_center_longitudes'].sel(height = slice(2, 4)).mean('height').values
    # clat2 = dataset['tc_center_latitudes'].sel(height = slice(2, 4)).mean('height').values

    clon = dataset['LONGITUDE'].mean('x').values[0]
    clat = dataset['LATITUDE'].mean('y').values[0]
    print(clon, clat)

    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(2, 2)

    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree())]
    
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_frame_on(False)

    for x in range(1, 5):
        axes[x] = spmap(axes[x], .5, 8)
        try:
            axes[x].set_extent([clon - 1, clon + 1, clat - 1, clat + 1], crs=ccrs.PlateCarree())
        except:
            try:
                axes[x].set_extent([clon2 - 1, clon2 + 1, clat2 - 1, clat2 + 1], crs=ccrs.PlateCarree())
            except:
                pass
    
    lats = dataset['LATITUDE'].squeeze()
    lons = dataset['LONGITUDE'].squeeze()
    # date = f"{str(dataset['swath_year'].values)}-{str(dataset['swath_month'].values).zfill(2)}-{str(dataset['swath_day'].values).zfill(2)} at {str(dataset['swath_hour'].values).zfill(2)}{str(dataset['swath_min'].values).zfill(2)}z"
    date = dataset['time']
    print(date)
    
    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar {height}km Diagnostic Plot\n{mission}', fontweight='bold', fontsize=10, loc='left')
    # axes[0].set_title(f'{date} (Case #{int(caseNum)})', fontsize=10, loc='center')
    axes[0].set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons, lats, dataset['REFLECTIVITY'].sel(level = height).squeeze().values, cmap = cmap.reflectivity2(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    
    srh, umotion, vmotion = computeHelicityv2(dataset)
    cr = axes[2].pcolormesh(lons, lats, srh, cmap = cmap.tempAnoms3(), vmin = -50, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, '0.5-3km Storm-Relative Helicity', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], dataset['U'].sel(level = 3).squeeze().values[::index, ::index], dataset['V'].sel(level = 3).squeeze().values[::index, ::index], color = 'purple', transform = ccrs.PlateCarree(central_longitude = 0), label = '3km')
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], dataset['U'].sel(level = 6).squeeze().values[::index, ::index], dataset['V'].sel(level = 6).squeeze().values[::index, ::index], color = 'red', transform = ccrs.PlateCarree(central_longitude = 0), label = '6km')
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], umotion.values[::index, ::index], vmotion.values[::index, ::index], color = 'blue', transform = ccrs.PlateCarree(central_longitude = 0), label = 'Motion')
    # axes[2].text(dataset['tc_center_longitudes'].sel(height = 3), dataset['tc_center_latitudes'].sel(height = 3), 'S', size = 15, color = '#9b30bf', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))
    # axes[2].text(dataset['tc_center_longitudes'].sel(height = 6), dataset['tc_center_latitudes'].sel(height = 6), 'M', size = 15, color = '#bf3030', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))
    # axes[2].legend(loc = 'lower right')

    # stretching = updraftHelicity(dataset, level = height)
    # cv = axes[2].contourf(lons, lats, stretching.values, cmap = cmap.probs(), levels = np.arange(0, .01, 0.00005), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    # cbar = plt.colorbar(cv, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    # cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    # axes[2].text(0.5, 0.95, '2-5km Updraft Helicity', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)

    stretching = computeStretching(dataset, height)
    stretching.values = gaussian_filter(stretching, sigma = 0.75)
    cv = axes[3].pcolormesh(lons, lats, stretching.squeeze().values, cmap = cmap.tempAnoms3(), vmin = -.002, vmax = .002, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Vorticity Stretching', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    
    vc = axes[4].pcolormesh(lons, lats, dataset['VORT'].sel(level = height).squeeze().values / 1000, cmap = cmap.probs(), vmin = 0, vmax = 0.005, transform=ccrs.PlateCarree(central_longitude=0))
    axes[4].streamplot(lons, lats, dataset['U'].sel(level = 3).squeeze().values, dataset['V'].sel(level = 3).squeeze().values, linewidth = 1, density = 1, color = '#9b30bf', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[4].streamplot(lons, lats, dataset['U'].sel(level = 6).squeeze().values, dataset['V'].sel(level = 6).squeeze().values, linewidth = 1, density = 1, color = '#bf3030', transform = ccrs.PlateCarree(central_longitude = 0))
    cbar = plt.colorbar(vc, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Relative Vorticity (1/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    # axes[4].text(dataset['tc_center_longitudes'].sel(height = 3), dataset['tc_center_latitudes'].sel(height = 3), 'S', size = 15, color = '#9b30bf', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), label = '3km Center')
    # axes[4].text(dataset['tc_center_longitudes'].sel(height = 6), dataset['tc_center_latitudes'].sel(height = 6), 'M', size = 15, color = '#bf3030', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), label = '6km Center')
    # axes[4].legend(loc = 'lower right')

    # DSHR = dataset["shdc_ships"].sel(ships_lag_times=0).values
    # DDIR = dataset["sddc_ships"].sel(ships_lag_times=0).values
    # u, v = DSHR * np.sin(np.deg2rad(DDIR)), DSHR * np.cos(np.deg2rad(DDIR))
    
    # axes[2].text(0.1, 0.19, f'200-850mb', color = 'black', fontsize = 8, ha = 'center', fontweight = 'bold', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75}, transform = axes[2].transAxes)
    # # axes[2].quiver(2.5, 0.046, u / DSHR, v / DSHR, pivot = 'middle', scale = 30, minshaft = 3, minlength=0, headaxislength = 3, headlength = 3, color = '#ff5959', zorder = 20, path_effects = [pe.withStroke(linewidth=1.25, foreground="black")], transform = axes[2].transAxes)
    # axes[2].annotate("", xy= (0.10 + (u/DSHR)*0.075, 0.10 + (v/DSHR)*0.075), xytext=(0.10,0.10), xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", color="#ff5959", lw=1.5, mutation_scale=12, path_effects=[pe.withStroke(linewidth=1.25, foreground="black")]), zorder=20, annotation_clip=False)
    # axes[2].text(0.1, 0.065, f'{round(float(DSHR), 1)} knots', fontsize = 8, color = 'black', ha = 'center', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75}, transform = axes[2].transAxes)

    plt.savefig(r"C:\Users\deela\Downloads\TDRTest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()

link = 'https://seb.omao.noaa.gov/pub/flight/radar/20251027H1/251027H1_1121_xy.nc.gz'
urllib.request.urlretrieve(link, r"C:\Users\deela\Downloads\RTTDR.nc.gz")
getGZ(r"C:\Users\deela\Downloads\RTTDR.nc.gz")

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\RTTDR.nc")

print(list(dataset.variables.keys()))

height = 2
panelPlot(dataset, link.split('/')[6], height = height)

print(dataset['VORT'])