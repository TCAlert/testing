import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs 
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import helper  
import matplotlib.patheffects as pe

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
    temp = helper.CtoF(vars[1])
    dewp = helper.CtoF(vars[2])

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)
    ax.set_ylabel('Degrees (F)', weight = 'bold', size = 9)
    ax.set_xlabel('Time', weight = 'bold', size = 9)

    ax.plot(vars[0], temp, color = '#ff4040', linewidth = 2.5)
    ax.plot(vars[0], dewp, color = '#408040', linewidth = 2.5)
    ax.fill_between(vars[0], temp, dewp, color = "#4084d6", alpha = 0.5)
    ax.scatter(vars[0].iloc[0], temp.iloc[0], color = 'black', zorder = 10)
    ax.scatter(vars[0].iloc[0], dewp.iloc[0], color = 'black', zorder = 10)
    plt.text(vars[0].iloc[0] + 14400, temp.iloc[0] + 1, f'{round(temp.iloc[0], 2)}F', size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    plt.text(vars[0].iloc[0] + 14400, dewp.iloc[0] + 1, f'{round(dewp.iloc[0], 2)}F', size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    plt.legend(title = f'Most Recent Change (T): {round(temp.iloc[0] - temp.iloc[1], 2)}F\nMost Recent Change (D): {round(dewp.iloc[0] - dewp.iloc[1], 2)}F', title_fontsize = 8)
    print(vars[0].iloc[0], vars[0].iloc[1])
    
    plt.title(f"{station.upper()} Temperature/Dewpoint Time Series\nMax Temp: {round(np.nanmax(temp), 1)}F\nMin Temp: {round(np.nanmin(temp), 1)}F" , fontweight='bold', fontsize=9, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=9, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\metartemp.png", dpi = 200, bbox_inches = 'tight')
    #plt.show()
    plt.close()

def presPlot(station):
    vars = getMETAR(station, ['observation_time', 'sea_level_pressure_mb', 'altim_in_hg'])
    try:
        pres = vars[1]
        min = np.min(pres)
        if np.isNaN(min):
            print('No SLP data found.')
            Exception
    except:
        pres = vars[2] * 33.864
        min = np.nanmin(pres)

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)
    ax.set_ylabel('Sea Level Pressure (mb)', weight = 'bold', size = 9)
    ax.set_xlabel('Time', weight = 'bold', size = 9)

    ax.plot(vars[0], pres, color = '#ff4040', linewidth = 2.5)
    ax.scatter(vars[0].iloc[0], pres.iloc[0], color = 'black', zorder = 10)
    plt.text(vars[0].iloc[0] + 14400, pres.iloc[0], f'{round(pres.iloc[0], 1)}mb', size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    plt.legend(title = f'Most Recent Change: {round(pres.iloc[0] - pres.iloc[1], 2)}mb', title_fontsize = 8)
    print(vars[0].iloc[0], vars[0].iloc[1])
    
    plt.title(f"{station.upper()} SLP Time Series\nMin Pressure: {round(np.nanmin(pres), 1)}mb" , fontweight='bold', fontsize=9, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=9, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\metarpres.png", dpi = 200, bbox_inches = 'tight')
    #plt.show()
    plt.close()

def windPlot(station):
    vars = getMETAR(station, ['observation_time', 'wind_dir_degrees', 'wind_speed_kt', 'wind_gust_kt'])
    wind = vars[2]
    gust = vars[3]

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(12, 9))
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)
    ax.set_ylabel('Windspeed (kts)', weight = 'bold', size = 9)
    ax.set_xlabel('Time', weight = 'bold', size = 9)

    ax.plot(vars[0], wind, color = '#50246b', linewidth = 2.5)
    ax.plot(vars[0], gust, color = '#b185cc', linewidth = 2.5)
    ax.scatter(vars[0].iloc[0], wind.iloc[0], color = 'black', zorder = 10)
    ax.scatter(vars[0].iloc[0], gust.iloc[0], color = 'black', zorder = 10)
    plt.text(vars[0].iloc[0] + 14400, wind.iloc[0], f'{round(wind.iloc[0], 2)}kt', size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    plt.text(vars[0].iloc[0] + 14400, gust.iloc[0], f'{round(gust.iloc[0], 2)}kt', size=8, color='black', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    plt.legend(title = f'Most Recent Change (W): {round(wind.iloc[0] - wind.iloc[1], 2)}kt\nMost Recent Change (G): {round(gust.iloc[0] - gust.iloc[1], 2)}kt', title_fontsize = 8)
    print(vars[0].iloc[0], vars[0].iloc[1])
    
    plt.title(f"{station.upper()} Wind Speed, Direction, and Gust Time Series\nMax Wind: {round(np.nanmax(wind), 1)}kt\nMax Gust: {round(np.nanmax(gust), 1)}kt" , fontweight='bold', fontsize=9, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=9, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\metarwind.png", dpi = 200, bbox_inches = 'tight')
    plt.show()
    plt.close()

#presPlot('gvnp')
#tempPlot('gvnp')
windPlot('mmmd')
#plt.show()