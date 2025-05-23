import scipy.ndimage
import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt
import scipy 
import warnings
warnings.filterwarnings("ignore")

def rePoPolar(dataset, radius):
    x = dataset.lons.values
    y = dataset.lats.values
    x, y = np.meshgrid(x, y)

    r = np.sqrt(x**2 + y**2)
    t = np.arctan2(y, x)

    rBins = np.linspace(np.nanmin(r), np.nanmax(r), 200)
    tBins = np.linspace(np.nanmin(t), np.nanmax(t), 200)

    R, T = np.meshgrid(rBins, tBins)
    newX, newY = R * np.cos(T), R * np.sin(T)
    gridded_data = scipy.interpolate.griddata((x.flatten(), y.flatten()), dataset.values.flatten(), (newX.flatten(), newY.flatten()), method='nearest')

    polar = xr.Dataset(
        {
            'data': (('r', 'theta'), gridded_data.reshape(R.shape).transpose())
        },
        coords={
            'r': rBins,
            'theta': tBins
        }
    )

    return polar

def getData(dataset, var, levels, case):
    rmw = dataset['tc_rmw'].sel(num_cases = case, level = 3).values
    shd = dataset['shdc_ships'].sel(num_cases = case, num_ships_times = 0).values
    #print(shd)
    data = []
    for x in range(len(var)):
        temp = dataset[var[x]].sel(num_cases = case, level = levels[x])
    
        try:
            temp = temp.max(axis = 2)
        except:
            pass

        temp = rePoPolar(temp, rmw)
        temp = temp['data'].sel(r = slice(0, rmw))

        #fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # plt.pcolormesh(temp.theta, temp.r, temp.values)
        # plt.show()
        data.append(float(temp.mean().values))    
    return data

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc")
#dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc")
# dataset = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')
dataset = dataset.assign_coords(longitude=((dataset.longitude - 100)).sortby('longitude'))
dataset = dataset.assign_coords(latitude=((dataset.latitude - 100)).sortby('latitude'))
#print(list(dataset.variables.keys()))

times = []
tilts = []
winds = []
names = []
cases = []
for x in range(len(dataset['num_cases'].values)):
    data = dataset.isel(num_cases = x)        

    date = np.datetime64(f'{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)}T{str(data['swath_hour'].values).zfill(2)}:{str(data['swath_min'].values).zfill(2)}')
    tilt = np.nanmax(data['tc_tilt_magnitude'].sel(height = [5, 5.5, 6.0, 6.5]).values)
    vmax = data['vmax_ships'].sel(ships_lag_times = 0).values
    name = f'{str(data['storm_name'].values)}_{str(data['swath_year'].values)}'
    case = data['num_cases'].values
    # if name == 'IAN_2022':
    #     print(case, tilt, date)
    if not np.isnan(tilt):
        names.append(name)
        times.append(date)
        tilts.append(tilt)
        winds.append(vmax)
        cases.append(case)
print('Number of cases:', len(cases))

iNames = [[] for x in np.unique(names)]
iTilts = [[] for x in np.unique(names)] 
iWinds = [[] for x in np.unique(names)]
iTimes = [[] for x in np.unique(names)] 
iCases = [[] for x in np.unique(names)]
for x in range(len(iNames)):
    for y in range(len(names)):
        uNames, index = np.unique(names, return_index=True)
        uNames = uNames[np.argsort(index)]
        if uNames[x] == names[y]:
            iNames[x].append(names[y])
            iTilts[x].append(tilts[y])
            iWinds[x].append(winds[y])
            iTimes[x].append(times[y])
            iCases[x].append(cases[y])

print(f'\n{"Case":10s}{"Name":15s}{"Start":20s}{"End":20s}{"Elapsed":10s}{"Start Tilt":15s}{"Final Tilt":15s}{"Tilt Change":15s}{'TChange / STilt':25s}{"Wind":10s}')

stormTilt = []
startTime = []
scaseList = []
tchangeList = []
dTiltRatio = []
counter = 0
for times in iTimes: 
    dTilt = []
    sTime = []
    x = 0
    while x < len(times):
        try:
            y = x + 1
            bestY = None
            bestDelta = 0.0
            maxAbsTiltChange = 0.0
            tiltChange = 0.0
            while y < len(times):
                delta = np.timedelta64(times[y] - times[x], 'h')
                tChange = round(iTilts[counter][y] - iTilts[counter][x], 2)
                if delta >= 6 and delta <= 26 and iWinds[counter][x] <= 75 and iTilts[counter][x] > 20:# and tChange <= -22.82: 
                    if abs(tChange) > maxAbsTiltChange:
                        bestY = y
                        bestDelta = delta
                        maxAbsTiltChange = abs(tChange)
                        tiltChange = tChange
                y = y + 1
            data = [0, 0]
            print(f'{str(iCases[counter][x])[:-2]:5s}{str(iCases[counter][bestY])[:-2]:5s}{str(iNames[counter][x].split('_')[0]):15s}{str(times[x]):20s}{str(times[bestY]):20s}{str(bestDelta):10s}{str(iTilts[counter][x]):15s}{str(iTilts[counter][bestY]):15s}{str(tiltChange):15s}{str(tiltChange / iTilts[counter][x]):25s}{str(iWinds[counter][bestY]):10s}')
            scaseList.append(float(iCases[counter][x]))#(float(iCases[counter][x]), float(iCases[counter][bestY])))
            tchangeList.append(tChange)
            sTime.append(times[x])
            dTilt.append(tChange)
            dTiltRatio.append(tiltChange / iTilts[counter][x])
            x = bestY
        except Exception as e:
            #print(e)
            x = x + 1
            pass
    counter = counter + 1
    stormTilt.append(dTilt)
    startTime.append(sTime)
print(scaseList)
print(tchangeList)
print(dTiltRatio)