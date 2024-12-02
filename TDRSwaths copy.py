import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 
import helper 

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

#dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")

print(list(dataset.variables.keys()))

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
    tilt = np.nanmax(dataset['tc_tilt_magnitude'].sel(num_cases = slice(startCase, endCase), height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
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
        axes[x] = spmap(axes[x], .5, 8)
    
    lats1, lats2 = data1['original_latitudes'], data2['original_latitudes']
    lons1, lons2 = data1['original_longitudes'], data2['original_longitudes']
    date1 = f'{str(data1['swath_year'].values)}-{str(data1['swath_month'].values).zfill(2)}-{str(data1['swath_day'].values).zfill(2)} at {str(data1['swath_hour'].values).zfill(2)}{str(data1['swath_min'].values).zfill(2)}z'
    date2 = f'{str(data2['swath_year'].values)}-{str(data2['swath_month'].values).zfill(2)}-{str(data2['swath_day'].values).zfill(2)} at {str(data2['swath_hour'].values).zfill(2)}{str(data2['swath_min'].values).zfill(2)}z'
    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar Tilt Change Diagnostic Plot\n{data1['storm_name'].values} {data1['swath_year'].values}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date1} to {date2}', fontsize=10, loc='center')
    axes[0].set_title(f'{tilt[0] - tilt[-1]}\nDeelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons1, lats1, data1['swath_reflectivity'].sel(height = 3).values, cmap = cmap.reflectivity(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    
    print(data1['swath_upward_air_velocity'].sel(height = [5, 5.5, 6, 6.5, 7, 7.5, 8]))

    cv = axes[2].pcolormesh(lons1, lats1, np.nanmean(data1['swath_upward_air_velocity'].sel(height = [5, 5.5, 6, 6.5, 7, 7.5, 8]).values, axis = 2), cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, 'Vertical Velocity (m/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    
    cr = axes[3].pcolormesh(lons2, lats2, data2['swath_reflectivity'].sel(height = 3).values, cmap = cmap.reflectivity(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)

    cv = axes[4].pcolormesh(lons2, lats2, np.nanmean(data2['swath_upward_air_velocity'].sel(height = [5, 5.5, 6, 6.5, 7, 7.5, 8]).values, axis = 2), cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Vertical Velocity (m/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    

    axes[5].set_frame_on(False)
    axes[5].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[5].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[5].set_xlabel(f'Tilt (km)', weight = 'bold', size = 9)
    axes[5].set_ylabel(f'VMax (kts)', weight = 'bold', size = 9)
    axes[5].axvline(color = 'black')
    axes[5].axhline(color = 'black')
    axes[5].scatter(tilt, vmax, c = 'black', linewidth = 2)


    axes[6].set_frame_on(False)
    axes[6].tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[6].grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    axes[6].set_xlabel(f'Zonal', weight = 'bold', size = 9)
    axes[6].set_ylabel(f'Meridional', weight = 'bold', size = 9)
    axes[6].axvline(color = 'black')
    axes[6].axhline(color = 'black')
    axes[6].scatter(u, v, c = 'black', linewidth = 2)

    plt.savefig(r"C:\Users\deela\Downloads\\tiltDecrease\\" + date1 + ".png", dpi = 400, bbox_inches = 'tight')
    #plt.show()

l1 = [(13.0, 15.0), (18.0, 26.0), (26.0, 29.0), (32.0, 35.0), (37.0, 40.0), (58.0, 63.0), (64.0, 65.0), (67.0, 77.0), (123.0, 126.0), (164.0, 168.0), (201.0, 205.0), (208.0, 211.0), (224.0, 226.0), (226.0, 227.0), (236.0, 242.0), (266.0, 272.0), (339.0, 341.0), (349.0, 352.0), (358.0, 363.0), (392.0, 393.0), (423.0, 426.0), (458.0, 461.0), (464.0, 467.0), (471.0, 474.0), (474.0, 477.0), (484.0, 488.0), (499.0, 506.0), (512.0, 516.0), (520.0, 524.0), (587.0, 599.0), (599.0, 611.0)]
l2 = [(10.0, 13.0), (19.0, 22.0), (29.0, 32.0), (35.0, 39.0), (55.0, 58.0), (61.0, 68.0), (84.0, 91.0), (91.0, 97.0), (164.0, 170.0), (186.0, 189.0), (197.0, 200.0), (205.0, 208.0), (209.0, 214.0), (227.0, 229.0), (229.0, 232.0), (232.0, 236.0), (245.0, 251.0), (255.0, 264.0), (341.0, 347.0), (347.0, 349.0), (351.0, 361.0), (363.0, 373.0), (391.0, 393.0), (418.0, 420.0), (420.0, 423.0), (436.0, 441.0), (464.0, 466.0), (466.0, 471.0), (487.0, 490.0), (490.0, 494.0), (510.0, 516.0), (516.0, 519.0), (586.0, 597.0), (611.0, 623.0)]

l = l2
for x in range(len(l)):
    panelPlot(dataset, l[x][0], l[x][1])
