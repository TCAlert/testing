import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from bdeckFormatter import getStorms
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

climoYears = [1995, 2023]
basin = 'AL'
day = 0
if basin == 'EP':
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
else:
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

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

# Retrieves best track data for 2024 and then similarly formats and plots it
def plotbdeck(data, ax):
    for x in range(len(data)):
        data[x][1] = np.datetime64(f'{data[x][1][0:4]}-{data[x][1][4:6]}-{data[x][1][6:8]}')
        data[x][3] = ACE(int(data[x][-2]), data[x][4].strip(), data[x][2].strip())

    dates, daily, accum = yearData(data, 2024)
    accum = daily
    dates = np.arange(f'2024-01-01', f'2025-01-01', dtype = 'datetime64[D]')

    today = datetime.datetime.utcnow()
    today = int(today.strftime('%j'))

    ax.plot(dates[:today], accum[:today], color = 'blue', zorder = 52, linewidth = 2, label = '2024')
    ax.scatter(dates[today - 1], accum[today - 1], color = 'blue', s = 50, zorder = 53)

    return daily, dates, today

# Retrieve needed climatological data, formats, and plots it
def createClimoData(climo, basin, ax):
    years = []
    for x in range(climo[0], climo[1] + 1):
        year = x
        data = getData([year, year], basin)
        for x in range(len(data)):
            data[x][1] = np.datetime64(f'{data[x][1][0:4]}-{data[x][1][4:6]}-{data[x][1][6:8]}')
            data[x][3] = ACE(int(data[x][-2]), data[x][4].strip(), data[x][2].strip())

        dates, daily, accum = yearData(data, year)
        years.append(daily)
    dates = np.arange(f'2024-01-01', f'2025-01-01', dtype = 'datetime64[D]')
    if len(dates) == 366:
        print(dates[59])
        dates = np.delete(dates, 59)

    years = pd.DataFrame(years, index = range(climo[0], climo[1] + 1), columns = range(1, 366))
    max = []
    min = []
    avg = []
    std = []
    for x in range(len(years.columns)):
        max.append(np.nanmax(years[x + 1]))
        min.append(np.nanmin(years[x + 1]))
        avg.append(np.nanmean(years[x + 1]))
        std.append(np.nanstd(years[x + 1]))

    ax.plot(dates, max, color = '#545e54', zorder = 50)
    ax.plot(dates, min, color = '#545e54', zorder = 50)
    ax.fill_between(dates, min, max, color='#d9ecd9', label = 'Range')
    
    ax.plot(dates, np.add(avg, std), color = '#98ab98', zorder = 50)
    ax.plot(dates, np.subtract(avg, std), color = '#98ab98', zorder = 50)
    ax.fill_between(dates, np.add(avg, std), np.subtract(avg, std), color='#add6ad', label = '1 S.D.')

    ax.plot(dates, np.add(avg, np.multiply(0.5, std)), color = '#98ab98', zorder = 50)
    ax.plot(dates, np.subtract(avg, np.multiply(0.5, std)), color = '#98ab98', zorder = 50)
    ax.fill_between(dates, np.add(avg, np.multiply(0.5, std)), np.subtract(avg, np.multiply(0.5, std)), color='#81c081', label = '0.5 S.D.')

    ax.plot(dates, avg, color = 'black', zorder = 51, label = 'Average')

    return years, avg, ax    

fig = plt.figure(figsize=(10, 6))

gs = fig.add_gridspec(64, 64, wspace = 0, hspace = 0)

axes = [fig.add_subplot(gs[0:64, 0:54]),
        fig.add_subplot(gs[0:64, 59:64], frameon = False)]

tx = axes[1]
ax = axes[0]

ax.set_ylim([0, 20])
ax.set_xlim([np.datetime64('2024-05-01'), np.datetime64('2024-12-31')])
ax.set_xticklabels(['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax.grid()

hdata, avg, ax = createClimoData(climoYears, basin, ax)
bdeck, dates, today = plotbdeck(getStorms(basin), ax)
for x in range(len(avg)):
    print(x + 1, avg[x])

hdata.loc[2024] = bdeck
hace = np.array((hdata.sort_values(today))[today])
hyear = np.array((hdata.sort_values(today)).index)
place = int(np.where(hyear == 2024)[0])

cols = ['#', 'Year', 'Daily\nACE', 'Total\nACE']
data = []
for x in range(-5, 6):
    if (len(hyear) - place + x) > (climoYears[1] - climoYears[0] + 2) or (len(hyear) - place + x) < 1:
        data.append(['N/A', 'N/A', 'N/A', 'N/A'])
    else:
        data.append([f'{len(hyear) - place + x}', f'{hyear[place + x]}', f'{round(hace[place - x], 2):.2f}', f'{round(np.array((hdata.sort_values(today)).iloc[:, -1])[place + x], 2):.2f}'])

test = pd.DataFrame(data, columns = cols)
print(test)
table = tx.table(cellText = test.values, colLabels = test.columns, colColours = ['salmon', "#FFFFFF", "#FFFFFF", "#FFFFFF"], colWidths = [0.42, 0.8, 0.8, 0.8], cellLoc = 'center', loc = 'center')
tx.set_xticks([])
tx.set_yticks([])
table.scale(1, 2.37)
table.auto_set_font_size(False)
table.set_fontsize(8)
for x in range(len(test.columns)):
    table[0, x].set_height(0.06)
    table[0, x].set_facecolor('salmon')
    table[6, x].set_facecolor('#c5e6ed')

place = len(hyear) - place
ax.text(dates[today] - 25, bdeck[today] + 10, 
         bold('ACE:') + " " + str(round(bdeck[today], 2)) + "\n" + bold('Avg:') + " " + str(round(avg[today + 1], 2)) + "\n" + bold('Rank:') + " " + str(int(place)) + "/" + str(len(hyear)),
         zorder = 54, color= '#3d3d99', fontsize = 11, 
         path_effects= [PathEffects.withStroke(linewidth=0.5, foreground="w")],
         bbox = dict(facecolor = 'white', alpha=0.75))

ax.set_title(f"HURDAT2 Daily ACE Plot (Climatology: {climoYears[0]}-{climoYears[1]})\nDate: {datetime.datetime.utcnow().date()}" , fontweight='bold', fontsize=10, loc='left')
if basin == 'EP':
    ax.set_title(f'East Pacific\nDeelan Jariwala', fontsize=10, loc='right')
else:
    ax.set_title(f'North Atlantic\nDeelan Jariwala', fontsize=10, loc='right')

ax.legend(loc = 'upper left')
plt.savefig(r"C:\Users\deela\Downloads\acedaily.png", bbox_inches='tight', dpi = 222)
plt.show()
plt.close()
