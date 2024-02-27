import xarray as xr 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
import satcmaps as cmaps
import cmaps as cmp 
import image_retrieval as ir
import numpy as np 
from datetime import datetime 
from pyproj import Proj 
import scipy 

ir.getDataGOES('16', 2017, 9, 5, '2230', '13')

data = xr.open_dataset(r"C:\Users\deela\Downloads\goesfile.nc")
center = data['geospatial_lat_lon_extent'].geospatial_lon_center
time = (data.time_coverage_start).split('T')
time = f"{time[0]} at {time[1][:5]} UTC"

# Define Reproject
def reproject(data):    
    # Scan time
    midpoint = str(data['t'].data)[:-8]
    scan_mid = datetime.strptime(midpoint, '%Y-%m-%dT%H:%M:%S.%f')
    
    # Load the 4 channels and convert to Celsius
    IR = data['CMI'].data - 273.15 

    # Satellite Parameters
    sat_h = data['goes_imager_projection'].perspective_point_height
    sat_lon = data['goes_imager_projection'].longitude_of_projection_origin
    sat_sweep = data['goes_imager_projection'].sweep_angle_axis

    # The projection x and y coordinates equals the scanning angle (in radians) multiplied by the satellite height
    # See details here: https://proj4.org/operations/projections/geos.html?highlight=geostationary
    x = data['x'][:] * sat_h
    y = data['y'][:] * sat_h

    # Create a Geostationary projection
    geos_proj = ccrs.Geostationary(central_longitude=sat_lon, satellite_height=sat_h)
    
    # Create a pyproj geostationary map object
    p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep)

    # Perform cartographic transformation. That is, convert image projection coordinates (x and y)
    # to latitude and longitude values.
    XX, YY = np.meshgrid(x, y)
    lons, lats = p(XX, YY, inverse=True)
    lons = np.nan_to_num(lons, posinf=center)
    lats = np.nan_to_num(lats, posinf=-79)

    extent = data.variables['geospatial_lat_lon_extent']
    minimglat = extent.attrs['geospatial_southbound_latitude']
    maximglat = extent.attrs['geospatial_northbound_latitude']
    minimglon = extent.attrs['geospatial_westbound_longitude']
    maximglon = extent.attrs['geospatial_eastbound_longitude']
    res = 0.0179985  # degrees resolution at nadir
    grid = np.meshgrid(np.arange(minimglat, maximglat, res), np.arange(minimglon, maximglon, res))

    lats = lats.flatten()
    lons = lons.flatten()
    IR = IR.flatten()

    floater = (np.greater(lats, minimglat) & np.greater(maximglat, lats) &
               np.greater(lons, minimglon) & np.greater(maximglon, lons) & np.isfinite(IR))

    temps_grid_IR = scipy.interpolate.griddata((lats[floater], lons[floater]), IR[floater], (grid[0], grid[1]))
    
    latitude = np.arange(minimglat, maximglat, res)
    longitude = np.arange(minimglon, maximglon, res)
    temps_grid_IR = np.transpose(temps_grid_IR)
    
    return latitude, longitude, temps_grid_IR

    # Create a new xarray dataset with latitude and longitude coordinates
    new_data = xr.Dataset(
        {'IR': (['y', 'x'], IR)},
        coords={'latitude': (['y', 'x'], lats), 'longitude': (['y', 'x'], lons),
        'file_time': scan_mid}
    )

    return new_data['IR']

def stormir(data, lon, lat, cmap = 'irg'):
    plt.figure(figsize = (18, 9))

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    #ax.set_extent(loc, crs=ccrs.PlateCarree())

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False    
    cmap, vmax, vmin = cmaps.irtables[cmap]
    print(data)

    plt.pcolormesh(data.longitude, data.latitude, data, vmin = vmin, vmax = vmax, cmap = cmap)
    plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    plt.title(f'GOES-16 Channel 13 Brightness Temperature\nSatellite Image: {time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\deela\Downloads\stormir.png", dpi = 250, bbox_inches = 'tight')
    plt.show()
    plt.close()

data = reproject(data)
stormir(data, -60, 17)