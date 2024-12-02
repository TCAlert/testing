import xarray as xr
import matplotlib.pyplot as plt
import cmaps as cmap 

data = xr.open_dataset(r"C:\Users\deela\Downloads\HURSAT-mw_v05_1992230N11325_ANDREW\1992\1992230N11325.ANDREW.1992.08.24.1447.17.F10.101.hursat-mw.v05.nc")
print(data.variables)

test = data['T85V']
print(test)
plt.imshow(test, origin = 'lower', vmin = 180, vmax = 290, cmap = cmap.mw().reversed())
plt.title("ANDREW.1992.08.24.1447.17.F10")
plt.show()