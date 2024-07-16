import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 

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

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")
#dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_2020_2022_xy_rel_swath_ships.nc")

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
    data = dataset.sel(level = 3)
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
    
    lats = data['original_latitudes']
    lons = data['original_longitudes']
    date = f'{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)} at {str(data['swath_hour'].values).zfill(2)}{str(data['swath_min'].values).zfill(2)}z'
    axes[0].set_title(f'TC-RADAR: Tail Doppler Radar {height}km Diagnostic Plot\n{name} {year}', fontweight='bold', fontsize=10, loc='left')
    axes[0].set_title(f'{date} (Case #{int(caseNum)})', fontsize=10, loc='center')
    axes[0].set_title(f'Deelan Jariwala', fontsize=10, loc='right') 

    cr = axes[1].pcolormesh(lons, lats, data['swath_reflectivity'].values, cmap = cmap.reflectivity(), vmin = 0, vmax = 50, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cr, ax = axes[1], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[1].text(0.5, 0.95, 'Reflectivity (dBZ)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[1].transAxes)
    
    cw = axes[2].pcolormesh(lons, lats, data['swath_wind_speed'].values * 1.94384, cmap = cmap.wind(), vmin = 0, vmax = 160, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cw, ax = axes[2], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[2].text(0.5, 0.95, 'Wind Speed (kt)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[2].transAxes)
    
    cv = axes[3].pcolormesh(lons, lats, data['swath_vertical_velocity'].values, cmap = cmap.tempAnoms3(), vmin = -5, vmax = 5, transform=ccrs.PlateCarree(central_longitude=0))
    cbar = plt.colorbar(cv, ax = axes[3], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[3].text(0.5, 0.95, 'Vertical Velocity (m/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[3].transAxes)
    
    vc = axes[4].pcolormesh(lons, lats, data['swath_relative_vorticity'].values, cmap = cmap.probs(), vmin = 0, vmax = 0.005, transform=ccrs.PlateCarree(central_longitude=0))
    axes[4].streamplot(lons, lats, data['swath_zonal_wind'].values, data['swath_meridional_wind'].values, linewidth = 1, density = 1, color = 'black', transform = ccrs.PlateCarree(central_longitude = 0))
    cbar = plt.colorbar(vc, ax = axes[4], orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    axes[4].text(0.5, 0.95, 'Relative Vorticity (1/s)', fontweight = 'bold', fontsize = 8, horizontalalignment='center', verticalalignment='center', transform = axes[4].transAxes)
    
    plt.savefig(r"C:\Users\deela\Downloads\TDR_Swaths\\" + date + ".png", dpi = 400, bbox_inches = 'tight')
    #plt.show()
name = 'Irma'
year = 2017
height = 3
data = retrieveStorm(name, year)
print(data.num_cases.values)
refl = data['swath_wind_speed'].sel(level = height) * 1.94384

ax = map(2, 9)
#ax.set_extent([-120, 0, 0, 60])
for x in range(len(refl.num_cases)):
    case = refl.num_cases[x].values
    panelPlot(data.sel(num_cases = case), case)
    temp = refl.sel(num_cases = refl.num_cases[x])
    lats = data['original_latitudes'].sel(num_cases = refl.num_cases[x])
    lons = data['original_longitudes'].sel(num_cases = refl.num_cases[x])
    c = plt.pcolormesh(lons, lats, temp.values, cmap = cmap.wind(), vmin = 0, vmax = 160, transform=ccrs.PlateCarree(central_longitude=0))
ax.set_title(f'TC-RADAR: Tail Doppler Radar {height}km Reflectivity\n{name} {year}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cbar.ax.tick_params(axis='both', labelsize=9, left = False, bottom = False)
cbar.set_ticks(np.arange(0, 170, 10))
plt.savefig(r"C:\Users\deela\Downloads\tdrtest.png", dpi = 400, bbox_inches = 'tight')
plt.show()