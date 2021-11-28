from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt  # Plotting library
from cpt_convert import loadCPT # Import the CPT convert function
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import xarray as xr
import windclimo as wc

def bold(string):
    string = r"$\bf{" + string + "}$" + " "
    return string

month = 'Oct'
lag = 0
nin = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - Nino 3.4.csv")
pdo = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - pdo.csv")
pmm = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - pmm.csv")
sah = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - sahel.csv")
ace = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - ace.csv")
amo = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - amo.csv")
tna = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - tna.csv")
tni = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - tni.csv")
amm = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - amm.csv")
atl = pd.read_csv(r"C:\Users\Jariwala\Downloads\oscillations - atlantic3.csv")

file = r"C:\Users\Jariwala\Downloads\uwnd.mon.mean.nc"
dat1 = xr.open_dataset(file)
file = r"C:\Users\Jariwala\Downloads\vwnd.mon.mean.nc"
dat2 = xr.open_dataset(file)

monthnum = nin.columns.get_loc(month)
windlevel = 850
uclimo = wc.uclimo(monthnum, windlevel)
vclimo = wc.vclimo(monthnum, windlevel)

year = nin['Year']
nin = nin[month]
pdo = pdo[month]
pmm = pmm[month]
sah = sah[month]
ace = ace[month]
amo = amo[month]
tna = tna[month]
tni = tni[month]
amm = amm[month]
atl = atl[month]

oscx = amo
oscy = sah

print('Data retrieved')
avg = []
years = []
for x in range(len(oscx)):
    #if oscx[x] >= -1.3 and oscx[x] <= -.9 and oscy[x] < 0:
    #if sah[x] > 1:
        #avg.append(oscy[x])
    if ace[x] > 20:# and sah[x] < 0:# and nin[x] < 0:
        years.append(year[x])
print(years)
data = []
for x in range(len(years)):
    link = r'https://podaac-opendap.jpl.nasa.gov/opendap/allData/ersst/L4/ncei/v5/monthly/netcdf/' + str(years[x]) + '/' + str(monthnum + lag).zfill(2) + '/ersst.v5.' + str(years[x]) + str(monthnum + lag).zfill(2) + '.nc'
    file = Dataset(link)
    data.append(file.variables['ssta'][:].squeeze())

data = sum(data) / len(data)

u = []
v = []
for x in range(len(years)):
    u.append(dat1["uwnd"].sel(level = windlevel, time = str(years[x]) + '-' + str(monthnum + lag) + '-01'))
    v.append(dat2["vwnd"].sel(level = windlevel, time = str(years[x]) + '-' + str(monthnum + lag) + '-01'))
lon = dat1["lon"]
lat = dat2["lat"]

u = (sum(u) / len(u)) - uclimo.squeeze()
v = (sum(v) / len(v)) - vclimo.squeeze()

print('Plotting data')

fig = plt.figure(figsize = (18,10))

# Use the Geostationary projection in cartopy
ax = plt.subplot(projection=ccrs.PlateCarree(central_longitude=0))
ax.set_extent([-180, -60, -40, 60], crs = ccrs.PlateCarree())
#ax.set_extent([240, 360, 0, 70], crs = ccrs.PlateCarree())

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5) 
ax.add_feature(cartopy.feature.STATES, edgecolor = 'black', linewidth = 0.1)
gl = ax.gridlines(crs=ccrs.PlateCarree(central_longitude=0), zorder = 9, draw_labels = True, linewidth = 0.5, color='black', alpha=0.5, linestyle='--', transform = ccrs.PlateCarree(central_longitude=180))
gl.xlabels_top = gl.ylabels_right = False 

plt.quiver(lon[::2], lat[::2], u[::2, ::2], v[::2, ::2])
if lag == 0:
    statement = ""
else:
    statement = f"\nComposite lagged by {lag} months"
ax.set_title('ERSSTv5 SSTA + NCEP/NCAR Reanalysis ' + str(windlevel) + f'mb Wind Anomalies (1971-2000)\nFiltered for {month} +ENSO, +TNI {statement}', fontweight='bold', fontsize=10, loc='left')

plt.imshow(data, origin = 'lower', vmin = -3, vmax = 3, cmap='RdBu_r', transform=ccrs.PlateCarree(central_longitude=180))

print('Plotting complete')

plt.title(bold('TCAlert') + "\n" + str(years), fontsize=10, loc = 'right')
#plt.savefig(r"C:\Users\Jariwala\Downloads\atlninoneutral" + str(lag) + ".png", dpi = 250, bbox_inches = 'tight')
plt.show()