import gzip
import pandas as pd 
from helper import strip 
from datetime import datetime 
import urllib.request as urllib

# Retrieve most recent fix in the NHC or JTWC Best Track for a given storm
def getData(storm):
    year = str(datetime.now().year)
    if ('al' in storm.lower() or 'ep' in storm.lower() or 'cp' in storm.lower()):
        link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/a' + storm.lower() + year + '.dat'     
        file = urllib.urlopen(link).read().decode('utf-8')    
    else:
        if ('sh' in storm.lower() and datetime.now().month >= 11):
            year = str(int(year) + 1)
            link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/a' + storm.lower() + year + '.dat'    
            file = urllib.urlopen(link).read().decode('utf-8')           
        else:
            link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/a' + storm.lower() + year + '.dat'    
            file = urllib.urlopen(link).read().decode('utf-8')           
    print(link)
    return file
         
def processData(data):
    data = strip(data.split('\n'))[:-1]

    newData = []
    for x in range(len(data)):
        data[x] = strip(data[x].split(','))
        if data[x][11] == '34':
            if data[x][6][-1] == 'N':
                data[x][6] = round(float(data[x][6][:-1]) * .1, 1)
            else:
                data[x][6] = round(float(data[x][6][:-1]) * -.1, 1)

            if data[x][7][-1] == 'E':
                data[x][7] = round(float(data[x][7][:-1]) * .1, 1)
            else:
                data[x][7] = round(float(data[x][7][:-1]) * -.1, 1)
            newData.append(data[x][0:11])

    return newData

def filterData(storm, date, models, hour):
    data = processData(getData(storm))

    filtered = []
    for x in range(len(data)):
        if data[x][2] in date and data[x][4] in models and int(data[x][5]) in hour:
            filtered.append(data[x])

    filtered = pd.DataFrame(filtered)
    
    return filtered
