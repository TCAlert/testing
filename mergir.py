import xarray as xr 

dataset = xr.open_dataset('https://disc2.gesdisc.eosdis.nasa.gov/opendap/MERGED_IR/GPM_MERGIR.1/2004/006/merg_2004010602_4km-pixel.nc4', decode_times=False)
print(dataset)