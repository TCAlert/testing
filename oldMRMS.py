import matplotlib.pyplot as plt 
import cartopy, cartopy.crs as ccrs
import cmaps as cmap 
import xarray as xr
from datetime import datetime
import bdeck as bdeck 

usage = '```$mrms [storm (best track ID)/latitude] [longitude]```'

def plot(lat, lon = 0):
    link = f'https://thredds.aos.wisc.edu/thredds/dodsC/grib/NCEP/MRMS/BaseRef/MRMS_BaseReflectivity_{datetime.utcnow().year}{str(datetime.utcnow().month).zfill(2)}{str(datetime.utcnow().day).zfill(2)}_{str(datetime.utcnow().hour).zfill(2)}00.grib2'
    data = xr.open_dataset(link)

    mrms = data['MergedBaseReflectivityQC_altitude_above_msl'].sel(time = data['time'][-1], altitude_above_msl = data['altitude_above_msl'][0])

    plt.figure(figsize=(18, 9))
    
    #print('Plotting...')

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))

    try:
        lat = float(lat)
        lon = float(lon)
        title = f'Centered at {lat}N, {abs(lon)}W'
        lon += 360
        extent = [lon - 1, lon + 1, lat - 1, lat + 1]
    except:
        storm = lat
        lat, lon = bdeck.latlon(storm)
        title = storm.upper()
        extent = [lon - 2.5, lon + 2.5, lat - 2.5, lat + 2.5]

    mrms = mrms.where((mrms.lon > extent[0]) & (mrms.lon < extent[1]) & (mrms.lat > extent[2]) & (mrms.lat < extent[3]), drop = True)

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='white', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5) 
    ax.add_feature(cartopy.feature.STATES.with_scale('10m'), edgecolor='white', linewidth=0.5) 
    ax.add_feature(cartopy.feature.LAND, facecolor='#242424', linewidth=0.5) 
    ax.add_feature(cartopy.feature.OCEAN, facecolor='#242424', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    plt.pcolormesh(mrms.lon, mrms.lat, mrms.values, cmap = cmap.ref(), vmin = 0, vmax = 75, transform=ccrs.PlateCarree(central_longitude = 0))

    t = str(data['time'][-1].values).split('T')
    time = f'{t[0]} at {t[1][0:5]}z'

    plt.title(f'MRMS Base Reflectivity\n{time}', fontweight='bold', fontsize=10, loc='left')
    plt.title(f'{title}\nDeelan Jariwala', fontsize=10, loc='right') 
    
    #print('Plotting complete!')
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.savefig(r"C:\Users\deela\Downloads\mrmsradar.png", dpi = 250, bbox_inches = 'tight')
    plt.show()
    plt.close()
plot(34.822, -98.757)
