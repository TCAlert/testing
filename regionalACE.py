import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Reformat HURDAT data so that it can be processed more easily 
def getData(lines, year, basin):
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
def createClimoData(climo, basin, lats = None, lons = None):
    if basin == 'EP':
        link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
    else:
        link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

    link = urlopen(link)
    soup = BeautifulSoup(link, 'html.parser')
    lines = soup.get_text().split('\n')

    years = []
    for x in range(climo[0], climo[1] + 1):
        year = x
        data = getData(lines, [year, year], basin)
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
        years.append(accum)

    years = pd.DataFrame(years, index = range(climo[0], climo[1] + 1), columns = range(1, 366))

    return years