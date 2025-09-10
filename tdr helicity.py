import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
from helper import helicity
from satcmaps import tdr
import matplotlib.patheffects as pe

index = 6

def map(interval, labelsize, dark = False):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
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

def spmap(ax, interval, labelsize, dark = False):
    ax.set_frame_on(False)

    # Add state boundaries to plot
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

def panelPlot(dataset, caseNum):
    data = dataset.sel(height = slice(0.5, 3))

    fig = plt.figure(figsize=(16, 6))
    gs = fig.add_gridspec(1, 2, wspace = 0, hspace = .2)

    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1], projection = ccrs.PlateCarree())]
    
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_frame_on(False)

    ax = spmap(axes[1], .25, 8)
    ax2 = spmap(axes[2], .25, 8, True)
    
    lats = data['original_latitudes']
    lons = data['original_longitudes']

    clat = lats.isel(latitude = 100, longitude = 100).values
    clon = lons.isel(latitude = 100, longitude = 100).values
    extent = [clon - 1, clon + 1, clat - 1, clat + 1]
    ax.set_extent(extent)
    ax2.set_extent(extent)

    date = f"{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)} at {str(data['swath_hour'].values).zfill(2)}{str(data['swath_min'].values).zfill(2)}z"
    print(date)
    # plt.pcolormesh(lons, lats, data['swath_eastward_wind'].sel(height = 0.5).values)
    # plt.show()
    umotion = dataset['swath_earth_relative_eastward_wind'].sel(height = slice(0.5, 6.5)).mean(['height'])#data['motion_x_ships'].sel(num_ships_times = 0).values
    vmotion = dataset['swath_earth_relative_northward_wind'].sel(height = slice(0.5, 6.5)).mean(['height'])#data['motion_y_ships'].sel(num_ships_times = 0).values

    hgts = data.height
    print(hgts.values)
    arr1 = []
    for x in range(len(dataset.longitude)):
        arr2 = []
        for y in range(len(dataset.latitude)):
            uM = umotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            vM = vmotion.sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            uwnd = data['swath_earth_relative_eastward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            vwnd = data['swath_earth_relative_northward_wind'].sel(longitude = dataset.longitude[x], latitude = dataset.latitude[y]).values
            if np.isnan(uwnd).any():
                temp = np.nan
            else:
                temp = helicity(hgts, uwnd, vwnd, uM, vM)
                print(x, y, temp)
            arr2.append(temp)
        arr1.append(arr2)
    srh = np.array(arr1)

    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar 0.5-3km Storm Relative Helicity\n{name} {year}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date} (Case #{int(caseNum)})', fontsize=10, loc='center')
    ax2.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = ax.pcolormesh(lons, lats, srh.T, cmap = cmap.tempAnoms3(), vmin = -100, vmax = 100, transform=ccrs.PlateCarree(central_longitude=0))
    # cr = ax.pcolormesh(lons, lats, dataset['swath_reflectivity'].sel(height = 3).values, cmap = tdr()[0], vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = ax, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.text(0.5, 0.95, 'Storm-Relative Helicity', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)
    ax.quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 2).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 2).values[::index, ::index], color = 'purple', transform = ccrs.PlateCarree(central_longitude = 0), label = '2km')
    ax.quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 5).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 5).values[::index, ::index], color = 'red', transform = ccrs.PlateCarree(central_longitude = 0), label = '5km')
    ax.quiver(lons[::index, ::index], lats[::index, ::index], umotion.values[::index, ::index], vmotion.values[::index, ::index], color = 'blue', transform = ccrs.PlateCarree(central_longitude = 0), label = 'Motion')
    ax.text(dataset['tc_center_longitudes'].sel(height = 2), dataset['tc_center_latitudes'].sel(height = 2), 'S', size = 15, color = '#9b30bf', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))
    ax.text(dataset['tc_center_longitudes'].sel(height = 5), dataset['tc_center_latitudes'].sel(height = 5), 'M', size = 15, color = '#bf3030', horizontalalignment='center', verticalalignment='center', fontfamily = 'Courier New', fontweight = 'bold', path_effects=[pe.withStroke(linewidth=2.25, foreground="white")], transform = ccrs.PlateCarree(central_longitude = 0))

    leg = ax.legend(loc = 'upper right')
    leg.get_frame().set_linewidth(0.0)

    cr = ax2.pcolormesh(lons, lats, dataset['swath_reflectivity'].sel(height = 3).values, cmap = tdr()[0], vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = ax2, orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax2.text(0.5, 0.95, '3km Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, color = 'white', horizontalalignment='center', verticalalignment='center', transform = ax2.transAxes)
    ax2.quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 2).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 2).values[::index, ::index], color = 'purple', transform = ccrs.PlateCarree(central_longitude = 0), label = '2km')
    ax2.quiver(lons[::index, ::index], lats[::index, ::index], dataset['swath_eastward_wind'].sel(height = 5).values[::index, ::index], dataset['swath_northward_wind'].sel(height = 5).values[::index, ::index], color = 'red', transform = ccrs.PlateCarree(central_longitude = 0), label = '5km')
    ax2.quiver(lons[::index, ::index], lats[::index, ::index], umotion.values[::index, ::index], vmotion.values[::index, ::index], color = 'blue', transform = ccrs.PlateCarree(central_longitude = 0), label = 'Motion')#, scale = )

    leg = ax2.legend(loc = 'upper right')
    leg.get_frame().set_linewidth(0.0)

    plt.savefig(r"C:\Users\deela\Downloads\helenesrh\hel_" + date + ".png", dpi = 400, bbox_inches = 'tight')
    #plt.show()
    plt.close()
name = 'Helene'
year = 2024
height = 3
data = retrieveStorm(name, year)
print(list(data.variables))
print(data['tc_center_longitudes'])
refl = data['swath_wind_speed'].sel(height = height)
print(refl.num_cases)
# print(data['swath_month'].sel(num_cases = 435).values, data['swath_day'].sel(num_cases = 435).values, data['swath_hour'].sel(num_cases = 435).values, data['swath_min'].sel(num_cases = 435).values)
for x in range(len(refl.num_cases)):
    case = refl.num_cases[x].values
    panelPlot(data.sel(num_cases = case), case)