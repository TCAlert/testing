import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
import cmaps as cmaps 
from cartopy.mpl.ticker import LongitudeFormatter
import cartopy.crs as ccrs
import psl
import cartopy.feature as cfeature
from helper import months 
month = 3
years = [1988]

# Plot velocity potential data
def smallPlot(ax, veloPot):
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 1)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 1)
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), zorder = 9, draw_labels = True, linewidth = 0.5, color='gray', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
    gl.xlabels_top = gl.ylabels_right = False 

    ax.set_extent([60, 300, -10, 10], crs = ccrs.PlateCarree())
    c1 = ax.contourf(veloPot.lon, veloPot.lat, veloPot.values, levels = np.arange(-10000000, 11000000, 500000), cmap = 'BrBG_r', extend = 'both', transform = ccrs.PlateCarree(central_longitude=0))
    plt.colorbar(c1, orientation = 'vertical', aspect = 25, pad = .02, ax = axes[1])
    #If I could, I'd throw irrotational wind vectors here

# Plots vertical velocity both as filled contorus and as a vector along with the zonal component of motion
# Also cleans up the plot a little bit
def bigPlot(ax, vvel, uwnd):
    ax.grid(linewidth = 1, color='gray', alpha=0.5, linestyle='--')
    print(vvel)

    c = ax.contourf(vvel.lon, vvel.lev, vvel.values, cmap = cmaps.tempAnoms(), levels = np.arange(-50, 52.5, 2.5), extend = 'both')
    plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02, ax = axes[0])
    ax.quiver(vvel.lon, vvel.lev, uwnd.values, vvel.values * -1)

    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.set_xticks([60, 120, 180, 240, 300])
    ax.set_xticklabels(['', '', '', '', ''])
    ax.set_xlim(60, 300)
    
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_yticks([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    ax.set_yticklabels(['100mb', '200mb', '300mb', '400mb', '500mb', '600mb', '700mb', '800mb', '900mb', '1000mb'])
    ax.set_ylim(1025, 100)

# Retrieves all of the data needed to make this plot from PSL
# Dataset is the NCEP/NCAR Reanalysis I with a 2.5 degree resolution
# Averages it over tropical latitudes as well as time (the latter of which is done in the createClimoMonthly function) 
def getData(year):
    data = psl.createClimoMonthly(year, str(month).zfill(2), ['omega', 'uwnd'], [False, False])
    for x in range(len(data)):
        data[x] = data[x].sel(lat = slice(10, -10), level = [100, 200, 300, 400, 500, 600, 700, 850, 925, 1000])
        data[x] = data[x].mean(['lat'])
        data[x] = data[x].rename({'level' : 'lev'})
    veloPot = psl.createClimoMonthly(year, str(month).zfill(2), ['chi'], [True])
    veloPot = veloPot[0].sel(lat = slice(15, -15), level = .2101)
    data.append(veloPot.rename({'level' : 'lev'}))

    data[0] = data[0] * 500
    return data

# Calculate anomaly data
data = getData(years)
climoData = getData(range(1991, 2021))
for x in range(len(data)):
    data[x].values = data[x].values - climoData[x].values

# Create plots, one for VVel data and one for VP200
# Add titles and save to computer
fig = plt.figure(figsize=(18, 8))
gs = fig.add_gridspec(2, 1, height_ratios=[5, 1], hspace=0.03)

axes = [fig.add_subplot(gs[0, 0]), 
        fig.add_subplot(gs[1, 0], projection = ccrs.PlateCarree(central_longitude=180))]

smallPlot(axes[1], data[2])
bigPlot(axes[0], data[0], data[1])

axes[0].set_title(f'NCEP/NCAR Reanalysis I: Vertical Velocity (Top) and VP200 (Bottom) Anomalies\nVV Data Upscaled by 500x', fontweight='bold', fontsize=10, loc='left')
axes[0].set_title(f'{months[month]} {str(years)[1:-1]}', fontsize = 10, loc = 'center')
axes[0].set_title('Deelan Jariwala\nClimatology: 1991-2020', fontsize=10, loc='right') 
plt.savefig(r"C:\Users\[Username]\Downloads\vpprof.png", dpi = 400, bbox_inches = 'tight')
plt.show() 
