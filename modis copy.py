import numpy as np
from netCDF4 import Dataset
import scipy 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import satcmaps as cmaps 
labelsize = 9

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
        plt.figure(figsize = (18, 9))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))

    # Add coastlines, borders and gridlines
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.75)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)  
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.top_labels = gl.right_labels = False

def reproject(dataset, lats, lons, pos):   
    size = 7.5         
                        
    # Extents and interpolation for IR
    minimglat = pos[0] - size
    maximglat = pos[0] + size
    minimglon = pos[1] - size
    maximglon = pos[1] + size
    res = 0.0179985  # degrees resolution at nadir
    grid = np.meshgrid(np.arange(minimglat, maximglat, res), np.arange(minimglon, maximglon, res))
    
    lats = lats.flatten()
    lons = lons.flatten()
    IR = IR.flatten()
    
    # Fix shape issue for boolean conditions
    floater_IR = (np.greater(lats, minimglat) & np.greater(maximglat, lats) &
                    np.greater(lons, minimglon) & np.greater(maximglon, lons) & np.isfinite(IR))

    gridded_data = scipy.interpolate.griddata((lats[floater_IR], lons[floater_IR]), IR[floater_IR], (grid[0], grid[1]), method='cubic')
    
    return grid[1], grid[0], gridded_data


def bT(radiance):
    temp = 1199 / (np.log(477.5 / radiance + 1))

    return temp

file = Dataset(r"C:\Users\deela\Downloads\MYD02QKM.A2003257.1750.061.2018009130113.hdf")
print(file.variables)

data = file.variables['EV_250_RefSB'][:][1].data
lons = file['Longitude'][:].data
lats = file['Latitude'][:].data
satt = 'Aqua'

# if satt == 'Aqua':
#     data = (data - 2035.9332) * 5.71001263e-04
#     data = bT(data) - 273.15
# else:
#     data = (data - 1658.2213) * 7.2969758e-04 #terra
#     data = bT(data) - 273.15
print(data)

data = data**(3/2)


from scipy.ndimage import zoom
from scipy.interpolate import griddata

lats_interp = zoom(lats, 5)
lons_interp = zoom(lons, 5)
# #cutting off the very last column to make shapes match
lats, lons = lats_interp[:, :-1], lons_interp[:, :-1]
#specify the shape and resolution of your lat-long grid
minlon, maxlon = np.nanmin(lons), np.nanmax(lons)
minlat, maxlat = np.nanmin(lats), np.nanmax(lats)
resolution = 0.00899928005 / 4

grid = np.meshgrid(np.arange(minlon, maxlon, resolution), np.arange(minlat, maxlat, resolution))
tempsgrid = griddata((lons.ravel(), lats.ravel(), ), data.ravel(), (grid[0].ravel(), grid[1].ravel()))
tempsgrid.shape = grid[1].shape

ax = map(-67.85, 25, None)
c = plt.pcolormesh(grid[0], grid[1], tempsgrid, vmin = 0, vmax = 1, cmap = 'Greys_r')
plt.title(f'{satt} MODIS Band 01 Visible Imagery\nTime: 09/14/2003 at 1750z' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# plt.savefig(r"C:\Users\deela\Downloads\terramodisgafilo2004.png", dpi = 400, bbox_inches = 'tight')
plt.show()