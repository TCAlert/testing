import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from helper import gridlines
import cmaps as cmap
import numpy as np 
import pandas as pd 

def getData(storm, version = 'original'):
    data = pd.read_csv(r"C:\Users\deela\Downloads\\" + storm + " - " + version + ".csv")
    for x in range(len(data['Date'])):
        data['Date'][x] = pd.to_datetime(f"{str(data['Date'][x])[0:4]}-{str(data['Date'][x])[4:6]}-{str(data['Date'][x])[6:8]}T{str(int(data['Hour'][x] / 100)).zfill(2)}")
        data['lat'][x] = float(str(data['lat'][x])[:-1])
        data['lon'][x] = float(str(data['lon'][x])[:-1]) * -1

    return data

def totalACE(vmax, type, time):
    ace = []
    for x in range(len(vmax)):
        print(time[x])
        if type[x] in ['SS', 'TS', 'HU', 'TY', 'ST'] and time[x].hour % 6 == 0 and time[x].minute == 0:
            ace.append(vmax[x]**2 / 10000)
        else:
            ace.append(0)

    return np.cumsum(ace)

def wvp(dataset, name, year = None):
    try:
        storm = dataset.get_storm((name, int(year)))
    except:
        storm = dataset.get_storm(name.upper())
    dict = storm.to_dict()
    name, id, time, vmax, mslp = dict['name'], dict['id'], dict['time'], dict['vmax'], dict['mslp']
    year = id[4:8]

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes()
    ax2 = ax.twinx()
    ax.set_frame_on(False)
    ax2.set_frame_on(False)
    ax.set_yticks(np.arange(0, 210, 10))
    ax2.set_yticks(np.arange(830, 1050, 10))
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax2.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)

    ax.plot(time, vmax, color = 'blue')
    ax2.plot(time, mslp, color = 'red')
    
    plt.title(f"{name.upper()} {year} ({id}) Wind and Pressure History\nMax Winds: {str(max(vmax))}kts | Minimum Pressure: {str(min(mslp))}mb" , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=10, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\wvp.png", dpi = 200, bbox_inches = 'tight')
    #plt.show()
    plt.close()

def acePlot(dataset, name, year = None):
    try:
        storm = dataset.get_storm((name, int(year)))
    except:
        storm = dataset.get_storm(name.upper())
    dict = storm.to_dict()
    name, id, time, type, vmax = dict['name'], dict['id'], dict['time'], dict['type'], dict['vmax']
    year = id[4:8]
    ace = totalACE(vmax, type, time)

    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.set_yticks(np.arange(0, 120, 5))
    ax.tick_params(axis='both', labelsize = 7.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)

    ax.plot(time, ace, color = 'blue')
    
    plt.title(f"{name.upper()} {year} ({id}) Lifetime ACE\nMax Winds: {str(max(vmax))}kts" , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Total ACE: {round(ace[-1], 4)}\nDeelan Jariwala', fontsize=10, loc='right')

    plt.savefig(r"C:\Users\deela\Downloads\ace.png", dpi = 200, bbox_inches = 'tight')
    #plt.show()
    plt.close()

def track(name):
    data = getData(name, 'original')
    name, id, time, stat, lat, lon, vmax = 'Gilda', 'AL161973', data['Date'], data['type'], data['lat'], data['lon'], data['vmax']
    year = id[4:8]
    ace = totalACE(vmax, stat, time)
    cl = 180
    for x in range(len(lon)):
        if lon[x] < 0:
            lon[x] += 360
        if lon[x] < 5 and cl == 180:
            cl = 0
    
    # Creates plot and map using matplotlib/cartopy
    fig = plt.figure(figsize=(18, 5))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude = cl))
    ax.set_frame_on(False)
    ax.coastlines(resolution='10m', color='black', linewidth=0.8)
    ax.add_feature(cartopy.feature.LAND.with_scale('10m'), facecolor = 'lightgrey')
    ax.add_feature(cartopy.feature.OCEAN, facecolor = 'dimgray')
    ax.add_feature(cartopy.feature.LAKES, facecolor = 'dimgray')
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
    ax = gridlines(ax, 5)

    if abs(max(lon) - min(lon)) < abs(max(lat) - min(lat)):
        ax.set_extent([min(lon) - 15, max(lon) + 15, min(lat) - 5, max(lat) + 5], crs=ccrs.PlateCarree())
    else:
        ax.set_extent([min(lon) - 5, max(lon) + 5, min(lat) - 5, max(lat) + 5], crs=ccrs.PlateCarree())

    if cl != 0:
        plt.plot(lon, lat, color = 'black', alpha = 0.5, linewidth = 0.5, transform = ccrs.PlateCarree(central_longitude = 0))
    
    for x in range(len(stat)):
        if stat[x] in ['SD', 'SS']:
            plt.scatter(lon[x], lat[x], c = vmax[x], cmap = cmap.sshws(), linewidths=0.5, vmin = 0, vmax = 140, edgecolors='black', zorder = 6, marker = 's', transform = ccrs.PlateCarree(central_longitude = 0))
        elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
            plt.scatter(lon[x], lat[x], c = vmax[x], cmap = cmap.sshws(), alpha = 0.375, vmin = 0, vmax = 140, linewidths=0.5, edgecolors='black', zorder = 6, marker = '^', transform = ccrs.PlateCarree(central_longitude = 0))
        else:
            p = plt.scatter(lon[x], lat[x], c = vmax[x], cmap = cmap.sshws(), linewidths=0.5, vmin = 0, vmax = 140, edgecolors='black', zorder = 6, transform = ccrs.PlateCarree(central_longitude = 0))

    plt.text(lon.iloc[0] - 3, lat.iloc[0] + 1, (str(time.iloc[0]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
    plt.text(lon.iloc[-1] - 3, lat.iloc[-1] + 1, (str(time.iloc[-1]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
    plt.title(f"{name.upper()} {year} ({id}) Track History\nMax Winds: {str(max(vmax))}kts" , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'Total ACE: {round(ace[-1], 4)}\nDeelan Jariwala', fontsize=10, loc='right')
    plt.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical')], loc = 'upper right')

    cbar = plt.colorbar(p, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 34, 64, 83, 96, 113, 137])    
    cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])

    plt.savefig(r"C:\Users\deela\Downloads\gilma_original.png", dpi = 200, bbox_inches = 'tight')
    plt.show()
    plt.close()
track('Gilda')