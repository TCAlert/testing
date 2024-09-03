import matplotlib.pyplot as plt
import urllib.request as urllib
import numpy as np 

def getData(year, month, dekad):
    link = f'https://ftp.cpc.ncep.noaa.gov/fews/itf/data/itf_{year}_{str(month).zfill(2)}{dekad}.txt'     
    data = (urllib.urlopen(link).read().decode('utf-8')).strip()
    data = data.split('\n')[1:]

    for x in range(len(data)):
        data[x] = data[x].split(',')

    data = np.array(data)
    lats, lons = data[:, 0], data[:, 1]

    west = []
    east = []
    for x in range(len(lons)):
        if float(lons[x]) <= 10 and float(lons[x]) >= -10:
            west.append(float(lats[x]))
        elif float(lons[x]) >= 20 and float(lons[x]) <= 35:
            east.append(float(lats[x]))
    
    return np.nanmean(west), np.nanmean(east)

def getClimo(years, months, dekads):
    allWests = []
    allEasts = []
    for year in years:
        wests = []
        easts = []
        for month in months:
            for dekad in dekads:
                try:
                    west, east = getData(year, month, dekad)
                except:
                    west, east = np.nan, np.nan
                wests.append(west)
                easts.append(east)
        allWests.append(wests)
        allEasts.append(easts)
    
    return np.nanmean(np.array(allWests), axis = 0), np.nanmean(np.array(allEasts), axis = 0)

years = range(1989, 2024)
colors = ['#bf3030', "#bfbf30", "#30bf30", '#30bfbf', '#3030bf', '#bf30bf']
westClimo, eastClimo = getClimo(range(1989, 2024), range(4, 11), range(1, 4))

fig = plt.figure(figsize=(14, 8))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)

# Add state boundaries to plot
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Latitude (\u00b0N)', weight = 'bold', size = 9)
ax.set_xlabel('Month', weight = 'bold', size = 9)
ax.set_ylim(10, 25)
ax.set_xlim(0, 20)
ax.set_xticks(range(0, 21, 3))
ax.set_xticklabels(['April', 'May', 'June', 'July', 'August', 'September', 'October'])

ax.plot(range(len(eastClimo)), eastClimo, linewidth = 2.5, color = '#404040')
for x in range(len(years)):
    westData, eastData = getClimo([years[x]], range(4, 11), range(1, 4))
    ax.plot(range(len(eastData)), eastData, linewidth = 2, color = colors[0], alpha = .1)#, label = str(years[x]))
    #ax.scatter(range(len(westData)), westData, color = 'black', zorder = 10, alpha = .1)
westData, eastData = getClimo([2024], range(4, 11), range(1, 4))
ax.plot(range(len(eastData)), eastData, linewidth = 2, color = colors[0], label = '2024')
ax.scatter(range(len(eastData)), eastData, color = 'black', zorder = 10)

plt.legend()
plt.title(f'East African Monsoon Trough (20E-35E)\nClimatology: 1989-2023' , fontweight='bold', fontsize=10, loc='left')
#plt.title(f'{year}', fontsize = 10, loc = 'center')
plt.title('Deelan Jariwala', fontsize=10, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\africaitfclimo2.png", dpi = 200, bbox_inches = 'tight')

plt.show()