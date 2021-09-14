import datetime
import pandas as pd
import urllib.request as urllib

# Retrieve most recent fix in the NHC or JTWC Best Track for a given storm
def mostRecent(storm):
    year = str(datetime.datetime.now().year)
    if ('al' in storm.lower() or 'ep' in storm.lower() or 'cp' in storm.lower()):
        try:
            link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b' + storm.lower() + year + '.dat'     
            data = urllib.urlopen(link).read().decode('utf-8')  
        except:      
            link = 'https://ftp.nhc.noaa.gov/atcf/btk/b' + storm.lower() + year + '.dat'  
            data = urllib.urlopen(link).read().decode('utf-8')     
    else:
        if ('sh' in storm.lower() and datetime.now().month >= 11):
            year = str(int(year) + 1)
            try:
                link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b' + storm.lower() + year + '.dat'    
                data = urllib.urlopen(link).read().decode('utf-8')           
            except:
                link = f'https://www.nrlmry.navy.mil/atcf_web/docs/tracks/{year}/b{storm.lower()}{year}.dat'          
                data = urllib.urlopen(link).read().decode('utf-8')     

    line = data.split("\n")
    return line[-2]         

# Retrieve best track data for a given TC in a Pandas Dataframe
def getStorm(storm):
    year = str(datetime.datetime.now().year)
    if ('al' in storm.lower() or 'ep' in storm.lower() or 'cp' in storm.lower()):
        try:
            link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b' + storm.lower() + year + '.dat' 
            data = pd.read_csv(link, header = None, usecols=range(20))
        except:
            link = 'https://ftp.nhc.noaa.gov/atcf/btk/b' + storm.lower() + year + '.dat'     
            data = pd.read_csv(link, header = None, usecols=range(20))          
    else:
        if ('sh' in storm.lower() and datetime.datetime.now().month >= 11):
            year = str(int(year) + 1)
        try:
            link = 'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b' + storm.lower() + year + '.dat'          
            data = pd.read_csv(link, header = None, usecols=range(20))
        except:
            link = f'https://www.nrlmry.navy.mil/atcf_web/docs/tracks/{year}/b{storm.lower()}{year}.dat'          
            data = pd.read_csv(link, header = None, usecols=range(20))
    return data

# Retrieve latitude and longitude data for a given TC
def latlon(storm):
    data = getStorm(storm)
    #print(data)
    lat = data[6]
    lon = data[7]

    for x in range(len(lat)):
        if ('N' in lat[x]):
            lat[x] = int(lat[x].replace('N', '')) * .1
        else:
            lat[x] = int(lat[x].replace('S', '')) * -.1
        if ('E' in lon[x]):
            lon[x] = int(lon[x].replace('E', '')) * .1
        else:
            lon[x] = 360 - int(lon[x].replace('W', '')) * .1
    return lat.iloc[-1], lon.iloc[-1]

# Returns the RMW (radius of maximum winds) for a TC
def rmw(storm):
    data = getStorm(storm)
    return int(data[19].iloc[-1])
