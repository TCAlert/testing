import xarray as xr
import matplotlib.pyplot as plt
import satcmaps as cmaps 
import numpy as np 
from matplotlib import rcParams  
import bdeck as bdeck 
import cmaps 

labelsize = 8

fig = plt.figure(figsize=(12, 9))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Y Equillibrium Points', weight = 'bold', size = 9)
ax.set_xlabel('X Equillibrium Points', weight = 'bold', size = 9)
ax.axhline(0, linewidth = 2, color = '#000000', zorder = 100)
ax.axvline(0, linewidth = 2, color = '#000000', zorder = 100)
ax.set_ylim(-.5, 10)
ax.set_xlim(-.5, 10)

B = np.arange(0, 500, .01)
A = [0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for a in A:
    c = cmaps.probs4()(a / 10)
    allPoints = [(a / (2*B + 1)), ((2*B**2 + B) / a)]
    print(allPoints[0].shape)
    plt.plot(allPoints[0], allPoints[1], linewidth = 2.5, color = c, label = f'A = {str(a)}')
plt.legend(loc = 'upper right')

plt.title(f'MTH 515 Project 8 (Chemical Network Model)\nConstant A Curves' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\ppeqoints2.png", dpi = 200, bbox_inches = 'tight')
plt.show()