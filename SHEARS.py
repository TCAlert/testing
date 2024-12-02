import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import cmaps as cmap 
import boto3
from botocore import UNSIGNED
from botocore.config import Config

levels = np.arange(200, 900, 50)

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(level = top) - u.sel(level = bot)
    vShear = v.sel(level = top) - v.sel(level = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

# Calculates all the possible shear layers
def allShear(u, v):
    # Define Levels to be used: intervals of 50 between bounds of classic deep shear level
    # Also define a grid of these levels -- will be used later
    grid = np.meshgrid(levels, levels)

    # Calculate the shear magnitudes and append it to the blank list, as well as the U and V components of the vectors
    # Note that we are calculating shear as the difference between the upper and lower bound here (top - bottom)
    # To prevent redundancies, anything else is set to 0
    shear = []
    us = []
    vs = []
    for x in levels:
        for y in levels:
            if y > x:
                uShear, vShear = calcShear(u, v, x, y)
                shear.append(shearMag(uShear, vShear))
                us.append(uShear) 
                vs.append(vShear)
            elif y == x:
                shear.append(0)
                us.append(0)
                vs.append(0)
            else:
                shear.append(np.nan)
                us.append(np.nan)
                vs.append(np.nan)
    # Return the numpy meshgrid and shape the three lists into gridded numpy arrays using  the 2D grid  
    return np.array(shear).reshape(grid[0].shape), np.array(us).reshape(grid[0].shape), np.array(vs).reshape(grid[0].shape)

# Function that retrieves Himawari-9 tiles of the requested band and melds them together
# Data is returned at full resolution, regardless of band
bucket = 'noaa-nesdis-tcprimed-pds'
product_name = 'v01r01'
def getStormFile(year, basin, storm, case):
    dataset = []
    
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    paginator = s3_client.get_paginator('list_objects_v2')
    prefix = f'{product_name}/final/{year}/{basin.upper()}/{storm}/'

    response_iterator = paginator.paginate(
        Bucket = bucket,
        Delimiter='/',
        Prefix = prefix,
    )
    for page in response_iterator:
        for object in page['Contents']:
            if 'env' in object['Key']:
                file = object['Key']
                print(file)
          
    s3_client.download_file(bucket, file, r"D:\\tcprimed_era5v2\\" + basin + storm + year + ".nc") 

    dataset = xr.open_dataset(r"D:\\tcprimed_era5v2\\" + basin + storm + year + ".nc", group = 'diagnostics')
    stormdt = xr.open_dataset(r"D:\\tcprimed_era5v2\\" + basin + storm + year + ".nc", group = 'storm_metadata')

    vmax = stormdt['intensity'].values
    dwnd = stormdt['intensity_change'].sel(intensity_change_periods = np.timedelta64(86400000000000)).values
    mslp = stormdt['central_min_pressure'].values
    type = stormdt['development_level'].values
    vspd = stormdt['storm_speed_meridional_component'].values
    uspd = stormdt['storm_speed_zonal_component'].values
    dstl = stormdt['distance_to_land'].values
    landfall = []
    for x in range(len(dwnd)):
        check = False
        for y in range(0, 5):
            try:
                temp = dstl[x + y]
                if temp < 0:
                    check = True
            except Exception as e:
                break
        landfall.append(check)
    lons = dataset['center_longitude'].values
    lats = dataset['center_latitude'].values
    uData = dataset['u_wind'].sel(regions = 1, level = levels)
    vData = dataset['v_wind'].sel(regions = 1, level = levels)
    empi = dataset['potential_intensity_theoretical'].sel(region = 0).values
    tcsst = (dataset['sst'].values - 273.15).flatten()
    rlhum = dataset['relative_humidity'].sel(regions = 0, level = levels).values
    times = dataset.time.values

    shears = []
    u_shrs = []
    v_shrs = []
    cases  = []
    atcfID = []
    for x in range(len(times)):
        case = case + 1
        shear, u, v = allShear(uData.isel(time = x), vData.isel(time = x))
        shears.append(shear)
        u_shrs.append(u)
        v_shrs.append(v)
        cases.append(case)
        atcfID.append(f'{basin.upper()}{str(storm).zfill(2)}{year}')

    ds = xr.Dataset({'sh_mag'    : (["case", "upper", "lower"], shears), 
                    'u_shrs'     : (["case", "upper", "lower"], u_shrs), 
                    'v_shrs'     : (["case", "upper", "lower"], v_shrs),
                    'rlhum'      : (["case", "upper"], rlhum),
                    'u_data'     : (["case", "upper"], uData.values),
                    'v_data'     : (["case", "upper"], vData.values),
                    'sst'        : (["case"], tcsst),
                    'mpi'        : (["case"], empi),
                    'lons'       : (["case"], lons),
                    'lats'       : (["case"], lats),
                    'dist_land'  : (["case"], dstl),
                    'landfall'   : (["case"], landfall),
                    'time'       : (["case"], times),
                    'vmax'       : (['case'], vmax),
                    'mslp'       : (['case'], mslp),
                    'delta_vmax' : (['case'], dwnd),
                    'system_type': (['case'], type),
                    'uspd'       : (['case'], uspd),
                    'vspd'       : (['case'], vspd),
                    'atcf'       : (['case'], atcfID)}, 
        coords =   {"case": cases,
                    "upper": levels,
                    "lower": levels})

    return ds, case

basins = ['CP', 'EP', 'WP', 'IO', 'SH', 'AL']
case = 0
data = []
for y in range(1987, 2024):
    for basin in basins:
        for x in range(1, 70):
            try:
                ds, case = getStormFile(f'{y}', f'{basin}', f'{str(x).zfill(2)}', case)
                data.append(ds)
                print(f'{basin}{str(x).zfill(2)}{str(y)}', case)
            except Exception as e:
                print(e)
                pass

ds = xr.concat(data, dim = 'case')

ds.to_netcdf(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
print(dataset)
test = dataset['sh_mag'].mean('case')

# Creates the plot
fig = plt.figure(figsize=(15, 12))
ax = plt.axes()
ax.invert_xaxis()
ax.invert_yaxis()
ax.set_ylabel('Pressure (Upper Bound)')
ax.set_xlabel('Pressure (Lower Bound)')
ax.grid()

# Plots the data using the pressure level grid created before
# Note that the vectors in the plot are normalized by the magnitude of the shear
c = ax.contourf(test.upper, test.lower, test.values * 1.944, cmap = cmap.shear(), levels = np.arange(0, 80, .1), extend = 'max')

ax.set_title(f'SHEARS Mean TC Wind Shear (m/s)\nClimatology: 1997-2021', fontweight='bold', fontsize=10, loc='left')
ax.set_title('Deelan Jariwala', fontsize=10, loc='right') 

cb = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
cb.set_ticks(range(0, 85, 5))

plt.savefig(r"C:\Users\deela\Downloads\shearDiagnosticsClimo.png", dpi = 400, bbox_inches = 'tight')
plt.show()