from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request as urllib

def getStorms(basin):
    link = urlopen('https://ftp.nhc.noaa.gov/atcf/btk/')

    soup = BeautifulSoup(link, 'html.parser')
    storms = []
    for x in soup.find_all('a'):
        temp = x.get('href')
        if basin.lower() in temp:
            storms.append(temp)
    
    data = []
    for x in range(len(storms)):
        temp = (urllib.urlopen(f'https://ftp.nhc.noaa.gov/atcf/btk/{storms[x]}').read().decode('utf-8')).split('\n')
        for y in range(0, len(temp) - 1):
            temp[y] = temp[y].split(',') 
            if temp[y][11].strip() == '34':
                temp[y] = [f'{temp[y][0].strip()}{temp[y][1].strip()}{temp[y][2][0:5].strip()}',
                           f'{temp[y][2][0:9].strip()}',
                           f'{temp[y][2][9:]}00',
                           f' ',
                           f'{temp[y][10]}',
                           f'{temp[y][6]}',
                           f'{temp[y][7]}',
                           f'{temp[y][8]}',
                           f'{temp[y][9]}']
                data.append(temp[y])
    return data