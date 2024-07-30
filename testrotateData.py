import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap

def rotateData(data, angle, degrees = True, xPivot = 0, yPivot = 0):
    if degrees == True:
        angle = np.deg2rad(angle)
    shape = data.shape

    rotMat = np.array([[np.cos(angle), -1 * np.sin(angle)], [np.sin(angle), np.cos(angle)]])

    newData = np.zeros((int(shape[0] * (2**0.5)), int(shape[1] * (2**0.5))))
    print(newData.shape)

    for x in range(len(data)):
        for y in range(len(data[0])):
            coordMat = np.transpose(np.array([[(x - xPivot), (y - yPivot)]]))
            rotated = np.dot(rotMat, coordMat)

            newX, newY = int(xPivot + rotated[0]), int(yPivot + rotated[1])
            try:
                newData[newX + int(shape[0] * np.cos(angle)), newY + int(shape[1] * np.sin(angle))] = data[x, y]
            except:
                pass
    return np.transpose(newData)


xs = np.arange(-1, 1, 0.1)
ys = np.arange(-1, 1, 0.1)

data = np.meshgrid(xs, ys)[0]

for x in range(len(xs)):
    for y in range(len(ys)):
        data[x][y] = np.sqrt(xs[x]**2 + ys[y]**2)

data = rotateData(data, 90, True)

fig = plt.figure(figsize=(12, 12))
ax = plt.axes()
plt.imshow(data, cmap = cmap.probs2())
plt.savefig(r"C:\Users\deela\Downloads\rottest.png", dpi = 400, bbox_inches = 'tight')
plt.show()
