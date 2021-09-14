import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy as np
import matplotlib.patches as mpatches
import rapRetrieve as rr
import cmaps as cmap

# Three functions for charts made using RAP data

# Plots dewpoint depression and 1000mb winds along side mean sea level pressure contours
def rapdew():
    data = rr.retrieveData(["mslmamsl", "ugrdprs", "vgrdprs", 'depr2m'])

    time = (data[0]['time'].values)
    time = str(time).split("T")
    time = f"{time[0]} at {time[1][:8]}"

    ax = rr.map(-130, -65, 20, 51, (20, 8.75))
    value1 = data[0] / 100
    value2 = data[3]
    uwn = data[1].sel(lev = 1000) * 1.944
    vwn = data[2].sel(lev = 1000) * 1.944

    extent = [min(data[1].lon), max(data[1].lon), min(data[1].lat), max(data[1].lat)]

    plt.contour(data[1].lon, data[1].lat, value1, levels = np.arange(993, 1033, 2), linewidths = 2, cmap = "seismic_r")
    plt.contourf(data[1].lon, data[1].lat, value2, levels = np.arange(0, 30, 0.5), extend = 'max', cmap = cmap.cmap('Greens_r', 64, 'pink_r', 128))
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02, extendrect = True, label = f'Dewpoint Depression (°C)')

    uwn = (uwn)[::8, ::8]
    vwn = (vwn)[::8, ::8]
    plt.quiver(uwn.lon, vwn.lat, uwn.values, vwn.values, color = 'black', zorder = 10)
        
    plt.title(f'RAP 1000mb Winds (arrows), Sea Level Pressure (contours), Dewpoint Depression (fill)\n{time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'TCAlert', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\Username\Downloads\rap.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()
    
# Plots CIN, CAPE, and winds at the 500, 850, and 1000mb levels.
def rapcape():
    data = rr.retrieveData(["cinsfc", "capesfc", "ugrdprs", "vgrdprs"])

    time = (data[0]['time'].values)
    time = str(time).split("T")
    time = f"{time[0]} at {time[1][:8]}"

    ax = rr.map(-130, -65, 20, 51, (20, 8.75))

    mask_lon = (data[1].lon >= -130) & (data[1].lon <= -65)
    mask_lat = (data[1].lat >= 20) & (data[1].lat < 61)
    data[1] = data[1].where(mask_lon & mask_lat, drop=True)

    plt.contourf(data[1].lon, data[1].lat, data[1].values, levels = np.arange(np.nanmin(data[1].values), np.nanmax(data[1].values) + 1), cmap = "RdGy_r")
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    c = plt.contour(data[0].lon, data[0].lat, data[0].values, levels = np.arange(np.nanmin(data[0].values), 0, 100), colors = "royalblue")
    plt.clabel(c, fontsize = 10, inline = 1, fmt = '%1.0f')

    maxi = data[1].where(data[1]==data[1].max(), drop=True).squeeze()

    plt.scatter(maxi['lon'], maxi['lat'], s = 50, edgecolor = 'gray', color = 'black')

    levels = [500, 850, 1000]
    colors = ['darkorchid', 'seagreen', 'coral']

    handles = []
    for x in range(len(levels)):
        uwn = data[2].sel(lev = levels[x])
        vwn = data[3].sel(lev = levels[x])

        uwn = (uwn)[::16, ::16]
        vwn = (vwn)[::16, ::16]
        plt.quiver(uwn.lon, vwn.lat, uwn.values, vwn.values, color = colors[x])

        handles.append(mpatches.Patch(color = colors[x], label = f"{str(levels[x])}mb"))
        
    plt.legend(handles = handles)  
    plt.title(f'RAP Surface CAPE (fill) and CINH (contour) - Arrows Depicting Wind per Legend\n{time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'TCAlert\nHighest CAPE: {str(maxi.values)}', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\Username\Downloads\rap.png", dpi = 250, bbox_inches = 'tight')
    plt.show()
    plt.close()

# Plots absolute vorticity, geopotential height, and winds at 500mb, along with preciptable water
def rapup():
    data = rr.retrieveData(["absv500mb", "hgtprs", "ugrdprs", "vgrdprs", 'pwatclm'])

    time = (data[0]['time'].values)
    time = str(time).split("T")
    time = f"{time[0]} at {time[1][:8]}"

    ax = rr.map(-130, -65, 20, 51, (20, 8.75))

    value1 = data[1].sel(lev = 500) / 10
    value2 = data[0] * 100000  
    value3 = data[4]  
    extent = [min(data[1].lon), max(data[1].lon), min(data[1].lat), max(data[1].lat)]

    plt.contour(data[1].lon, data[1].lat, value1, levels = np.arange(np.nanmin(value1), np.nanmax(value1) + 1, 10), colors = "black")
    plt.contourf(data[1].lon, data[1].lat, value3, levels = np.arange(20, 50, 1), extend = 'max', cmap = "summer_r")
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02, extendrect = True, label = 'PWAT')
    plt.contour(data[1].lon, data[1].lat, value3, levels = [50], colors = "white")
    plt.contourf(data[1].lon, data[1].lat, value2, extent = extent, origin = 'lower', extend = 'max', levels = np.arange(10, 40, 1), cmap = 'autumn_r', transform = ccrs.PlateCarree(central_longitude = 0))

    uwn = data[2].sel(lev = '500')
    vwn = data[3].sel(lev = '500')
    uwn = (uwn)[::8, ::8]
    vwn = (vwn)[::8, ::8]
    plt.quiver(uwn.lon, vwn.lat, uwn.values, vwn.values, color = 'darkolivegreen', zorder = 10)
        
    plt.title(f'RAP 500mb Vorticity, Geopotential Height, Winds + Precipitable Water (50 kg/m^2 in white)\n{time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'TCAlert', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\Username\Downloads\rap.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()
