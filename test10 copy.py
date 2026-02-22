import numpy as np 
import matplotlib.pyplot as plt

vmax = 140
rmw = 10 
O = 7.2921 * 10**-5
lat = 30
f = 2 * O * np.sin(np.deg2rad(lat))
R = np.arange(10, 500, 1)

o = vmax * (rmw / R[R > rmw])
i = vmax * (R[R <= rmw] / rmw)

V = np.concat((i, o))

ax = plt.axes()
ax.plot(R, V, label = 'VMax')

M = R*V + 0.5 * f * R**2

ax2 = ax.twinx()

ax2.plot(R, M, color = 'black', label = 'M')
plt.legend()
plt.show()