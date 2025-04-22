import xarray as xr
import numpy as np 
import matplotlib.pyplot as plt

# Specify the full path to the file
# Change directory to the location of the file
dataset = xr.open_dataset(r"C:\Users\deela\Downloads\amy.ts.precp.lens.nc")
print(dataset['precp'])
TS_aa = dataset['TS'].values
TS_aa = dataset['precp'].values
# plt.imshow(TS_aa.isel(time = 0))
# plt.show()

lon = np.linspace(0,360,288)
lat = np.linspace(-90,90,192)
time = np.arange(1920, 1921+85, 1)

W = np.cos(lat * (180 / np.pi))
W = np.tile(W, (len(lon), 1)) 
W = W / np.sum(W)

GMT = np.sum(np.sum(TS_aa * W.T, axis=2), axis=1)

tr = np.polyfit(time, np.squeeze(GMT).flatten(), 1)
yfit = np.polyval(tr, time)
plt.figure()
plt.plot(time, np.squeeze(GMT))
plt.plot(time, yfit)
plt.title('Global Mean Precipitation (1920-2005)')
plt.xlabel('Year')
plt.ylabel('Precipitation')
plt.legend('GMT', 'Linear Trend')
plt.savefig(r"C:\Users\deela\Downloads\clementplot6.png", dpi = 400, bbox_inches = 'tight')
plt.show()

print(TS_aa.shape)

T = np.zeros((TS_aa.shape[1], TS_aa.shape[2]))
for i in range(TS_aa.shape[1]):
    for j in range(TS_aa.shape[2]): 
        slope = np.polyfit(time, np.squeeze(TS_aa[:, i, j,]), 1)  
        T[i, j] = slope[0]

plt.figure()
plt.imshow(T * 10, aspect='auto', extent=[lon.min(), lon.max(), lat.min(), lat.max()], vmin = -0.0005, vmax = 0.0005, cmap = 'seismic')
plt.gca().invert_yaxis() 
plt.title('Linear Trend 1920-2005')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.colorbar() 
plt.savefig(r"C:\Users\deela\Downloads\clementplot7.png", dpi = 400, bbox_inches = 'tight')
plt.show()