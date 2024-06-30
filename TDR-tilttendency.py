import xarray as xr 
import numpy as np 
import cmaps as cmap 
import matplotlib.pyplot as plt

def rePoPolar(dataset, xOrigin, yOrigin, radius):
    

def getData(dataset, var, levels, case):
    rmw = dataset['tc_rmw'].sel(num_cases = case, level = 3).values
    print(rmw)
    data = []
    for x in range(len(var)):
        temp = dataset[var[x]].sel(num_cases = case, level = levels[x])
    
        try:
            temp = np.nanmax(temp, axis = 2)
        except:
            pass

        print(temp)
        plt.imshow(temp)
        plt.show()
        data.append(temp)
    
    return data

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_v3k_1997_2019_xy_rel_swath_ships.nc")
print(list(dataset.variables.keys()))
getData(dataset, ['swath_reflectivity', 'swath_vertical_velocity'], [3, [5, 5.5, 6, 6.5, 7, 7.5, 8]], 1)

times = []
tilts = []
names = []
cases = []
for x in range(len(dataset['num_cases'].values)):
    data = dataset.sel(num_cases = x)        

    date = np.datetime64(f'{str(data['swath_year'].values)}-{str(data['swath_month'].values).zfill(2)}-{str(data['swath_day'].values).zfill(2)}T{str(data['swath_hour'].values).zfill(2)}:{str(data['swath_min'].values).zfill(2)}')
    tilt = np.nanmax(data['tc_tilt_magnitude'].sel(level = [5, 5.5, 6.0, 6.5]).values)
    name = f'{str(data['storm_name'].values)}_{str(data['swath_year'].values)}'
    case = data['num_cases'].values
    if not np.isnan(tilt):
        names.append(name)
        times.append(date)
        tilts.append(tilt)
        cases.append(case)
print('Number of cases:', len(cases))

iNames = [[] for x in np.unique(names)]
iTilts = [[] for x in np.unique(names)] 
iTimes = [[] for x in np.unique(names)] 
iCases = [[] for x in np.unique(names)]
for x in range(len(iNames)):
    for y in range(len(names)):
        uNames, index = np.unique(names, return_index=True)
        uNames = uNames[np.argsort(index)]
        if uNames[x] == names[y]:
            iNames[x].append(names[y])
            iTilts[x].append(tilts[y])
            iTimes[x].append(times[y])
            iCases[x].append(cases[y])

print(f'\n{"Case":10s}{"Name":15s}{"Start":20s}{"End":20s}{"Elapsed":10s}{"Start Tilt":15s}{"Final Tilt":15s}{"Change in Tilt":15s}')

stormTilt = []
startTime = []
counter = 0
for times in iTimes: 
    dTilt = []
    sTime = []
    x = 0
    while x < len(times):
        try:
            y = x + 1
            while y < len(times):
                delta = np.timedelta64(times[y] - times[x], 'h')
                tChange = iTilts[counter][y] - iTilts[counter][x]
                if tChange < 0.0 and delta >= 6 and delta <= 18 and iTilts[counter][x] > 10:
                    getData(dataset, ['swath_reflectivity', 'swath_vertical_velocity'], [3, [5, 5.5, 6, 6.5, 7, 7.5, 8]], iCases[counter][x])

                    print(f'{str(iCases[counter][x])[:-2]:5s}{str(iCases[counter][y])[:-2]:5s}{str(iNames[counter][x].split('_')[0]):15s}{str(times[x]):20s}{str(times[y]):20s}{str(delta):10s}{str(iTilts[counter][x]):15s}{str(iTilts[counter][y]):15s}{str(tChange):15s}')
                    sTime.append(times[x])
                    dTilt.append(tChange)
                    x = y
                    break
                else:
                    y = y + 1
            else:
                x += 1
        except Exception as e:
            print(e)
            x = y
            pass
    counter = counter + 1
    stormTilt.append(dTilt)
    startTime.append(sTime)