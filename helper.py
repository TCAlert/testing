import numpy as np 
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker

REGIONS = {'NATL' : ([-100, -10, 0, 65], (18, 9)),
           'WATL' : ([-100, -50, 2.5, 35], (18, 9)),
           'MDR'  : ([-65, -15, 5, 27.5], (16, 6)),
           'US'   : ([-130, -60, 20, 60], (18, 9)),
           'WUS'  : ([-140, -100, 25, 57.5], (18, 9)),
           'SWATL': ([-95, -55, 10, 45], (18, 9)),
           'GOM'  : ([-100, -75, 15, 32.5], (18, 9)),
           'EPAC' : ([-140, -80, 0, 30], (16, 6)),
           'CPAC' : ([-179, -119, 0, 30], (16, 6)),
           'NPAC' : ([-179, -99, 20, 70], (16, 6)),
           'TPAC' : ([-179, -79, 0, 50], (16, 6)),
           'WPAC' : ([105, 170, 0, 45], (18, 9)),
           'WMDR' : ([110, 160, 5, 27.5], (16, 6)),
           'PHIL' : ([105, 140, 5, 26], (16, 6)),
           'SPAC' : ([105, 170, -45, 0], (18, 9)),
           'ENSO' : ([-179, -79, -25, 25], (16, 6))}

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

def theta(temp, pres, ref):
    return temp * ((ref / pres) ** (287.052874 / 1005))

def thetae(temp, pres, ref, sh):
    t = theta(temp, pres, ref)

    return t * (np.e)**((2.501e6 * sh) / (1005 * temp))

def CtoF(temperature):
    return (temperature * (9/5)) + 32

def FtoC(temperature):
    return (temperature - 32) * (5/9)