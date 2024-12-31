import xarray as xr 
import matplotlib.pyplot as plt
import satcmaps as cmap

# data = xr.open_dataset(r"C:\Users\deela\Downloads\POES_ESSA-NOAA_IRNight_s19740901_e19740930_c20190130\poes.NOAA-2.halftone.north.IRNight.1974.09.01.nc")
# print(data)
# cmp, vmax, vmin = cmap.irtables['rbtop']

# test = data['IR_count_raw'].squeeze()#((data['calibrated_longwave_flux'].squeeze() / (5.670374419 * 10**-8))**0.25) - 273.15

# plt.imshow(test, cmap = 'Greys_r')#cmp, vmin = vmin, vmax = vmax)
# plt.show()

data = xr.open_dataset(r"C:\Users\deela\Downloads\N42RF_20241007H1FD_2024_10Oct_07_20_08_56_NC\SEA_2000_10_07_20_38_49.nc")
print(data)

data = data['DBZ']
print(data)

plt.imshow(data, cmap = 'Greys_r')#cmp, vmin = vmin, vmax = vmax)
plt.show()
