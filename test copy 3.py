from metpy.calc import storm_relative_helicity, wind_components
from metpy.units import units
import cdsapi as cds 
import xarray as xr 

level = [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
c = cds.Client()
print('Internal HURDAT2 Parser loaded.')

def retrieve(type, level, date, lat, lon): 
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
            'format'        : 'netcdf',                 # Supported format: grib and netcdf. Default: grib
            'area'          : [lat + 5, lon - 5, lat - 5, lon + 5], # North, West, South, East.          Default: global
        },
        r"C:\Users\deela\Downloads\era5.nc")                          # Output file. Adapt as you wish.

retrieve(['geopotentia', 'u_component_of_wind', 'v_component_of_wind'], level, [year, str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2)], lat, lon)
data = xr.open_dataset(r"C:\Users\deela\Downloads\era5.nc")

# set needed values of pressure, height, wind direction/speed
p = [1000, 925, 850, 700, 500, 400] * units.hPa
h = [250, 700, 1500, 3100, 5720, 7120] * units.meters
wdir = [165, 180, 190, 210, 220, 250] * units.degree
sped = [5, 15, 20, 30, 50, 60] * units.knots
# compute wind components
u, v = wind_components(sped, wdir)
# compute SRH with a storm vector
srh = storm_relative_helicity(h, u, v, depth=1 * units.km,
                        storm_u=7 * units('m/s'), storm_v=7 * units('m/s'))
print(srh)