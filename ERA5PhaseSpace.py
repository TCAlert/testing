import matplotlib.pyplot as plt  # Plotting library
import numpy as np
import xarray as xr 
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmaps 
import cartopy, cartopy.crs as ccrs  # Plot maps
import cartopy.feature as cfeature
import cmaps as cmap 
import cdsapi as cds 
import matplotlib.patheffects as pe
import helper 
import ibtracsParser as IP 
import scipy 

USAGE = '```$era5 [temp | dewp | slp] [date] [hour] [level] [name (if in HURDAT2) | coordinate]```'
labelsize = 8 
level = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
c = cds.Client()

def Gradient2D(data):
    # Define gradient vector as <fx, fy>
    # Compute the derivative of the dataset, A, in x and y directions, accounting for dimensional changes due to centered differencing
    dAx = data.diff('longitude')[1:, :]
    dAy = data.diff('latitude')[:, 1:]

    # Compute the derivative of both the x and y coordinates
    dx = data['longitude'].diff('lon') * np.cos(data['latitude'] * (np.pi / 180)) 
    dy = data['latitude'].diff('latitude')

    # Return dA/dx and dA/dy, where A is the original dataset
    return dAx / dx, dAy / dy

def retrieve(type, level, date, lat, lon): 
    if "mean_sea_level_pressure" in type:
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type'  : 'reanalysis',
                'variable'      : type,
                'year'          : f'{date[0]}',
                'month'         : f'{date[1]}',
                'day'           : f'{date[2]}',
                'time'          : f'{date[3]}:00',
                'data_format'   : 'netcdf',                               # Supported format: grib and netcdf. Default: grib
                'area'          : [lat + 9, lon - 11, lat - 9, lon + 11], # North, West, South, East.          Default: global
            },
            r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.
    else:
        c.retrieve(
            'reanalysis-era5-pressure-levels',
            {
                'product_type'  : 'reanalysis',
                'variable'      : type,
                'pressure_level': level,
                'year'          : f'{date[0]}',
                'month'         : f'{date[1]}',
                'day'           : f'{date[2]}',
                'time'          : f'{date[3]}:00',
                'data_format'   : 'netcdf',                               # Supported format: grib and netcdf. Default: grib
                'area'          : [lat + 9, lon - 11, lat - 9, lon + 11], # North, West, South, East.          Default: global
            },
            r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.


def rePoPolar(dataset, lats, lons, offset, center = None):
    if center is None:
        clat = np.nanmean(lats)
        clon = np.nanmean(lons)
    else:
        clat, clon = center

    R = 6371.0
    cphi = np.cos(np.radians(clat))
    x = R * np.radians(lons - clon) * cphi
    y = R * np.radians(lats - clat)

    r = np.sqrt(x**2 + y**2)
    t = np.arctan2(y, x)

    rBins = np.linspace(0, 500, 500)
    tBins = np.linspace(-np.pi, np.pi, 500)

    for i in range(len(tBins)):
            tBins[i] = tBins[i] - offset + np.pi/2
            while tBins[i] <= (-1 * np.pi):
                tBins[i] = tBins[i] + (2 * np.pi)
            while tBins[i] >= np.pi:
                tBins[i] = tBins[i] - (2 * np.pi)

    R, T = np.meshgrid(rBins, tBins)
    newX, newY = R * np.cos(T), R * np.sin(T)

    x, y = np.meshgrid(x, y, indexing = 'ij')

    gridded_data = scipy.interpolate.griddata((x.flatten(), y.flatten()), dataset.values.flatten(), (newX, newY), method='linear')

    polar = xr.Dataset(
        {
            'data': (('theta', 'r'), gridded_data.reshape(R.shape))
        },
        coords={
            'r': rBins,
            'theta': tBins
        }
    )

    return x, y, polar['data']

def computeBParam(hgts, dir, center, factor = 1):
    x, y, data = rePoPolar(hgts, hgts.latitude, hgts.longitude, dir, center)
    data = data.sortby("theta")

    left = xr.concat([data.sel(theta=slice(np.pi/2, np.pi)), data.sel(theta=slice(-np.pi, -np.pi/2))], dim="theta").mean()
    right = data.sel(theta=slice(-np.pi/2, np.pi/2)).mean()
    
    if center[0] < 0:
        factor = -1 
    
    return factor * (right - left)

def computeVtParam(hgts, levels, center):
    clat, clon = center

    R = 6371.0
    cphi = np.cos(np.radians(clat))
    x = R * np.radians(hgts.longitude - clon) * cphi
    y = R * np.radians(hgts.latitude - clat)

    r = np.sqrt(x**2 + y**2)

    mask = r <= 500

    hgtTop = hgts.sel(pressure_level = levels[1])
    hgtTop = hgtTop.where(mask).max() - hgtTop.where(mask).min()
    hgtBot = hgts.sel(pressure_level = levels[0])
    hgtBot = hgtBot.where(mask).max() - hgtBot.where(mask).min()

    Vt = (hgtTop - hgtBot) / (np.log(levels[1]) - np.log(levels[0]))
    
    return -Vt
 
# Function to put together the whole plot
def windplot(hurdatParser, database, month, day, year, hour, name, ibtracs = None):
    if type(name) == str:
        try:
            # Retrieve storm data from HURDAT2
            stormData = hurdatParser.retrieveStorm(database, [name, str(year)])['Storm Data']
            stormData = stormData[(stormData['Time'] == np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))]
            lat, lon = stormData['Latitude'].values[0], stormData['Longitude'].values[0]
        except:
            lat, lon = IP.getCoords(ibtracs, f'{month}/{day}/{year}', hour, [name, int(year)])
    else:
        lat, lon = name
    
    date = f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}'
    print(date, hour)

    # Requests GFS zonal and meridional wind data 
    # fileName = retrieve(['geopotential'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
    data = xr.open_dataset(r"C:\Users\deela\Downloads\\era5.nc")['z']

    B = computeBParam(data.sel(pressure_level = slice(900, 600)).mean('pressure_level').squeeze(), dir = 0, center = (lat, lon))
    VTu = computeVtParam(data, [300, 600], center = (lat, lon))
    VTl = computeVtParam(data, [600, 900], center = (lat, lon))

    print(B.values, VTu.values, VTl.values)

windplot(None, None, '09', '05', '2017', '18', (17, -60))