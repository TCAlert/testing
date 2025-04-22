import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import xarray as xr 
import cmaps as cmap 
import boto3
from botocore import UNSIGNED
from botocore.config import Config

levels = np.arange(200, 900, 50)
lats = np.arange(-60, 61, 1)
lons = np.arange(-60, 61, 1)

# Helper function to calculate wind shear, primarily for the maximum wind function
def calcShear(u, v, top, bot):
    uShear = u.sel(level = top) - u.sel(level = bot)
    vShear = v.sel(level = top) - v.sel(level = bot)
    return uShear, vShear 

# Helper function to calculate the shear magnitude
def shearMag(u, v):
    return float(((u**2 + v**2)**0.5).values)

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
    
    s3_client.download_file(bucket, file, r"C:\Users\deela\Downloads\tiltTCPRIMED\\" + basin + storm + year + ".nc") 

    dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tiltTCPRIMED\\" + basin + storm + year + ".nc", group = 'rectilinear')
    stormdt = xr.open_dataset(r"C:\Users\deela\Downloads\tiltTCPRIMED\\" + basin + storm + year + ".nc", group = 'storm_metadata')

    vmax = stormdt['intensity'].values
    dwnd = stormdt['intensity_change'].sel(intensity_change_periods = np.timedelta64(86400000000000)).values
    bwnd = stormdt['intensity_change'].sel(intensity_change_periods = np.timedelta64(-86400000000000)).values
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
    uData = dataset['u_wind'].sel(level = levels)
    vData = dataset['v_wind'].sel(level = levels)
    tmpr = dataset['temperature'].sel(level = levels)
    sphum = dataset['specific_humidity'].sel(level = levels)
    rlhum = dataset['relative_humidity'].sel(level = levels)
    pwat = dataset['precipitable_water']
    times = dataset.time.values

    cases  = []
    atcfID = []
    for x in range(len(times)):
        case = case + 1
        cases.append(case)
        atcfID.append(f'{basin.upper()}{str(storm).zfill(2)}{year}')

    ds = xr.Dataset({
                    'rlhum'      : (["case", "level", "lon", "lat"], rlhum.values),
                    'sphum'      : (["case", "level", "lon", "lat"], sphum.values),
                    'u_data'     : (["case", "level", "lon", "lat"], uData.values),
                    'v_data'     : (["case", "level", "lon", "lat"], vData.values),
                    'temperature': (["case", "level", "lon", "lat"], tmpr.values),
                    'pwat'       : (["case", "lon", "lat"], pwat.values),
                    'dist_land'  : (["case"], dstl),
                    'landfall'   : (["case"], landfall),
                    'time'       : (["case"], times),
                    'vmax'       : (['case'], vmax),
                    'mslp'       : (['case'], mslp),
                    'fdelta_vmax': (['case'], dwnd),
                    'bdelta_vmax': (['case'], bwnd),
                    'system_type': (['case'], type),
                    'uspd'       : (['case'], uspd),
                    'vspd'       : (['case'], vspd),
                    'atcf'       : (['case'], atcfID)}, 
        coords =   {"case": cases,
                    "level": uData.level,
                    "lon": lons,
                    "lat": lats})

    return ds, case

IDs = ['AL112008', 'AL072010', 'AL032014', 'AL042014', 'AL052016', 'AL092016', 'AL052019', 'AL092019', 'AL082020', 'AL132020', 'AL192020', 'AL282020', 'AL072021', 'AL082021', 'AL092021', 'AL062022', 'AL072022', 'AL092022', 'AL132022', 'AL172022', 'AL082023', 'AL102023', 'AL202023', 'AL042008', 'AL112008', 'AL042014', 'AL092016', 'AL122016', 'AL072018', 'AL052019', 'AL092020', 'AL282020', 'AL292020', 'AL052021', 'AL062021', 'AL072021', 'AL062022', 'AL172022', 'AL082023', 'AL102023']
IDs = list(set(IDs))

case = 0
data = []
for x in range(len(IDs)):
    # try:
        year = IDs[x][4:]
        basin = IDs[x][:2]
        storm = IDs[x][2:4]
        print(basin, storm, year)

        ds, case = getStormFile(f'{year}', f'{basin}', f'{str(storm).zfill(2)}', case)
        data.append(ds)
        print(f'{basin}{str(storm).zfill(2)}{str(year)}', case)
    # except Exception as e:
    #     print(e)
            #    pass

ds = xr.concat(data, dim = 'case')
ds.to_netcdf(r"C:\Users\deela\Downloads\TC_Tilt_TCPRIMED_ERA5_Files.nc")