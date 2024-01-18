import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

def getMETAR(station, variables):
    data = pd.read_csv(f'https://aviationweather.gov/api/data/dataserver?requestType=retrieve&dataSource=metars&stationString={station}&hoursBeforeNow=96&format=csv', skiprows = [0, 1, 2, 3, 4])
    print(data)
    vars = []
    for x in range(len(variables)):
        if variables[x] == 'observation_time':
            for y in range(len(data[variables[x]])):
                data[variables[x]][y] = np.datetime64(data[variables[x]][y][:-1])
        vars.append(data[variables[x]])

    return vars

def tempPlot(station):
    vars = getMETAR(station, ['observation_time', 'temp_c', 'dewpoint_c'])
    print(vars[0])

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)

    ax.plot(vars[0], vars[1], color = 'red')
    ax.plot(vars[0], vars[2], color = 'green')
    
    plt.title(f"{station.upper()} Temperature/Dewpoint Time Series\nMax Temp: {np.nanmax(vars[1])}" , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\ace.png", dpi = 200, bbox_inches = 'tight')
    plt.show()
    plt.close()
tempPlot('kmia')