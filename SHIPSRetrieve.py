import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import numpy as np
import urllib.request as urllib
from datetime import datetime
import matplotlib.patches as mpatches
import pandas as pd 
import bdeck as bdeck 
from goesRequest2 import getData

# Function to retrieve SHIPS data for given storm (best track ID)
def ships(storm, year, mon, day, hr = None):
    if hr == None:
        for x in ['18', '12', '06', '00']:
            try:
                link = f'https://ftp.nhc.noaa.gov/atcf/stext/{year}{str(mon).zfill(2)}{str(day).zfill(2)}{x}{storm.upper()}{year}_ships.txt'
                data = urllib.urlopen(link).read().decode('utf-8')
                stime = f'{mon}/{day}/20{year} at {x}z'
                break
            except:
                continue 
    else:
        hr = hr[0:2]
        link = f'https://ftp.nhc.noaa.gov/atcf/stext/{year}{str(mon).zfill(2)}{str(day).zfill(2)}{str(hr).zfill(2)}{storm.upper()}{year}_ships.txt'
        data = urllib.urlopen(link).read().decode('utf-8')
        stime = f'{mon}/{day}/20{year} at {hr}z'
    
    print(stime)

    line = (data.split("\n"))[4:]
    
    for x in range(len(line)):
        line[x] = ([y for y in line[x].split(' ') if y])
        nums = []
        for y in range(len(line[x])):
            try:
                line[x][y] = float(line[x][y])
            except:
                if line[x][y] in ['N/A', 'xx.x', 'xxx.x', 'LOST']:
                    line[x][y] = np.nan

    ri = []
    an = ''
    for x in range(len(line)):
        try:
            if line[x][0] == 'SHIPS':
                temp = line[x][4:9]
                ri.append(' '.join(temp))
            if line[x][0] == '##':
                temp = line[x][1:len(line[x]) - 1]
                an += (' '.join([str(y) for y in temp])) + '\n'
        except Exception as e:
            pass

    # If they add back the missing parameter, bring this back too
    #if 'AL' in storm.upper():
    #    line = line[1:4] + line[7:11] + line[12:26]
    #else:
    #    line = line[1:4] + line[7:26]
    # for x in range(len(line)):
    #     print(line[x])
    line = line[1:4] + line[7:26]# + line[12:26]


    for x in range(len(line)):
        sep = ''
        for y in range(len(line[x])):
            if type(line[x][y]) == str:
                sep += line[x][y] + ' '
                line[x][y] = ''

        line[x].insert(0, sep.strip())
        line[x] = [i for i in line[x] if i != '']


    for x in range(len(line)):
        try:
            if line[x][0][:2] == 'MB':
                line[x][0] = str(int(line[x][1])) + line[x][0]
                line[x].pop(1)
        except:
            pass
    
    line = np.array(line[:-1])

    temp = data.split('\n')
    prev12HrIntensity = []
    [prev12HrIntensity.append(x) for x in temp if "  T-12 MAX WIND: " in x]
    prev12HrIntensity = int(prev12HrIntensity[0][16:21])

    convectionArea = []
    [convectionArea.append(x) for x in temp if "T < -20 C    50-200 KM RAD:" in x]
    convectionArea = float(convectionArea[0][52:58])


    return line, stime, ri, an, link, prev12HrIntensity, convectionArea

# print(ships('AL05', '25', '08', '17', '18'))