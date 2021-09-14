from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
from siphon.catalog import TDSCatalog
import xarray as xr 
import goesRequest as goes
import cgfs as gfs 
import cmaps as cmap
import bdeck as bdeck 
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import urllib.request as urllib
import math 
from matplotlib.offsetbox import AnchoredText
from datetime import datetime
import matplotlib.patches as mpatches
import pandas as pd 
import bdeck as bdeck 

usage = '```$ships [storm (best track ID)]```'

def ships(storm, year, mon, day):
    print(year, mon, day)
    for x in ['18', '12', '06', '00']:
        try:
            link = f'https://ftp.nhc.noaa.gov/atcf/stext/{year}{mon}{day}{x}{storm.upper()}{year}_ships.txt'
            data = urllib.urlopen(link).read().decode('utf-8')
            break
        except:
            continue 
    
    stime = f'{mon}/{day}/20{year} at {x}z'
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

    if 'AL' in storm.upper():
        line = line[1:4] + line[7:11] + line[12:26]
    else:
        line = line[1:4] + line[7:26]

    for x in range(len(line)):
        sep = ''
        for y in range(len(line[x])):
            if type(line[x][y]) == str:
                sep += line[x][y] + ' '
                line[x][y] = ''

        line[x].insert(0, sep.strip())
        line[x] = [i for i in line[x] if i != '']

    return line, stime, ri, an, link

def chart2(div, ohc, vmx, spd, time, stime, storm, fig):
    time = time[1:]

    para = fig.add_subplot(2, 2, 2)
    para.set_facecolor('whitesmoke')

    para.get_yaxis().get_major_formatter().set_scientific(False)
    #total.set_ylim(ymin = 0, ymax = 30000000)

    hour = para.twinx()
    hour.set_ylabel(r'$\bf{Winds}$' + " " + r'$\bf{(knots)}$')
    #daily.set_ylim(ymin = 0, ymax = 300000)
    para.set_ylabel(r'$\bf{Divergence/OHC/Speed}$')

    hour.plot(time, vmx[1:], linewidth = 4, color = 'darkslateblue')
    para.plot(time, div[2:], linewidth = 4, color = 'gray')
    para.plot(time, ohc[1:], linewidth = 4, color = 'wheat')
    para.plot(time, spd[1:], linewidth = 4, color = 'pink')

    hour.legend(handles=[mpatches.Patch(color = 'darkslateblue', label = 'Winds (knots)'),
                         mpatches.Patch(color = 'gray', label = f'{div[1]}{div[0]}'),
                         mpatches.Patch(color = 'wheat', label = ohc[0]),
                         mpatches.Patch(color = 'pink', label = spd[0])])        
    
    hour.set_xlabel(r"$\bf{Forecast}$" + " " + r'$\bf{Hour}$', labelpad=4)
    hour.grid(True)
    hour.set_title(f"Storm Environment Information\n{storm}", fontweight='bold', fontsize=10, loc = 'left')
    hour.set_title(f"As of {stime}", fontsize=10, loc = 'right')
    hour.grid(True)

def chart1(shr, vmx, sst, hum, time, stime, storm, fig):
    time = time[1:]

    para = fig.add_subplot(2, 2, 4)
    para.set_facecolor('whitesmoke')

    para.get_yaxis().get_major_formatter().set_scientific(False)
    #total.set_ylim(ymin = 0, ymax = 30000000)

    hour = para.twinx()
    hour.set_ylabel(r'$\bf{Winds}$' + " " + r'$\bf{(knots)}$')
    #daily.set_ylim(ymin = 0, ymax = 300000)
    para.set_ylabel(r'$\bf{SST/RH/Shear}$')

    hour.plot(time, vmx[1:], linewidth = 4, color = 'darkslateblue')
    para.plot(time, sst[1:], linewidth = 4, color = 'salmon')
    para.plot(time, shr[1:], linewidth = 4, color = 'lightslategrey')
    para.plot(time, hum[1:], linewidth = 4, color = 'mediumseagreen')

    wind = mpatches.Patch(color = 'darkslateblue', label = "Winds (knots)")
    ssts = mpatches.Patch(color = 'salmon', label = sst[0])
    shear = mpatches.Patch(color = 'lightslategrey', label = shr[0])
    humi = mpatches.Patch(color = 'mediumseagreen', label = hum[0])

    hour.legend(handles=[wind, ssts, shear, humi])        
    
    hour.set_xlabel(r"$\bf{Forecast}$" + " " + r'$\bf{Hour}$', labelpad=4)
    hour.grid(True)
    hour.set_title(f"Storm Environment Information\n{storm}", fontweight='bold', fontsize=10, loc = 'left')
    hour.set_title(f"As of {stime}", fontsize=10, loc = 'right')
    hour.grid(True)

def run(storm):
    fig = plt.figure(figsize=(24, 10))
    
    year = (str(datetime.utcnow().year))[2:4]
    mon = (str(datetime.utcnow().month)).zfill(2)
    day = (str(datetime.utcnow().day)).zfill(2)

    dat, stime, ri, annular, link = ships(storm, year, mon, day)#, '21', '08', '24')
        
    btk = bdeck.mostRecent(storm)
    btk = btk.split(',')
    btk = (', '.join(btk[:10])) + '\n' + (', '.join(btk[10:20]) + '\n' + (', '.join(btk[20:30])) + '\n' + (', '.join(btk[30:])))

    #for x in range(len(dat)):
    #    print(f'{x}. {dat[x]}')

    time = dat[0]
    
    # chart 1
    vmx = dat[2]
    shr = dat[3]
    sst = dat[6]
    hum = dat[11]
    
    # chart 2
    ohc = dat[20]
    div = dat[14]
    spd = dat[19]

    # chart 3
    lat = dat[17][1:]
    lon = dat[18][1:]

    for x in range(len(lon)):
        if lon[x] != None:
            lon[x] = -1 * (lon[x])

    #print('Plotting data')
    fig.set_facecolor('snow')

    text = fig.add_subplot(1, 2, 1)
    text.set_title(f'SHIPS Output Diagram for {storm.upper()}', fontweight = 'bold', fontsize = 20, loc = 'left')
    text.set_title(f'TCAlert\n{stime}', fontstyle = 'italic', fontsize = 10, color = "gray", loc = 'right')
    text.set_facecolor('whitesmoke')

    text.text(0.5, 0.95, f'Latest NHC Best Track Data',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, weight = 'bold', color = "black")

    text.text(0.5, 0.87, f'{btk}',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 12.5, color = "black", wrap = True)

    text.text(0.5, 0.73, f'Annularity Index',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, weight = 'bold', color = "black")

    text.text(0.5, 0.66, f'{annular}',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 10, color = "black", wrap = True)

    text.text(0.5, 0.55, f'Rapid Intensification Probabilities',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, weight = 'bold', color = "black")

    list1 = []
    list2 = []
    for x in range(len(ri)):
        list1.append(f'{ri[x][:5]}{ri[x][6:10]}')
        list2.append(f'{ri[x][-3:].strip()}')

    test = pd.DataFrame([list2], columns = list1)
    text.table(cellText = test.values, colLabels = test.columns, colColours = ["salmon"] * len(list1), cellLoc = 'center', loc = 'center')

    text.set_xticks([])
    text.set_yticks([])

    mp = fig.add_subplot(2, 2, 3, projection=ccrs.PlateCarree(central_longitude=0))

    mp.add_feature(cartopy.feature.COASTLINE.with_scale('10m'))
    mp.add_feature(cartopy.feature.BORDERS.with_scale('10m'))
    mp.add_feature(cartopy.feature.OCEAN, facecolor = 'whitesmoke')
    mp.add_feature(cartopy.feature.LAND, facecolor = 'whitesmoke')

    mp.outline_patch.set_visible(False)
    mp.set_facecolor('whitesmoke')
    #mp.set_title("Map", fontweight = 'bold')
    try:
        mp.set_extent([np.nanmin(lon) - 10, np.nanmax(lon) + 10, np.nanmin(lat) - 5, np.nanmax(lat) + 5], crs=ccrs.PlateCarree())
    except:
        mp.set_extent([np.nanmin(lon) - 10, np.nanmin(lon) + 10, np.nanmax(lat) - 5, np.nanmax(lat) + 5], crs=ccrs.PlateCarree())

    gl = mp.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth = 1, color='gray', alpha=0.5, linestyle='--')   
    gl.xlabels_top = gl.ylabels_right = False

    mp.scatter(lon, lat, linewidths=0.5, vmin = 0, vmax = 1000, edgecolors='black', zorder = 500, transform = ccrs.PlateCarree(central_longitude = 0))
    mp.plot(lon, lat, color = 'black', alpha = 0.5, linewidth = 0.5, transform = ccrs.PlateCarree(central_longitude = 0))
    chart1(shr, vmx, sst, hum, time, stime, storm.upper(), fig)
    chart2(div, ohc, vmx, spd, time, stime, storm.upper(), fig)

    #print('Plotting complete')
    plt.savefig(r"C:\Users\Jariwala\Downloads\shipsplot.png", dpi = 300, bbox_inches = 'tight', facecolor=fig.get_facecolor())
    #plt.show()
    plt.close()
    return link
#print(run("al12"))