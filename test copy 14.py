# def surface(flw, frmw, rira, lats, dist):
#     return round(((0.64502706 * flw) + (0.25005867 * frmw) + (1.00577612 * rira) + (-0.33655164 * lats) + (-0.46855027 * dist)) + 40.19240566764449, 3)
# print(surface(140, 10, 0, 10, 10))

import xarray as xr 
import numpy as np 
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap
from scipy.ndimage import gaussian_filter
import pandas
from sklearn import linear_model
import scipy
from matplotlib import patheffects as pe
from sklearn.ensemble import RandomForestRegressor

def map(interval, labelsize):
    fig = plt.figure(figsize=(18, 9))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.5)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def filter(dataset):
    xDistB = dataset['TOPxdist']
    yDistB = dataset['TOPydist']
    flwrmw = dataset['vdm_flrmw_r']

    normX = xDistB / flwrmw
    normY = yDistB / flwrmw
    radius = np.sqrt(normX**2 + normY**2)
    mask = (radius < 1.33) & (radius > 0.66)
    normX = normX.where(mask, drop = True)
    normY = normY.where(mask, drop = True)
    dataset = dataset.where(mask, drop = True)

    dewp, temp = dataset['levels_dwpt'], dataset['levels_temp']
    rh = 100 - (5 * (temp - dewp))
    rh = rh.min('nlevel')

    RHMask = (rh > 75)
    normX = normX.where(RHMask, drop = True)
    normY = normY.where(RHMask, drop = True)
    rh = rh.where(RHMask, drop = True)

    dataset = dataset.where(RHMask, drop = True)
    
    return dataset

def bin(xData, yData, values):
    xBins = np.arange(195, 312.5, 2.5)
    yBins = np.arange(5, 42.5, 2.5)
    grid = np.meshgrid(xBins, yBins)

    data = []
    nobs = []
    for x in range(len(xBins)):
        for y in range(len(yBins)):
            subList = []
            for z in range(len(values)):
                try:
                    if (xData[z] > xBins[x]) and (xData[z] < xBins[x + 1]) and (yData[z] > yBins[y]) and (yData[z] < yBins[y + 1]):
                        subList.append(values[z])
                except:
                    pass
            data.append(np.nanmean(subList))
            nobs.append(len(subList))
    data = np.array(data)
    nobs = np.array(nobs)
    print(np.nanmax(data), np.nanmin(data), grid[0].shape)

    return [grid[0].T, grid[1].T], np.array(data.T).reshape(grid[0].T.shape), np.array(nobs.T).reshape(grid[0].T.shape)

def regression(input, output):
    input = np.transpose(input)
    
    trainIn = np.transpose(input[:, :600])
    trainOut = output[:600]
    testIn = np.transpose(input[:, 600:])
    testOut = output[600:]

    print(f"trainIn shape: {trainIn.shape}")
    print(f"trainOut shape: {trainOut.shape}")

    regr = linear_model.LinearRegression()
    regr.fit(trainIn, trainOut)
    predictTest = regr.predict(testIn)

    print(regr.coef_, regr.intercept_)

    # regr = RandomForestRegressor(n_estimators=100, n_jobs=-1)
    # regr.fit(trainIn, trainOut) 
    # predictTest = regr.predict(testIn)

    corr, sig = scipy.stats.pearsonr(predictTest, testOut)
    # error = np.sqrt(np.mean((predictTest - testOut)**2))
    error = np.mean(np.abs(predictTest - testOut))
    plt.scatter(predictTest, testOut)
    plt.xlabel('predicted')
    plt.ylabel('actual')
    plt.title('r^2 = ' + str(round(corr**2, 2)) + ', MAE: ' + str(round(error, 2)))
    # plt.xlim(0, 2.5)
    # plt.ylim(0, 2.5)
    plt.savefig(r"C:\Users\deela\Downloads\ratiopred.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

    #print(str(error) + f"kt error\nCorrelation: {corr**2}")

    return corr**2

def scatter(x, y, z = None):    
    fig = plt.figure(figsize=(14, 11))
    ax = plt.axes()

    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_xlabel(f'{x[0]}', weight = 'bold', size = 9)
    ax.set_ylabel(f'{y[0]}', weight = 'bold', size = 9)
    ax.axvline(color = 'black')
    ax.axhline(color = 'black')
    print(len(x[1]), y[1].shape)
    if z == None:
        ax.scatter(x[1], y[1], c = 'black', linewidth = 2)
    else:
        s = ax.scatter(x[1], y[1], c = z[1], cmap = cmap.probs2(), linewidth = 2)
        cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max')
        cbar.set_label(z[0])

    tempX, tempY = x[1][(~np.isnan(x[1])) & (~np.isnan(y[1]))], y[1][(~np.isnan(x[1])) & (~np.isnan(y[1]))]
    corr, sig = scipy.stats.pearsonr(np.nan_to_num(tempX), np.nan_to_num(tempY))
    
    regr = linear_model.LinearRegression()
    regr.fit(tempX.reshape(-1, 1), tempY.reshape(-1, 1))
    coef, intr = regr.coef_[0][0], regr.intercept_[0]
    print(regr.coef_)

    bogusX = np.linspace(np.nanmin(tempX), np.nanmax(tempY))

    ax.plot(bogusX, (coef * bogusX) + intr, linewidth = 2, color = 'black')

    ax.set_title(f'Dropsonde Ratio {x[0]}/{y[0]} Scatterplot\nn = {len(x[1])}, R^2 = {str(round(corr**2, 2))}, y = {coef}x + ({intr})', fontweight='bold', fontsize=labelsize, loc='left')  
    ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
    plt.savefig(r"C:\Users\deela\Downloads\scattertest.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

labelsize = 9

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\sonde-master.nc")
dataset = filter(dataset)
print(dataset)
print(list(dataset.variables))

wspd = dataset['levels_wspd']
plvl = dataset['levels_pres']
hlvl = dataset['levels_hgt']
lats = dataset['TOPlat']
lons = 360 + dataset['TOPlon']
frmw = dataset['vdm_flrmw_r']
sora = dataset['sonde_radius']
rira = dataset['bt_intensification_rate_ph']
wl150 = dataset['WL150spd']
flwnd = dataset['vdm_flwnd_spd']
print(np.nanmin(rira.values))
# print(wspd, plvl, hlvl)

vdmflw = []
flw = []
sfc = []
for x in range(len(wspd)):
    flw.append(np.nanmean(wspd[x].where((plvl[x] >= 675) & (plvl[x] <= 725))))
    sfc.append(np.nanmean(wspd[x].where((hlvl[x] >= 5) & (hlvl[x] <= 15))))
    vdmflw.append(flwnd.values[x])
flw, sfc = np.array(flw), np.array(sfc)

ratio = sfc / flw#vdmflw


ratio =  np.nan_to_num(ratio)
features = np.array([flw, frmw, rira, lats, sora])

nFeat = []
nRati = []
nFLW = []
nSFC = []
nwl150 = []
nvdmfl = []
for x in range(len(features[0])):
    if ratio[x] >= 0.05 and wl150[x] > 0:
        nRati.append(ratio[x])
        nFeat.append(features[:, x])
        nSFC.append(sfc[x])
        nFLW.append(flw[x])
        nwl150.append(wl150[x])
        nvdmfl.append(flwnd[x])

print(np.nanmean(ratio), np.nanmedian(ratio))

scatter(['Flight Level Wind (sonde)', np.array(nFLW)], ['Surface Wind', np.array(nSFC)])#, ['Flight Level RMW', np.array(nFeat)[:, 1]])
# scatter(['WL150', np.array(nwl150)], ['Flight Level Wind', np.array(nFLW)])
# scatter(['WL150', nwl150], ['Distance from Center', np.array(nFeat)[:, 4]])
# scatter(['Surface Wind', np.array(nSFC)], ['Flight Level Wind', np.array(nFLW)])

# for x in range(len(nRati)):
#     print(x, nFeat[x], nRati[x])

print(np.nanmean(nRati))

corr = regression(np.nan_to_num(np.array(nFeat)), np.nan_to_num(nwl150))
print(corr)

# grid, data, nobs = bin(lons, lats, ratio)
# nobs = 10 * (nobs / np.nanmax(nobs))**1.4
# nobs = np.where(nobs > 1, 1, nobs)

# ax = map(15, labelsize)

# # c = plt.pcolormesh(grid[0], grid[1], nobs, cmap = cmap.probs(), vmin = 0, vmax = 100, transform = ccrs.PlateCarree(central_longitude=0))
# c = plt.pcolormesh(grid[0], grid[1], data, alpha = nobs, cmap = cmap.probs2(), vmin = 0.75, vmax = 1.25, transform = ccrs.PlateCarree(central_longitude=0))
# cbar = plt.colorbar(c, orientation = 'horizontal', aspect = 100, pad = .08)

# ax.set_title(f'Dropsonde-Derived Average Flight Level Wind Reduction Ratio \n2.5 Degree Bins', fontweight='bold', fontsize=labelsize, loc='left')  
# ax.set_title(f'Deelan Jariwala', fontsize=labelsize, loc='right')  
# plt.savefig(r"C:\Users\deela\Downloads\ratioWithNobs.png", dpi = 400, bbox_inches = 'tight')
# plt.show()


fig = plt.figure(figsize=(14, 7))

# Add the map and set the extent
ax = plt.axes()
ax.set_frame_on(False)
ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
ax.set_ylabel('Number of Dropsondes', weight = 'bold', size = 9)
ax.set_xlabel('Reduction Ratio', weight = 'bold', size = 9)
# ax.set_ylim(0, 24)
# ax.set_xticks(np.arange(-30, 34, 4))
# ax.set_yticks(np.arange(0, 24, 2))

plt.title(f'Tropical Cyclone Dropsonde-Derived Reduction Ratio\nNumber of Valid Datapoints: {len(nRati)}' , fontweight='bold', fontsize=labelsize + 1, loc='left')
plt.title(f'Deelan Jariwala', fontsize=labelsize + 1, loc='right')  
plt.hist(nRati, bins = np.arange(0.5, 2.5, .1), color = '#9f80ff', alpha = 0.75)
plt.savefig(r"C:\Users\deela\Downloads\histogramdropsonde.png", dpi = 400, bbox_inches = 'tight')
plt.show()