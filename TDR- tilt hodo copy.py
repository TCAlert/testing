import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import numpy as np 
import cmaps as cmap 

def setUpHodo(max, meanU, meanV):
    fig = plt.figure(figsize=(10, 8))

    ax = plt.axes()
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_frame_on(False)
    ax.grid(linewidth = 0.5, color = 'black', alpha = 0.5, linestyle = '--', zorder = 10)
    ax.axvline(x = 0, c = 'black', zorder = 0)
    ax.axhline(y = 0, c = 'black', zorder = 0)

    if max > 50:
        interval = 10
    elif max > 100:
        interval = 20
    else:
        interval = 5
    max = int(max + interval * 7)
    remainder = max % interval
    max = max - remainder

    for x in range(interval, max + interval, interval):
        c = plt.Circle((0, 0), radius = x, facecolor = "None", edgecolor = '#404040', linestyle = '--')
        ax.add_patch(c)

    ax.set_xlim(meanU - (max / 2), meanU + (max / 2))
    ax.set_ylim(meanV - (max / 2), meanV + (max / 2))

    return ax

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")

print(list(dataset.variables.keys()))

ax = setUpHodo(25, 15, -10)

name = 'Hermine'
year = 2016
for x in range(413, 419):
    data = dataset.sel(num_cases = x)
    date = f'{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)} at {str(data['swath_hour'].values).zfill(2)}{str(data['swath_min'].values).zfill(2)}z'
    uData, vData = data['tc_zonal_tilt'], data['tc_meridional_tilt']
    print(uData.values, vData.values)
    colors = cmap.probs2()((x - 413) / 5)#[cmap.probs()(uData.level[l + 1] / 10) for l in range(len(uData.level) - 1)]
    c = ax.scatter(uData, vData, c = [x for _ in range(0, 37)], linewidth = .5, vmin = 413, vmax = 418, cmap = cmap.probs2(), zorder = 6)
    ax.scatter(uData, vData, linewidth = .5, vmin = 413, vmax = 418, color = colors, zorder = 12)
    ax.plot(uData, vData, linewidth = 3, color = colors, zorder = 11)

ax.set_title(f'TC-RADAR: Derived Tilt Hodograph ({name} 2016)\n{date}', fontweight='bold', fontsize=9, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=9, loc='right') 

cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)    
cbar.set_label('Case #')
#cbar.ax.invert_yaxis()
plt.savefig(r"C:\Users\deela\Downloads\tdrhodo.png", dpi = 400, bbox_inches = 'tight')
plt.show() 
plt.close()
