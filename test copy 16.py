import xarray as xr 

data = xr.open_dataset(r"C:\Users\deela\Downloads\hrrr.t17z.wrfsfcf00.grib2")
print(data)