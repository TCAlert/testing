import xarray as xr 
import matplotlib.pyplot as plt
import satcmaps as cmap
#[r"C:\Users\deela\Downloads\VI5BO_j01_d20240702_t0554450_e0556412_b34304_c20240702063054305000_oebc_ops.h5", 
data = xr.open_dataset(r"C:\Users\deela\downloads\VI5BO_j01_d20240702_t0553211_e0555154_b34304_c20240702063101475000_oebc_ops.h5", engine = 'h5netcdf', group = 'All_Data/VIIRS-I5-IMG-EDR_All', phony_dims = 'sort')
print(data['BrightnessTemperature'])
cmp, vmax, vmin = cmap.irtables['irg']

plt.imshow(data['BrightnessTemperature'] / 1e4, cmap = cmp, vmin = vmin, vmax = vmax)
plt.show()