import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from helper import dayOfYear
from scipy import stats

climoYears = [2024, 2024]#2010, 2024]
basin = 'AL'
day = 0
if basin == 'EP':
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
else:
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

try:
    link = urlopen(link)
except:
    if basin == 'EP':
        link = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-042624.txt'
    else:
        link = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt'

    link = urlopen(link)
soup = BeautifulSoup(link, 'html.parser')
lines = soup.get_text().split('\n')

# Helper function to bold text
def bold(string):
    return r"$\bf{" + string + "}$"

# Reformat HURDAT data so that it can be processed more easily 
def getData(year, basin):
    storms = []
    for x in range(len(lines)):
        temp = lines[x].split(',')
        if basin in temp[0] and int(temp[0][4:8]) in year:
            advNum = int(temp[2])
            stormData = lines[x + 1 : x + advNum]
            for y in range(len(stormData)):
                stormData[y] = (f'{temp[0]},' + (stormData[y][:47])).split(',')
                storms.append(stormData[y])
            x += advNum
    return storms 

# Calculates ACE for given period
def ACE(wind, status, time):
    if status in ['SS', 'TS', 'HU'] and time in ['0000', '0600', '1200', '1800']:
        ace = (wind)**2 / 10000
    else:
        ace = 0
    return round(ace, 4) 

# Formats data and calculates the cumulative sum
def yearData(data, year):
    dates = np.arange(f'{year}-01-01', f'{year + 1}-01-01', dtype = 'datetime64[D]')
    daily = [0 for x in range(len(dates))]
    
    for x in range(len(daily)):
        for y in range(len(data)):
            if data[y][1] == dates[x]:
                daily[x] += data[y][3]
    
    if year % 4 == 0 and year != 1900:
        dates = np.delete(dates, 59)
        daily.remove(daily[59])

    accum = np.cumsum(daily)

    return dates, daily, accum

# Retrieve needed climatological data, formats, and plots it
def createClimoData(climo, basin, roll = 5, lats = None, lons = None):
    years = []
    for x in range(climo[0], climo[1] + 1):
        year = x
        data = getData([year, year], basin)
        for x in range(len(data)):
            data[x][1] = np.datetime64(f'{data[x][1][0:4]}-{data[x][1][4:6]}-{data[x][1][6:8]}')
            if lats == lons == None:
                data[x][3] = ACE(int(data[x][-2]), data[x][4].strip(), data[x][2].strip())
            else:
                lat = float(data[x][5][:-1])
                lon = float(data[x][6][:-1]) * -1

                if lat < lats[0] or lat > lats[1] or lon < lons[0] or lon > lons[1]:
                    data[x][3] = 0
                else:
                    data[x][3] = ACE(int(data[x][-2]), data[x][4].strip(), data[x][2].strip())

        dates, daily, accum = yearData(data, year)
        years.append(daily)

    years = pd.DataFrame(years, index = range(climo[0], climo[1] + 1), columns = range(1, 366))
    years = years.rolling(roll, axis = 1, center = True).sum()

    avg = []
    std = []
    for x in range(len(years.columns)):
        avg.append(np.mean(years[x + 1]))
        std.append(np.std(years[x + 1]))
    

    avg = (avg - np.nanmin(avg)) / (np.nanmax(avg) - np.nanmin(avg))

    # plt.plot(range(1, 366), avg)
    # plt.show()

    years = (years - avg) / std

    return years, avg

roll = 28
labelsize = 9
dailyACEAnoms, avg1 = createClimoData(climoYears, basin, roll, [0, 70], [-120, -1])
dailyACEAnoms, avg2 = createClimoData([1980, 2009], basin, roll, [0, 70], [-120, -1])
avg1, avg2 = avg1[:348], avg2[:348]
print(stats.kstest(np.nan_to_num(avg2), np.nan_to_num(avg1)))

dates = np.arange(f'1999-01-01', f'1999-12-15', dtype = 'datetime64[D]')
print(len(dates))
avgDiff = (avg1 - avg2)
print(np.nanmean(avgDiff))

fig = plt.figure(figsize=(14, 11))
ax = plt.axes()

ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_xlabel(f'Time', weight = 'bold', size = 9)
ax.set_ylabel(f'Normalized ACE', weight = 'bold', size = 9)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=np.arange(1, 13, 1)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.axvline(x = dates[0], color = 'black')
ax.axhline(color = 'black')

ax.plot(dates, avgDiff, c = 'black', linewidth = 1)
ax.fill_between(dates, avg1, 0, where=(avg1 > 0), color='blue', alpha=0.3)
ax.fill_between(dates, avg2, 0, where=(avg2 > 0), color='red', alpha=0.3)
ax.set_title(f'Change in Distribution of Seasonal NATL ACE (Rolling {roll} Day Average)\n2010-2024 (blue) minus 1980-2009 (red)', fontweight='bold', fontsize=labelsize, loc='left')  
ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
plt.savefig(r"C:\Users\deela\Downloads\changeInACEDist.png", dpi = 400, bbox_inches = 'tight')
plt.show()

# dataset = dailyACEAnoms.to_numpy()

# dates = []
# for x in range(len(dataset)):
#     for y in range(len(dataset[x])):
#         if dataset[x][y] > 15:
#             dates.append((x + 1981, y))

# dates = np.array(dates)
# nDates = []
# for x in range(len(dates)):
#     try:
#         if dates[:, 1][x] + 1 == dates[:, 1][x + 1]:
#             pass
#         else:
#             date = dayOfYear(dates[:, 1][x], dates[x][0])            
#             nDates.append(date)
#     except:
#         pass
# print(nDates)