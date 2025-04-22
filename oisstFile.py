import xarray as xr 
import numpy as np 

labelsize = 9
startYear = 1982
endYear = 2023
extent = [80, 0, 259, 359]

dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.week.mean.nc')
for x in range(len(dataset.time.values)):
    print(dataset.time.values[x])
dataset = dataset.sel(lat=slice(extent[1], extent[0], 2), lon=slice(extent[2], extent[3], 2), time = slice(np.datetime64('1982-01-01'), np.datetime64('2024-12-29')))
data = dataset['sst'] * np.cos(np.radians(dataset.lat))
print(data)
# data.to_netcdf(r"C:\Users\deela\Downloads\\allOISST.nc")
# for x in range(len(links)):
#     dataset = xr.open_dataset(links[x], engine="netcdf4")

#     dataset = dataset.sel(lat=slice(extent[1], extent[0]), lon=slice(extent[2], extent[3]))
#     data = dataset['sst']# * np.cos(np.radians(dataset['lat']))

#     print(data)
data.to_netcdf(r"C:\Users\deela\Downloads\weeklyOISST2.nc")