import numpy as np 
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
from datetime import datetime

REGIONS = {'NATL' : ([-100, -10, 0, 65], (18, 9)),
           'TATL' : ([-90, -20, 0, 40], (18, 9)),
           'CATL' : ([-70, -20, 0, 30], (18, 9)),
           'WATL' : ([-100, -50, 2.5, 35], (18, 9)),
           'EATL' : ([-60, 0, -10, 30], (18, 9)),
           'NAFR' : ([-40, 40, 0, 40], (16, 6)),
           'MEDI' : ([-20, 40, 25, 50], (18, 9)),
           'SATL1' : ([-50, -10, -10, -40], (18, 9)),
           'SATL2' : ([-70, -30, -35, -65], (18, 9)),
           'SATL3' : ([-25, 25, 5, -40], (18, 9)),
           'MDR'  : ([-65, -15, 5, 27.5], (16, 6)),
           'US'   : ([-130, -60, 20, 60], (18, 9)),
           'WUS'  : ([-140, -100, 25, 57.5], (18, 9)),
           'SAMS' : ([-90, -30, -25, -65], (18, 9)),
           'SAMN' : ([-90, -30, 15, -25], (18, 9)),
           'NWATL': ([-85, -45, 25, 60], (18, 9)),
           'NEATL': ([-50, -10, 25, 60], (18, 9)),
           'SWATL': ([-95, -55, 10, 45], (18, 9)),
           'SEATL': ([-50, -10, 10, 45], (18, 9)),
           'CAG'  : ([-100, -70, 5, 30], (18, 9)),
           'CA'   : ([-120, -60, 0, 40], (18, 9)),
           'CAR'  : ([-90, -55, 5, 26], (18, 9)),
           'GOM'  : ([-100, -75, 15, 32.5], (18, 9)),
           'EPAC' : ([-140, -80, 0, 30], (16, 6)),
           'CPAC' : ([-179, -119, 0, 30], (16, 6)),
           'NPAC' : ([-189, -99, 20, 70], (24, 8)),
           'NPAC2': ([110, 200, 20, 70], (24, 8)),
           'TPAC' : ([-179, -79, 0, 50], (16, 6)),
           'WPAC' : ([105, 170, 0, 45], (18, 9)),
           'WMDR' : ([110, 160, 5, 27.5], (16, 6)),
           'PHIL' : ([105, 140, 5, 26], (16, 6)),
           'AUS'  : ([100, 165, -45, 0], (18, 9)),
           'SPAC' : ([139, 199, -45, 0], (18, 9)),
           'SCPAC': ([-189, -129, -45, 0], (18, 9)),
           'SEPAC': ([-159, -79, -45, 0], (18, 9)),
           'ENSO' : ([-189, -79, -25, 25], (16, 6)),
           'EQ'   : ([69, 179, -25, 25], (16, 6)),
           'IO'   : ([30, 120, -35, 30], (18, 9)),
           'SWIO' : ([30, 75, 5, -35], (16, 6)),
           'SEIO' : ([75, 120, 5, -35], (16, 6)),
           'BOB'  : ([75, 120, 5, 30], (16, 6)),
           'ARB'  : ([35, 80, 5, 30], (16, 6))}

USREGIONS = {'NE' : ([-82.5, -65, 37.5, 48], (18, 9)),
             'MA' : ([-85, -67.5, 33, 42.5], (18, 9)),
             'SE' : ([-95, -77.5, 25, 37.5], (18, 9)),
             'SC' : ([-110, -90, 25, 40], (18, 9)),
             'MW' : ([-95, -80, 37.5, 48], (18, 9)),
             'GP' : ([-110, -90, 35, 50], (18, 9)),
             'SW' : ([-130, -105, 30, 42.5], (18, 9)),
             'NW' : ([-130, -110, 40, 50], (18, 9)),
             'US' : ([-126, -67, 23, 51], (18, 9))}

RADCONV = np.pi / 180
RADIUSOFEARTH = 3440.1 #nmi

def greatCircle(lat1, lon1, lat2, lon2): 
    lat1, lon1, lat2, lon2 = lat1 * RADCONV, lon1 * RADCONV, lat2 * RADCONV, lon2 * RADCONV 
    return RADIUSOFEARTH * np.arccos(np.cos(lat1) * np.cos(lat2) * np.cos(lon1 - lon2) + (np.sin(lat1) * np.sin(lat2)))

def dirSpdToUV(direction, magnitude):
    return magnitude * np.cos(np.deg2rad(direction)), magnitude * np.sin(np.deg2rad(direction))

def strip(l):
    l = [x.strip() for x in l]

    return l 

def dayOfYear(num, year):
    if int(year) != 1900 and int(year) % 4 == 0:
        date = str(datetime.strptime(f'{year}-{int(num) + 1}', "%Y-%j").strftime("%m-%d-%Y"))
    else:
        date = str(datetime.strptime(f'{year}-{int(num)}', "%Y-%j").strftime("%m-%d-%Y"))
    
    date = date.split('-')
    date = np.datetime64(f'{date[2]}-{date[0]}-{date[1]}')

    return date

def gridlines(ax, interval):
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize = interval * 1.5, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 100)

    return ax

def numToMonth(num):
    dict = {1 : 'January',
            2 : 'February',
            3 : 'March',
            4 : 'April',
            5 : 'May',
            6 : 'June',
            7 : 'July',
            8 : 'August',
            9 : 'September',
            10: 'October',
            11: 'November',
            12: 'December'}
    
    return dict[int(num)]

def monthToNum(month):
    dict = {'January'   : 1,
            'February'  : 2,
            'March'     : 3,
            'April'     : 4,
            'May'       : 5,
            'June'      : 6,
            'July'      : 7,
            'August'    : 8,
            'September' : 9,
            'October'   : 10,
            'November'  : 11,
            'December'  : 12}
    
    return dict[month]

def theta(temp, pres, ref):
    return temp * ((ref / pres) ** (287.052874 / 1005))

def thetae(temp, pres, ref, sh):
    t = theta(temp, pres, ref)

    return t * (np.e)**((2.501e6 * sh) / (1005 * temp))

def CtoF(temperature):
    return (temperature * (9/5)) + 32

def FtoC(temperature):
    return (temperature - 32) * (5/9)