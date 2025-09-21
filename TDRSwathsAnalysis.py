import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from helper import helicity
import matplotlib.patheffects as pe
from helper import trapezoidalRule

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
    vort = dataset['swath_relative_vorticity'].sel(height = slice(2, 5))
    vert = dataset['swath_upward_air_velocity'].sel(height = slice(2, 5))
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
    f = 2 * omega * np.sin(np.deg2rad(dataset['latitude']))
    temp = dataset['swath_relative_vorticity'].sel(height = level) + f
    # temp = temp.isel(latitude=slice(1, None), longitude=slice(1, None))

    vert = dataset['swath_upward_air_velocity'].differentiate('height').sel(height = level)

    temp = (temp * vert)

    return temp

def computeVerticalAdvection(dataset, level):
    # Vertical Advection Term
    temp = dataset['swath_upward_air_velocity'].sel(height = level)
    vort = dataset['swath_relative_vorticity'].differentiate('height').sel(height = level)
    temp.values = -temp.values * vort

    return temp

def computeHelicity(dataset):
    data = dataset.sel(height = slice(0.5, 3))
    umotion = dataset['swath_earth_relative_eastward_wind'].sel(height = slice(0.5, 6.5)).mean(['height']).astype('float32')
    vmotion = dataset['swath_earth_relative_northward_wind'].sel(height = slice(0.5, 6.5)).mean(['height']).astype('float32')

    hgts = data.height
    print(hgts.values)
    arr1 = []
    for x in range(len(dataset.longitude)):
        arr2 = []
        for y in range(len(dataset.latitude)):
            uM = umotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            vM = vmotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            uwnd = data['swath_earth_relative_eastward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).astype('float32').values
            vwnd = data['swath_earth_relative_northward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).astype('float32').values
            if np.isnan(uwnd).any():
                temp = np.nan
            else:
                temp = helicity(hgts, uwnd, vwnd, uM, vM)
            arr2.append(temp)
        arr1.append(arr2)
    srh = np.array(arr1)

    return srh.T, umotion, vmotion

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

# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc")
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc")

print(list(dataset.variables.keys()))

def retrieveStorm(name, year = None):
    names = dataset['storm_name']
    print(names.values)
    years = dataset['swath_year']
    names = names.where(names == name.upper(), drop = True)
    
    years = years.sel(num_cases = names['num_cases'].values)
    if year == None:
        print(f'Available Years for Storm {name.upper()}: {list(set(years.values))}')
    else:
        years = years.where(years == year, drop = True)
    
    return dataset.sel(num_cases = years['num_cases'].values)

def panelPlot(dataset, caseNum, height):
    print(dataset['mission_ID'].values)
    clon = dataset['tc_center_longitudes'].sel(height = height).values
    clat = dataset['tc_center_latitudes'].sel(height = height).values

    clon2 = dataset['tc_center_longitudes'].sel(height = slice(2, 4)).mean('height').values
    clat2 = dataset['tc_center_latitudes'].sel(height = slice(2, 4)).mean('height').values

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
        axes[x] = spmap(axes[x], .25, 8)
        try:
            axes[x].set_extent([clon - 1, clon + 1, clat - 1, clat + 1], crs=ccrs.PlateCarree())
        except:
            try:
                axes[x].set_extent([clon2 - 1, clon2 + 1, clat2 - 1, clat2 + 1], crs=ccrs.PlateCarree())
            except:
                pass
    
    lats = dataset['original_latitudes']
    lons = dataset['original_longitudes']
    date = f"{str(dataset['swath_year'].values)}-{str(dataset['swath_month'].values).zfill(2)}-{str(dataset['swath_day'].values).zfill(2)} at {str(dataset['swath_hour'].values).zfill(2)}{str(dataset['swath_min'].values).zfill(2)}z"
    print(date)
    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar {height}km Diagnostic Plot\n{name} {year}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date} (Case #{int(caseNum)})', fontsize=10, loc='center')
    axes[0].set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons, lats, dataset['swath_reflectivity'].sel(height = height).values, cmap = cmap.reflectivity2(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    
    srh, umotion, vmotion = computeHelicity(dataset)
    cr = axes[2].pcolormesh(lons, lats, srh, cmap = cmap.tempAnoms3(), vmin = -50, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, '0.5-3km Storm-Relative Helicity', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 3).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 3).values[::index, ::index], color = 'purple', transform = ccrs.PlateCarree(central_longitude = 0), label = '3km')
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 6).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 6).values[::index, ::index], color = 'red', transform = ccrs.PlateCarree(central_longitude = 0), label = '6km')
    axes[2].quiver(lons[::index, ::index], lats[::index, ::index], umotion.values[::index, ::index], vmotion.values[::index, ::index], color = 'blue', transform = ccrs.PlateCarree(central_longitude = 0), label = 'Motion')
    axes[2].text(dataset['tc_center_longitudes'].sel(height = 3), dataset['tc_center_latitudes'].sel(height = 3), 'S', size = 15, color = '#9b30bf', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))
    axes[2].text(dataset['tc_center_longitudes'].sel(height = 6), dataset['tc_center_latitudes'].sel(height = 6), 'M', size = 15, color = '#bf3030', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))
    axes[2].legend(loc = 'lower right')

    # stretching = updraftHelicity(dataset, level = height)
    # cv = axes[2].contourf(lons, lats, stretching.values, cmap = cmap.probs(), levels = np.arange(0, .01, 0.00005), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    # cbar = plt.colorbar(cv, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    # cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    # axes[2].text(0.5, 0.95, '2-5km Updraft Helicity', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)

    stretching = computeStretching(dataset, height)
    cv = axes[3].pcolormesh(lons, lats, stretching.values, cmap = cmap.tempAnoms3(), vmin = -.001, vmax = .001, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Vorticity Stretching', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    
    vc = axes[4].pcolormesh(lons, lats, dataset['swath_relative_vorticity'].sel(height = height).values, cmap = cmap.probs(), vmin = 0, vmax = 0.005, transform=ccrs.PlateCarree(central_longitude=0))
    axes[4].streamplot(lons, lats, dataset['swath_eastward_wind'].sel(height = 3).values, dataset['swath_northward_wind'].sel(height = 3).values, linewidth = 1, density = 1, color = '#9b30bf', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[4].streamplot(lons, lats, dataset['swath_eastward_wind'].sel(height = 6).values, dataset['swath_northward_wind'].sel(height = 6).values, linewidth = 1, density = 1, color = '#bf3030', transform = ccrs.PlateCarree(central_longitude = 0))
    cbar = plt.colorbar(vc, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Relative Vorticity (1/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    axes[4].text(dataset['tc_center_longitudes'].sel(height = 3), dataset['tc_center_latitudes'].sel(height = 3), 'S', size = 15, color = '#9b30bf', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), label = '3km Center')
    axes[4].text(dataset['tc_center_longitudes'].sel(height = 6), dataset['tc_center_latitudes'].sel(height = 6), 'M', size = 15, color = '#bf3030', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0), label = '6km Center')
    # axes[4].legend(loc = 'lower right')

    DSHR = dataset["shdc_ships"].sel(ships_lag_times=0).values
    DDIR = dataset["sddc_ships"].sel(ships_lag_times=0).values
    u, v = DSHR * np.sin(np.deg2rad(DDIR)), DSHR * np.cos(np.deg2rad(DDIR))
    
    axes[2].text(0.1, 0.19, f'200-850mb', color = 'black', fontsize = 8, ha = 'center', fontweight = 'bold', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75}, transform = axes[2].transAxes)
    # axes[2].quiver(2.5, 0.046, u / DSHR, v / DSHR, pivot = 'middle', scale = 30, minshaft = 3, minlength=0, headaxislength = 3, headlength = 3, color = '#ff5959', zorder = 20, path_effects = [pe.withStroke(linewidth=1.25, foreground="black")], transform = axes[2].transAxes)
    axes[2].annotate("", xy= (0.10 + (u/DSHR)*0.075, 0.10 + (v/DSHR)*0.075), xytext=(0.10,0.10), xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", color="#ff5959", lw=1.5, mutation_scale=12, path_effects=[pe.withStroke(linewidth=1.25, foreground="black")]), zorder=20, annotation_clip=False)
    axes[2].text(0.1, 0.065, f'{round(float(DSHR), 1)} knots', fontsize = 8, color = 'black', ha = 'center', path_effects = [pe.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75}, transform = axes[2].transAxes)

    plt.savefig(r"C:\Users\deela\Downloads\\TDR_Swaths_v2\\" + date + "_" + str(height) + ".png", dpi = 400, bbox_inches = 'tight')
    # plt.show()
    plt.close()
name = 'TDR'
year = 2024
height = 3
data = retrieveStorm(name, year)
print(data.num_cases.values)
refl = data['swath_wind_speed'].sel(height = height) * 1.94384

ax = map(2, 9)
ax.set_extent([-120, 0, 0, 60])
for x in range(len(refl.num_cases)):
    case = refl.num_cases[x].values
    print(case)
    panelPlot(data.sel(num_cases = case), case, height = height)

#     temp = refl.sel(num_cases = refl.num_cases[x])
#     lats = data['original_latitudes'].sel(num_cases = refl.num_cases[x])
#     lons = data['original_longitudes'].sel(num_cases = refl.num_cases[x])
#     c = plt.pcolormesh(lons, lats, temp.values, cmap = cmap.wind(), vmin = 0, vmax = 160, transform=ccrs.PlateCarree(central_longitude=0))
# ax.set_title(f'TC-RADAR: Tail Doppler Radar {height}km Reflectivity\n{name} {year}', fontweight='bold', fontsize=9, loc='left')
# ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
# cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
# cbar.set_ticks(np.arange(0, 170, 10))
# plt.savefig(r"C:\Users\deela\Downloads\tdrtest.png", dpi = 400, bbox_inches = 'tight')
# plt.show()

# for x in range(len(data.height.values)):
#     case = 423
#     panelPlot(data.sel(num_cases = case), case, height = data.height.values[x])