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

def updraftHelicity(dataset, bottom = 2, top = 5):
    vort = dataset['swath_relative_vorticity'].sel(height = slice(bottom, top))
    vert = dataset['swath_upward_air_velocity'].sel(height = slice(bottom, top))
    temp = vort.mean('height')
    temp.values = np.trapz((vort * vert), vort.height, axis=vort.get_axis_num('height'))

    return temp, bottom, top

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

def computeDivergence(dataset, level):
    # Stretching Term
    u = dataset['swath_eastward_wind'].sel(height = level)
    ux, uy = Gradient2D(u)
    v = dataset['swath_northward_wind'].sel(height = level)
    vx, vy = Gradient2D(v)

    temp = ux + vy

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

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
# dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc")

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
    ax = map(.5, 8)
    
    clon = dataset['tc_center_longitudes'].sel(height = height).values
    clat = dataset['tc_center_latitudes'].sel(height = height).values

    lats = dataset['original_latitudes']
    lons = dataset['original_longitudes']
    date = f"{str(dataset['swath_year'].values)}-{str(dataset['swath_month'].values).zfill(2)}-{str(dataset['swath_day'].values).zfill(2)} at {str(dataset['swath_hour'].values).zfill(2)}{str(dataset['swath_min'].values).zfill(2)}z"
    ax.set_title(f'TC-RADAR: Tail Doppler Radar {height}km Diagnostic Plot\n{name} {year}', fontweight='bold', fontsize=10, loc='left')
    ax.set_title(f'{date} (Case #{int(caseNum)})', fontsize=10, loc='center')
    ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    # stretching, bottom, top = updraftHelicity(dataset, 3, 8)
    # cv = ax.contourf(lons, lats, stretching.values, cmap = cmap.probs(), levels = np.arange(0, .01, 0.00005), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    # cbar = plt.colorbar(cv, ax = ax, orientation = 'vertical', aspect = 50, pad = .02)
    # cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    # ax.text(0.5, 0.95, f'{bottom}-{top}km Updraft Helicity', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

    # stretching = computeStretching(dataset, height)
    # cv = ax.contourf(lons.sel(longitude = slice(1, None), latitude = slice(1, None)), lats.sel(longitude = slice(1, None), latitude = slice(1, None)), stretching.values, cmap = cmap.tempAnoms3(), levels = np.arange(-0.05, .05, 0.00005), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    # cbar = plt.colorbar(cv, ax = ax, orientation = 'vertical', aspect = 50, pad = .02)
    # cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    # ax.text(0.5, 0.95, f'{height}km Vorticity Stretching', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

    stretching = computeStretching(dataset, height)
    # stretching.values = gaussian_filter(stretching.values, sigma = 1)
    try:
        cv = ax.contourf(lons.sel(longitude = slice(1, None), latitude = slice(1, None)), lats.sel(longitude = slice(1, None), latitude = slice(1, None)), stretching.values, cmap = cmap.tempAnoms3(), levels = np.arange(-20, 20, 0.02), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    except:
        cv = ax.contourf(lons, lats, stretching.values, cmap = cmap.tempAnoms3(), levels = np.arange(-.001, .001, 0.00001), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = ax, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.text(0.5, 0.95, f'{height}km Vorticity Stretching', color = 'black', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

    plt.savefig(r"C:\Users\deela\Downloads\stretching3km.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()
name = 'Fay'
year = 2008
height = 6
data = retrieveStorm(name, year)
print(data.num_cases.values)
refl = data['swath_wind_speed'].sel(height = height) * 1.94384

# ax = map(2, 9)
# ax.set_extent([-120, 0, 0, 60])
for x in range(len(refl.num_cases)):
    case = refl.num_cases[x].values
    case = 28
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


# print(dataset.sel(num_cases = 1051 - 710, height = 2.0)['tc_center_longitudes'].values, dataset.sel(num_cases = 1051 - 710, height = 2.0)['tc_center_latitudes'].values)

# cases = [1051 - 710]
# # ax = map(2, 9)
# for x in range(len(cases)):
#     panelPlot(dataset.sel(num_cases = cases[x]), cases[x], height)
