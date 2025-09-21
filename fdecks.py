from file import getGZ
import urllib.request

def getFile(basin, num, year):
    link = f'https://ftp.nhc.noaa.gov/atcf/archive/{year}/f{basin.lower()}{num.zfill(2)}{year}.dat.gz'
    urllib.request.urlretrieve(link, r"C:\Users\deela\Downloads\fdeck_temp.dat.gz")

    fileName = r"C:\Users\deela\Downloads\fdeck_text\\" + "f" + basin.lower() + str(num).zfill(2) + str(year) + ".txt"
    getGZ(r"C:\Users\deela\Downloads\fdeck_temp.dat.gz", fileName) 

    with open(fileName, 'r') as data:
        return data.read().split('\n')


def processData(data, file, fixType = 'DVTS', value = 140.):
    lats = []
    lons = []
    for x in range(len(data)):
        temp = data[x].split(',')
        temp = [a.strip() for a in temp]
        try:
            fix = temp[4]
            vmx = float(temp[11]) 
        except:
            continue
        if fix == fixType:
            lat = float(temp[7][:-1]) / 100
            lon = float(temp[8][:-1]) / -100

            lats.append(lat)
            lons.append(lon)
            print(','.join(temp))
            file.write(','.join(temp) + "\n")
            file.flush()
    
    return lats, lons

def processDataAirc(data, file, fixType = 'AIRC'):
    for x in range(len(data)):
        print(data[x])
        temp = data[x].split(',')
        temp = [a.strip() for a in temp]
        try:
            fix = temp[4]
        except:
            continue 

        if fix == fixType:
            print(','.join(temp))
            file.write(','.join(temp) + "\n")
            file.flush()
    
with open(r"C:\Users\deela\Downloads\nhcaircfixes.txt", 'w') as file:
    for x in range(1988, 2025):
        for y in range(1, 40):
            for z in ['ep', 'cp', 'al']:
                try:
                    data = getFile(z, str(y).zfill(2), str(x))
                    lats, lons = processDataAirc(data, file)
                except Exception as e:
                    continue