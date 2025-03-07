import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
import helper 
import warnings
import matplotlib.patheffects as pe
warnings.filterwarnings("ignore")

h = [5, 5.5, 6.0, 6.5]

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

def spmap(ax, interval, labelsize):
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

def retrieveStorm(name, year = None):
    names = dataset['storm_name']
    years = dataset['swath_year']
    names = names.where(names == name.upper(), drop = True)
    
    years = years.sel(num_cases = names['num_cases'].values)
    if year == None:
        print(f'Available Years for Storm {name.upper()}: {list(set(years.values))}')
    else:
        years = years.where(years == year, drop = True)
    
    return dataset.sel(num_cases = years['num_cases'].values)

def panelPlot(dataset, startCase, endCase):
    data1 = dataset.sel(num_cases = startCase)
    data2 = dataset.sel(num_cases = endCase)

    print(dataset['storm_name'].sel(num_cases = slice(startCase, endCase)).values)

    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
    try:
        tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
        targ = np.nanargmax(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
    except:
        tilt = np.max(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
        targ = np.argmax(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)

    clat1, clat2 = data1['tc_center_latitudes'].sel(height = h[targ[0]]).values, data2['tc_center_latitudes'].sel(height = h[targ[-1]]).values
    clon1, clon2 = data1['tc_center_longitudes'].sel(height = h[targ[0]]).values, data2['tc_center_longitudes'].sel(height = h[targ[-1]]).values
    
    vmax = dataset['vmax_ships'].sel(num_cases = slice(startCase, endCase), ships_lag_times = 0).values
    shd = dataset['sddc_ships'].sel(num_cases = slice(startCase, endCase), ships_lag_times = 0)
    shr = dataset['shdc_ships'].sel(num_cases = slice(startCase, endCase), ships_lag_times = 0)
    u, v = helper.dirSpdToUV(270 - shd, shr)

    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 3)

    axes = [fig.add_subplot(1, 1, 1),
            fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[1, 1], projection = ccrs.PlateCarree()),
            fig.add_subplot(gs[0, 2]),
            fig.add_subplot(gs[1, 2])]
    
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[0].set_frame_on(False)

    for x in range(1, 5):
        axes[x] = spmap(axes[x], .5, 5)
    
    lats1, lats2 = data1['original_latitudes'], data2['original_latitudes']
    lons1, lons2 = data1['original_longitudes'], data2['original_longitudes']
    date1 = f'{str(data1['swath_year'].values)}-{str(data1['swath_month'].values).zfill(2)}-{str(data1['swath_day'].values).zfill(2)} at {str(data1['swath_hour'].values).zfill(2)}{str(data1['swath_min'].values).zfill(2)}z'
    date2 = f'{str(data2['swath_year'].values)}-{str(data2['swath_month'].values).zfill(2)}-{str(data2['swath_day'].values).zfill(2)} at {str(data2['swath_hour'].values).zfill(2)}{str(data2['swath_min'].values).zfill(2)}z'
    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar Tilt Change Diagnostic Plot\n{data1['storm_name'].values} {data1['swath_year'].values}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date1} to {date2}', fontsize=10, loc='center')
    axes[0].set_title(f'{tilt[-1] - tilt[0]}\nDeelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons1, lats1, data1['swath_reflectivity'].sel(height = 3).values, cmap = cmap.reflectivity(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    axes[1].scatter(clon1, clat1, color = 'black', edgecolors = 'white', transform=ccrs.PlateCarree(central_longitude=0), path_effects=[pe.withStroke(linewidth = 1, foreground="white")])

    cv = axes[2].pcolormesh(lons1, lats1, np.nanmean(data1['swath_upward_air_velocity'].sel(height = [5, 5.5, 6, 6.5, 7, 7.5, 8]).values, axis = 2), cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].streamplot(lons1, lats1, data1['swath_eastward_wind'].sel(height = 2), data1['swath_northward_wind'].sel(height = 2), linewidth = .5, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[2].streamplot(lons1, lats1, data1['swath_eastward_wind'].sel(height = h[targ[0]]), data1['swath_northward_wind'].sel(height = h[targ[0]]), linewidth = .5, density = 1, color = 'green', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[2].text(0.5, 0.95, f'Vertical Velocity (m/s)\n2km (black), {h[targ[0]]}km (green)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    axes[2].scatter(clon1, clat1, color = 'black', edgecolors = 'white', transform=ccrs.PlateCarree(central_longitude=0))


    cr = axes[3].pcolormesh(lons2, lats2, data2['swath_reflectivity'].sel(height = 3).values, cmap = cmap.reflectivity(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    axes[3].scatter(clon2, clat2, color = 'black', edgecolors = 'white', transform=ccrs.PlateCarree(central_longitude=0), path_effects=[pe.withStroke(linewidth = 1, foreground="white")])

    cv = axes[4].pcolormesh(lons2, lats2, np.nanmean(data2['swath_upward_air_velocity'].sel(height = [5, 5.5, 6, 6.5, 7, 7.5, 8]).values, axis = 2), cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].streamplot(lons2, lats2, data2['swath_eastward_wind'].sel(height = 2), data2['swath_northward_wind'].sel(height = 2), linewidth = .5, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[4].streamplot(lons2, lats2, data2['swath_eastward_wind'].sel(height = h[targ[0]]), data2['swath_northward_wind'].sel(height = h[targ[0]]), linewidth = .5, density = 1, color = 'green', transform = ccrs.PlateCarree(central_longitude = 0))
    axes[4].text(0.5, 0.95, f'Vertical Velocity (m/s)\n2km (black), {h[targ[0]]}km (green)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    axes[4].scatter(clon2, clat2, color = 'black', edgecolors = 'white', transform=ccrs.PlateCarree(central_longitude=0))

    axes[5].set_frame_on(False)
    axes[5].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[5].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[5].set_xlabel(f'Tilt (km)', weight = 'bold', size = 9)
    axes[5].set_ylabel(f'VMax (kts)', weight = 'bold', size = 9)
    axes[5].axvline(color = 'black')
    axes[5].axhline(color = 'black')
    c1 = axes[5].scatter(tilt, vmax, c = np.arange(len(tilt)), cmap = cmap.probs2(), linewidth = 2)
    cbar = plt.colorbar(c1, ax = axes[5], orientation = 'vertical', aspect = 50, pad = .02)


    axes[6].set_frame_on(False)
    axes[6].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[6].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[6].set_xlabel(f'Zonal', weight = 'bold', size = 9)
    axes[6].set_ylabel(f'Meridional', weight = 'bold', size = 9)
    axes[6].axvline(color = 'black')
    axes[6].axhline(color = 'black')
    c2 = axes[6].scatter(u, v, c = np.arange(len(tilt)), cmap = cmap.probs2(), linewidth = 2)
    cbar = plt.colorbar(c2, ax = axes[6], orientation = 'vertical', aspect = 50, pad = .02)

    #plt.savefig(r"C:\Users\deela\Downloads\\tiltDecrease\\" + date1 + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show()

l1 = [(220.0, 225.0), (282.0, 289.0), (311.0, 313.0), (313.0, 316.0), (345.0, 347.0), (375.0, 376.0), (402.0, 403.0), (422.0, 425.0), (425.0, 429.0), (429.0, 432.0), (510.0, 516.0), (545.0, 546.0), (600.0, 603.0)]
l2 = [(43.0, 47.0), (18.0, 23.0), (24.0, 26.0), (26.0, 29.0), (32.0, 35.0), (35.0, 40.0), (56.0, 63.0), (63.0, 66.0), (66.0, 77.0), (89.0, 95.0), (164.0, 166.0), (189.0, 191.0), (201.0, 205.0), (208.0, 211.0), (224.0, 226.0), (226.0, 227.0), (230.0, 233.0), (234.0, 241.0), (245.0, 248.0), (339.0, 341.0), (350.0, 352.0), (352.0, 357.0), (357.0, 363.0), (436.0, 439.0), (464.0, 467.0), (485.0, 488.0), (512.0, 516.0), (586.0, 600.0), (600.0, 611.0), (613.0, 626.0)]

l3 = [(220.0, 222.0), (223.0, 227.0), (283.0, 292.0), (333.0, 335.0), (345.0, 349.0), (374.0, 376.0), (376.0, 379.0), (403.0, 408.0), (413.0, 418.0), (427.0, 433.0), (601.0, 604.0), (604.0, 606.0)]
l4 = [(42.0, 46.0), (11.0, 13.0), (29.0, 32.0), (36.0, 38.0), (55.0, 59.0), (63.0, 68.0), (84.0, 91.0), (164.0, 170.0), (186.0, 191.0), (197.0, 200.0), (205.0, 208.0), (227.0, 229.0), (229.0, 239.0), (246.0, 251.0), (258.0, 265.0), (341.0, 347.0), (347.0, 349.0), (354.0, 361.0), (363.0, 375.0), (391.0, 393.0), (418.0, 420.0), (420.0, 423.0), (437.0, 441.0), (464.0, 466.0), (466.0, 471.0), (487.0, 490.0), (490.0, 494.0), (510.0, 517.0), (517.0, 520.0), (591.0, 600.0), (614.0, 623.0)]

l = l3
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
print(list(dataset.variables))
for x in range(len(l)):
    panelPlot(dataset, l[x][0], l[x][1])

l = l4
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")
for x in range(len(l)):
    panelPlot(dataset, l[x][0], l[x][1])