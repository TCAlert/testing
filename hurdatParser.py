import numpy as np
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import math 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

pd.options.mode.chained_assignment = None

basin = 'AL'
yearsUsed = [1951, 2022]

if basin == 'EP':
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html'
else:
    link = 'https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.html'

link = urlopen(link)
soup = BeautifulSoup(link, 'html.parser')
lines = soup.get_text().split('\n')

# Useful Charts
class charts():
    def acecum(data):
        name = data['Name']
        year = data['Year']
        stormData = data['Storm Data']

        fig = plt.figure(figsize=(15, 10))
        plt.xticks(rotation = 45)

        plt.ylabel(r'$\bf{ACE}$')

        plt.plot(stormData.Time, stormData.ACE, linewidth = 4)

        plt.xlabel(r"$\bf{Date}$", labelpad=4)
        plt.grid(True)

        plt.title(name.upper() + " " + year, loc = 'left')
        plt.title(r"$\bf{ACE}$" + " " + r"$\bf{Timeline}$")
        plt.title('Total - ' + str(round(stormData['ACE'].iloc[-1], 2)), loc='right') 

        plt.tight_layout()

        plt.savefig(r"C:\Users\deela\Downloads\wpplot.png")
        #plt.show()
        #plt.close()

    def track(data):    
        name = data['Name']
        year = data['Year']
        data = data['Storm Data']
        ace = round(data['ACE'].iloc[-1], 2)
        lons = np.where(data['Longitude'] > 0, data['Longitude'], data['Longitude'] + 360)
        lats = data['Latitude']
        wind = data['Wind']
        stat = data['Status']
        vm = max(wind)

        fig = plt.figure(figsize=(18,5))

        if max(lons) >= 355 or min(lats) == 0:
            ax = plt.axes(projection = ccrs.PlateCarree(central_longitude = 20))
            gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
            gl.top_labels = gl.right_labels = False  
        else:
            ax = plt.axes(projection = ccrs.PlateCarree(central_longitude = 200))
            gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude = 0), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
            gl.top_labels = gl.right_labels = False
        ax.coastlines(resolution='10m', color='black', linewidth=0.8)
        ax.add_feature(cartopy.feature.LAND.with_scale('10m'), facecolor = 'lightgrey')
        ax.add_feature(cartopy.feature.OCEAN, facecolor = 'dimgray')
        ax.add_feature(cartopy.feature.LAKES, facecolor = 'dimgray')
        ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 

        if abs(max(lons) - min(lons)) < abs(max(lats) - min(lats)):
            ax.set_extent([min(lons) - 15, max(lons) + 15, min(lats) - 5, max(lats) + 5], crs=ccrs.PlateCarree())
        else:
            ax.set_extent([min(lons) - 5, max(lons) + 5, min(lats) - 5, max(lats) + 5], crs=ccrs.PlateCarree())

        cmap = LinearSegmentedColormap.from_list("", [
                (0/137, "#5ebaff"),
                (33/137, "#5ebaff"),
                (33/137, "#00faf4"),
                (64/137, "#00faf4"),
                (64/137, "#ffffcc"),
                (83/137, "#ffffcc"),
                (83/137, "#ffe775"),
                (96/137, "#ffe775"),
                (96/137, "#ffc140"),
                (113/137, "#ffc140"),
                (113/137, "#ff8f20"),
                (137/137, "#ff8f20"),
                (137/137, "#ff6060")])

        plt.plot(lons, lats, color = 'black', alpha = 0.5, linewidth = 0.5, transform = ccrs.PlateCarree(central_longitude = 0))
        for x in range(len(stat)):
            if stat[x] in ['SD', 'SS']:
                plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, linewidths=0.5, vmin = 0, vmax = 137, edgecolors='black', zorder = 500, marker = 's', transform = ccrs.PlateCarree(central_longitude = 0))
            elif stat[x] in ['EX', 'LO', 'WV', 'DB']:
                plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, alpha = 0.375, vmin = 0, vmax = 137, linewidths=0.5, edgecolors='black', zorder = 500, marker = '^', transform = ccrs.PlateCarree(central_longitude = 0))
            else:
                p = plt.scatter(lons[x], lats[x], c = wind[x], cmap=cmap, linewidths=0.5, vmin = 0, vmax = 137, edgecolors='black', zorder = 500, transform = ccrs.PlateCarree(central_longitude = 0))
        plt.text(lons[0] - 3, lats[0] + 1, (str(data['Time'][0]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
        plt.text(lons[-1] - 3, lats.iloc[-1] + 1, (str(data['Time'].iloc[-1]))[:10], transform = ccrs.PlateCarree(central_longitude = 0))
        plt.title(f"{name.upper()} {year} Track History\nMax Winds: {str(vm)}kts" , fontweight='bold', fontsize=10, loc='left')
        plt.title(f'Total ACE: {ace}\nDeelan Jariwala', fontsize=10, loc='right')
        plt.legend(handles = [plt.Line2D([0], [0], marker = "s", markersize = 8, linewidth = 0, label = 'Subtropical')], loc = 'upper right')

        cbar = plt.colorbar(p, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max', ticks = [0, 33, 64, 83, 96, 113, 137])    
        cbar.ax.set_yticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])

        plt.savefig(r"C:\Users\deela\Downloads\wpplot.png", bbox_inches='tight', dpi = 222)
        #plt.show()
        #plt.close()

    def VRmslp(data):
        name = data['Name']
        year = data['Year']
        data = data['Storm Data']

        newcmp = LinearSegmentedColormap.from_list("", [
            (0, "#fff2f2"), 
            (15/40, "#ff0000"), 
            (20/40, "#121212"),
            (25/40, "#0000ff"),
            (40/40, "#f2f2ff")])
        cmap = newcmp.reversed() 

        plt.figure(figsize = (9, 6))
        plt.grid()
        plt.plot(data.VR, data.MSLP)
        plt.scatter(data.VR, data.MSLP, c = data['24hrChange'], vmin = -40, vmax = 40, cmap = cmap, zorder = 5)
        plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02, label = '24hr VMax Change')

        #plt.ylim(880, 1020)
        #plt.xlim(0, 4)
        
        plt.ylabel('Minimum SLP')
        plt.xlabel('VMax / mean R34')
        plt.title(f'{name.upper()} {year}', fontweight = 'bold', loc = 'left')
        plt.title('Deelan Jariwala', loc = 'right')
        plt.annotate('Start', (data.VR[0], data.MSLP[0]), xytext = (data.VR[0], data.MSLP[0] - 5))
        plt.annotate('End', (data.VR.iloc[-1], data.MSLP.iloc[-1]), xytext = (data.VR.iloc[-1], data.MSLP.iloc[-1] - 5))
        plt.savefig(r"C:\Users\deela\Downloads\ratio.png", bbox_inches='tight', dpi = 222)
        #plt.show()
        #plt.close()

# Helper Functions
class helper():
    def distance(a, b):
        R = 3443.92
        latA = a[0] * math.pi / 180 
        lonA = a[1] * math.pi / 180
        latB = b[0] * math.pi / 180
        lonB = b[1] * math.pi / 180
        d = R * math.acos(math.cos(latA) * math.cos(latB) * math.cos(lonA - lonB) + (math.sin(latA) * math.sin(latB)))

        return d 

    def ACE(data, status):
        wind = data.astype(int)
        status = status
        total = []
        for x in range(len(wind)):
            if status[x].strip() in ['SS', 'TS', 'HU']:
                ace = wind[x]**2 / 10000
                total.append(round(ace, 2))
            else:
                total.append(0)
        return np.cumsum(total) 

# Loop through HURDAT2 and separate it into a list of lists containing storm data
def getData(year):
    storms = []
    for x in range(len(lines)):
        temp = lines[x].split(',')
        if basin in temp[0] and int(temp[0][4:8]) in year:
            advNum = int(temp[2])
            stormData = lines[x + 1 : x + advNum]
            for y in range(len(stormData)):
                stormData[y] = (f'{temp[0]},' + (stormData[y][:71])).split(',')
            storms.append(stormData)
            x += advNum
    return storms 

def getStormInfo(year):
    names = []
    ID = []
    years = []
    for x in range(len(lines)):
        temp = lines[x].split(',')
        if (basin in temp[0]) and (int(temp[0][4:8]) in year) and len(temp) == 4:
            names.append(temp[1].strip())
            ID.append(temp[0].strip())
            years.append(temp[0][4:8].strip())

    return names, ID, years 

# Filter storm data by month
def filterByMonth(storms, months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']):
    stormsToReturn = []
    for x in range(len(storms)):
        if storms[x][0][1][4:6] in months:
            stormsToReturn.append(storms[x])
    return stormsToReturn

# Convert each array to a Pandas Dataframe for ease of use, as well calculating additional parameters
def stormObjects(l):
    for x in range(len(l)):
        l[x] = pd.DataFrame(l[x], columns = ['ID', 'Date', 'Time', 'L', 'Status', 'Latitude', 'Longitude', 'Wind', 'MSLP', 'R34NE', 'R34SE', 'R34NW', 'R34SW'])        
        l[x] = l[x].drop(l[x][l[x].Time.astype(int) % 600 != 0].index)
        l[x] = l[x].drop('L', axis = 1)
        l[x].index = range(len(l[x]))
        l[x].Latitude = ((l[x].Latitude).str[:-1]).astype(float)
        l[x].Longitude = ((l[x].Longitude).str[:-1]).astype(float) * -1
        l[x].Wind = (l[x].Wind).astype(int)
        l[x].MSLP = (l[x].MSLP).astype(int)
        l[x].Status = (l[x].Status).str.strip()
        l[x].R34NE = (l[x].R34NE).astype(int)
        l[x].R34SE = (l[x].R34SE).astype(int)
        l[x].R34NW = (l[x].R34NW).astype(int)
        l[x].R34SW = (l[x].R34SW).astype(int)

        change = []
        ri = []
        r34 = []
        speed = []
        for y in range(len(l[x]['Wind'])):
            l[x]['ID'][y] = f'{l[x]["ID"][y][0:4]}{l[x]["Date"][y][0:4]}'
            l[x]['Time'][y] = np.datetime64(f'{l[x]["Date"][y][0:4]}-{l[x]["Date"][y][4:6]}-{l[x]["Date"][y][6:8]}T{l[x]["Time"][y][1:3]}')
            try:
                if l[x]['Wind'][y] > 34:
                    r34.append((l[x]['R34NE'][y] + l[x]['R34SE'][y] + l[x]['R34NW'][y] + l[x]['R34SW'][y]) / 4)
                else:
                    r34.append(0)
                
                if (y - 4 >= 0) and ((l[x]['Wind'][y] - l[x]['Wind'][y - 4]) >= 30):
                    ri.append(True)
                else:
                    ri.append(False)
                
                if (y - 1) >= 0:
                    d = helper.distance([l[x]['Latitude'][y], l[x]['Longitude'][y]], [l[x]['Latitude'][y - 1], l[x]['Longitude'][y - 1]])
                    speed.append(round(d / 6, 1))
                else:
                    speed.append(np.nan)

                if (y - 4) >= 0:
                    change.append(l[x]['Wind'][y] - l[x]['Wind'][y - 4])
                else:
                    change.append(np.nan)
            except:
                speed.append(np.nan)
                change.append(0)
                ri.append(False)

        l[x] = l[x].drop('Date', axis = 1)
        l[x]['Speed'] = speed
        l[x]['24hrChange'] = change
        l[x]['RI'] = ri
        l[x]['R34'] = r34
        l[x]['VR'] = l[x]['Wind'] / l[x]['R34']
        l[x]['ACE'] = helper.ACE(l[x]['Wind'], l[x]['Status'])
    return l

def database():
    storms = getData(np.arange(yearsUsed[0], yearsUsed[1]))
    names, ID, years = getStormInfo(np.arange(yearsUsed[0], yearsUsed[1]))
    storms = stormObjects(storms)

    data = []
    for x in range(len(storms)):
        tempDict = {'Name' : names[x],
                    'Year' : years[x],
                    'ID' : ID[x],
                    'VMax' : storms[x]['Wind'].max(),
                    'MSLP' : storms[x]['MSLP'].min(),
                    'ACE' : round(storms[x]['ACE'].iloc[-1], 2),
                    'RI' : storms[x]['RI'].max(),
                    'Max24hr' : storms[x]['24hrChange'].max(),
                    'aceChart' : charts.acecum,
                    'track' : charts.track,
                    'ratio' : charts.VRmslp,
                    'Storm Data' : storms[x]}

        data.append(tempDict)
    return data

def retrieveStorm(dataset, storm = None, ID = None):
    for x in range(len(dataset)):
        if (dataset[x]['Name'] == storm[0].upper()) and (dataset[x]['Year'] == storm[1]):
            data = dataset[x]
            break 
        elif (dataset[x]['ID'].lower() == ID) or (dataset[x]['ID'].upper() == ID):
            data = dataset[x]
            break 
        else:
            data = 'Storm not found!'
    return data


# Sample Usage:
# Pass processed database to retrieveStorm function with necessary inputs
# Returns dictionary with storm information and a few basic charts
hurdat2 = database()

storm = retrieveStorm(hurdat2, ['Irma', '2017'])
storm['ratio'](storm)

plt.show()
plt.chose()
