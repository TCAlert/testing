import xarray as xr 

shears = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
print(shears)