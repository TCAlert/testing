import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import matplotlib.patheffects as pe
from matplotlib import rcParams
rcParams['font.family'] = 'Courier New'

def timeseries():
    fig = plt.figure(figsize=(16, 8))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)

    # Add state boundaries to plot
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Pressure (dB)',  weight = 'bold', size = 9)
    ax.set_xlabel('Temperature (\u00b0C)', weight = 'bold', size = 9)
    ax.set_ylim(-50, 0)
    ax.set_xlim(15, 30)

    dataset = [xr.open_dataset(r"C:\Users\deela\Downloads\R2903462_029.nc"), xr.open_dataset(r"C:\Users\deela\Downloads\R6902919_183.nc")]
    colors = ['#ff4040', "#802020"]
    for x in range(len(dataset)):
        temp = dataset[x]['TEMP'].sel(N_PROF = 0)
        pres = dataset[x]['PRES'].sel(N_PROF = 0) * -1
        loc = f'{round(float(dataset[x].LATITUDE.sel(N_PROF = 0).values), 1)}N, {round(float(dataset[x].LONGITUDE.sel(N_PROF = 0).values), 1)}W'
        date = str(dataset[x]['DATE_CREATION'].values)
        print(date)
        date = f'{date[2:6]}-{date[6:8]}-{date[8:10]}'
        ax.plot(temp.values, pres.values, linewidth = 2.5, color = colors[x], label = f'{date} ({loc})')
        for y in temp.values:
            if y > 26:
                ax.fill_betweenx(pres.values, 26, np.where(temp.values <= 26, 26, temp.values), color = colors[x], alpha = .25)
                break
    ax.axvline(26)
    plt.legend()

    plt.title(f'ARGO Float Profiles' , fontweight='bold', fontsize=10, loc='left')
    plt.title('Deelan Jariwala', fontsize=10, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\argotest.png", dpi = 400, bbox_inches = 'tight')

    plt.show()

timeseries()