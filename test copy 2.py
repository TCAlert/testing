import cartopy
import cartopy.mpl.geoaxes
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


#fig, ax = plt.subplots()
fig = plt.figure(figsize=(15, 12))
ax = plt.axes()
ax.plot([4,5,3,1,2])


axins = inset_axes(ax, width="40%", height="40%", loc="upper right", 
                   axes_class=cartopy.mpl.geoaxes.GeoAxes, 
                   axes_kwargs=dict(map_projection=cartopy.crs.PlateCarree()))
axins.add_feature(cartopy.feature.COASTLINE)


plt.show()