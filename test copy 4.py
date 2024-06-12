import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
from matplotlib import rcParams
import numpy as np 
import matplotlib.patheffects as pe
rcParams['font.family'] = 'Courier New'

def map(interval, labelsize):
    fig = plt.figure(figsize=(14, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', which = 'major', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

REGIONS = {'NATL' : ([-100, -10, 0, 65], (18, 9)),
           'WATL' : ([-100, -50, 2.5, 35], (18, 9)),
           'EATL' : ([-60, 0, -10, 30], (18, 9)),
           'SATL1' : ([-50, -10, -10, -40], (18, 9)),
           'SATL2' : ([-70, -30, -35, -65], (18, 9)),
           'MDR'  : ([-65, -15, 5, 27.5], (16, 6)),
           'US'   : ([-130, -60, 20, 60], (18, 9)),
           'WUS'  : ([-140, -100, 25, 57.5], (18, 9)),
           'SAMS' : ([-90, -30, -25, -65], (18, 9)),
           'SAMN' : ([-90, -30, 15, -25], (18, 9)),
           'NWATL': ([-85, -45, 25, 60], (18, 9)),
           'NEATL': ([-50, -10, 25, 60], (18, 9)),
           'SWATL': ([-95, -55, 10, 45], (18, 9)),
           'SEATL': ([-50, -10, 10, 45], (18, 9)),
           'CAG'  : ([-100, -70, 5, 30], (18, 9)),
           'CAR'  : ([-90, -55, 5, 26], (18, 9)),
           'GOM'  : ([-100, -75, 15, 32.5], (18, 9)),
           'EPAC' : ([-140, -80, 0, 30], (16, 6)),
           'CPAC' : ([-179, -119, 0, 30], (16, 6)),
           'NPAC' : ([-189, -99, 20, 70], (24, 8)),
           'NPAC2': ([110, 200, 20, 70], (24, 8)),
           'TPAC' : ([-179, -79, 0, 50], (16, 6)),
           'WPAC' : ([105, 170, 0, 45], (18, 9)),
           'WMDR' : ([110, 160, 5, 27.5], (16, 6)),
           'PHIL' : ([105, 140, 5, 26], (16, 6)),
           'AUS'  : ([100, 165, -45, 0], (18, 9)),
           'SPAC' : ([139, 199, -45, 0], (18, 9)),
           'SCPAC': ([-189, -129, -45, 0], (18, 9)),
           'SEPAC': ([-159, -79, -45, 0], (18, 9)),
           'ENSO' : ([-189, -79, -25, 25], (16, 6)),
           'EQ' : ([69, 179, -25, 25], (16, 6))}

def box(boxXCoords, boxYCoords, name):
    try:
        for y in range(len(boxXCoords)):
            try:
                ax.plot([boxXCoords[y], boxXCoords[y + 1]], [boxYCoords[y], boxYCoords[y + 1]], color = 'black', zorder = 20, transform = ccrs.PlateCarree(central_longitude = 360))
            except:
                pass
        textX, textY = ((boxXCoords[0] + boxXCoords[1]) / 2, (boxYCoords[0] + boxYCoords[2]) / 2)
        ax.text(textX, textY, name.upper(), color = 'black', size = 15, horizontalalignment = 'center', verticalalignment = 'center', zorder = 30, path_effects = [pe.withStroke(linewidth = .5, foreground="black")], transform = ccrs.PlateCarree(central_longitude = 360))
    except:
       pass
    print(name + " done!")

ax = map(20, 9)
keys = list(REGIONS.keys())
for x in range(len(REGIONS.keys())):
    extent, size = REGIONS[keys[x]]
    lats = [extent[2], extent[3]]
    lons = [extent[0], extent[1]]
    boxXCoords = [lons[0], lons[1], lons[1], lons[0], lons[0]]
    boxYCoords = [lats[0], lats[0], lats[1], lats[1], lats[0]]

    box(boxXCoords, boxYCoords, keys[x])

ax.set_title(f'Available Regions in Cyclobot\nAs of 5/30/2024', fontweight='bold', fontsize=11, loc='left')
ax.set_title(f'Deelan Jariwala', fontsize=10, loc='right') 
plt.savefig(r"C:\Users\deela\Downloads\regions.png", dpi = 400, bbox_inches = 'tight')
plt.show()
