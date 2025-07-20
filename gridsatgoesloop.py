import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import satcmaps as cmaps
import cmaps as cmp 
import image_retrieval as ir
import numpy as np 
import cartopy.feature as cfeature
from pyproj import Proj 
import scipy 
import random 
from helper import REGIONS

def map(lon, lat, zoom = 2, center = 0):
    try:
        zoom = int(zoom)
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))
    
        if zoom == 1:
            ax.set_extent([lon - 5, lon + 5, lat - 5, lat + 5], crs=ccrs.PlateCarree())
        elif zoom == 3:
            ax.set_extent([lon - 15, lon + 15, lat - 15, lat + 15], crs=ccrs.PlateCarree())
        elif zoom == 2:
            ax.set_extent([lon - 7.5, lon + 7.5, lat - 7.5, lat + 7.5], crs=ccrs.PlateCarree())
    except:
        extent, size = REGIONS[zoom.upper()]
        plt.figure(figsize = size)
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))

        ax.set_extent(extent, crs = ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.75)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)  
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False

def run(satellite, date, time, lat, lon, band, cmp = None, zoom = 2, num = 0):
    date = date.split('/')

    filename = ir.getDataGridsatGOES(satellite, int(date[2]), int(date[0]), int(date[1]), time)
    
    dataset = xr.open_dataset(r"C:\Users\deela\Downloads\\" + filename + ".nc")
    data = dataset[f'ch{band}'].squeeze()
    center = dataset['satlon'].values[0]
    time = str(dataset.time.values[0]).split('T')
    time = f"{time[0]} at {time[1][:5]} UTC"

    ch = band
    repo = False
    res = '4km'
    satellite = f'GRIDSAT GOES-{satellite}'
    
    if band == '3':
        try:
            if cmp.lower() == 'random':
                rand = random.randrange(0, len(cmaps.wvtables.keys()), 1)
                cmp = list(cmaps.wvtables.keys())[rand]
        
            cmap, vmax, vmin = cmaps.wvtables[cmp.lower()]
        except:
            try:
                cmap, vmax, vmin = cmaps.irtables[cmp]
                vmax = 0
                vmin = -90
            except:
                if cmp == None:
                    cmap, vmax, vmin = cmaps.wvtables['wv']
                else:
                    cmap, vmax, vmin = cmp, 0, -90    
    elif band == '4':
        try:
            if cmp.lower() == 'random':
                rand = random.randrange(0, len(cmaps.irtables.keys()), 1)
                cmp = list(cmaps.irtables.keys())[rand]
        
            cmap, vmax, vmin = cmaps.irtables[cmp.lower()]
        except:
            try:
                cmap, vmax, vmin = cmaps.wvtables[cmp]
                vmax = 40
                vmin = -100
            except:
                if cmp == None:
                    cmap, vmax, vmin = cmaps.irtables['irg']
                else:
                    cmap, vmax, vmin = cmp, 40, -110        

    print(cmp, vmin, vmax)

    try:
        if zoom.lower() in ['spac', 'scpac', 'enso', 'npac', 'npac2'] or (float(lon) < 196 and float(lon) > 164) or (float(lon) < -164 and float(lon) > -196):
            map(float(lon), float(lat), zoom, 180)
        else:
            map(float(lon), float(lat), zoom)
    except:
        map(float(lon), float(lat), zoom)

    if repo == True:
        plt.imshow(data - 273, origin = 'upper', transform = ccrs.Geostationary(central_longitude = center, satellite_height=35786023.0), vmin = vmin, vmax = vmax, cmap = cmap)
    else:
        if zoom.lower() in ['spac', 'scpac', 'enso', 'npac', 'npac2'] or (float(lon) < 190 and float(lon) > 170) or (float(lon) < -164 and float(lon) > -196):
            print(lon)
            plt.pcolormesh(data.lon, data.lat, data.values - 273, vmin = vmin, vmax = vmax, cmap = cmap, transform = ccrs.PlateCarree(central_longitude = 0))
        else:
            plt.pcolormesh(data.lon, data.lat, data.values - 273, vmin = vmin, vmax = vmax, cmap = cmap)
    cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    cbar.set_label(cmp.upper())
    plt.title(f'{satellite} Channel {ch.zfill(2)} Brightness Temperature\nTime: {time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{res}\nDeelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\goesloop\\25sept_" + str(counter) + ".png", dpi = 150, bbox_inches = 'tight')
    #plt.show()
    plt.close()
    dataset.close()

    return filename

counter = 0
for x in range(3, 5, 1):
    for y in range(0, 24, 1):
        try:
            counter = counter + 1
            run(8, f"10/{str(x)}/1995", f"{str(y).zfill(2)}00", "0", "0", "3", "wv13", 'gom', counter)
        except:
            pass