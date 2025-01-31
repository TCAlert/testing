import matplotlib.pyplot as plt
import xarray as xr 
import scipy 
import numpy as np
import cmaps as cmap 
import matplotlib.patheffects as pe
import datetime as DT
from sklearn.ensemble import RandomForestRegressor

# Cleans up time data from the TC-RADAR dataset
def times(dataset):
    tc_dt = np.full((dataset.swath_year.shape[0]),np.nan,dtype='object')

    for i in range(tc_dt.shape[0]):
        # Make sure valid data exists:
        if np.isfinite(dataset.swath_year.isel(num_cases=i)):
            try:
                tc_dt[i] = DT.datetime(dataset.swath_year.isel(num_cases=i).values,\
                                    dataset.swath_month.isel(num_cases=i).values,\
                                    dataset.swath_day.isel(num_cases=i).values,\
                                    dataset.swath_hour.isel(num_cases=i).values,\
                                    dataset.swath_min.isel(num_cases=i).values,0)
            except ValueError:
                print('Weird value for index',i)
    
    return tc_dt

# Helper function to retrieve SHIPS data
def getSHIPS(dataset, params, hours):
    l = ()
    for x in range(len(params)):
        l += (dataset[params[x]].sel(ships_lag_times = hours[x]).values, )

    return l

def regression(input, output):
    print(input.shape)
    input = np.transpose(input)
    
    trainIn = input[:900]
    trainOut = output[:900]
    testIn = input[900:]
    testOut = output[900:]

    regr = RandomForestRegressor(n_estimators=100, n_jobs=-1)
    regr.fit(trainIn, trainOut) 
    predictTest = regr.predict(testIn)

    corr, sig = scipy.stats.pearsonr(predictTest, testOut)
    # error = np.sqrt(np.mean((predictTest - testOut)**2))
    # error = np.mean(np.abs(predictTest - testOut))
    # plt.scatter(predictTest, testOut)
    # plt.show()

    #print(str(error) + f"kt error\nCorrelation: {corr**2}")

    return corr**2

TDRData = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')
validCases = TDRData['num_cases']
print(TDRData)

tc_dt = times(TDRData)
tc_year = TDRData["swath_year"].values
swath_flight_id = TDRData["mission_ID"].values
swath_storm_name = TDRData["storm_name"].values

# vars = list(TDRData.variables)
# ships = []
# for x in range(len(vars)):
#     if '_ships' in vars[x]:
#         ships.append(vars[x])
ships = ['lat_ships', 'lon_ships', 'vmax_ships', 'pres_ships', 'motion_x_ships', 'motion_y_ships', 'shdc_ships', 'sddc_ships', 'shrg_ships', 'shgc_ships', 'shrd_ships', 'shtd_ships', 'shrs_ships', 'shts_ships', 'rhlo_ships', 'rhmd_ships', 'rhhi_ships', 'dtl_ships', 'mpi_ships', 'sst_ships', 'ohc_ships', 'pw2m_ships', 'pw2s_ships', 'pw5u_ships', 'pw5m_ships']
predictors = getSHIPS(TDRData, ships, [0 for x in ships])
print(predictors, np.shape(predictors[0]))

# Establish the variable we wish to predict (in this case the max vortex tilt magnitude in the middle troposphere):
vTiltMax = np.nanmax(TDRData["tc_tilt_magnitude"].sel(height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
print(np.shape(vTiltMax))

corrList = []
for x in range(len(predictors)):
    for y in range(len(predictors)):
        #try:
            corr, sig = regression(predictors[:x] + predictors[:y], vTiltMax)
            corr = corr**2
            print(corr)
        #except:
        #    corr = 0
        #corrList.append(corr)

corrList = np.transpose(np.array(corrList).reshape(len(predictors), len(predictors)))
corrList = corrList# - corrList[:, [0]]
ships = [x[0:4] for x in ships]

fig = plt.figure(figsize=(14, 12))
ax = plt.axes()
ax.set_frame_on(False)
ax.set_xticks(range(len(predictors)))
ax.set_yticks(range(len(predictors)))
ax.set_xticklabels(ships) 
ax.set_yticklabels(ships) 

s = plt.pcolormesh(np.arange(len(predictors)), np.arange(len(predictors)), corrList, cmap = cmap.probs2(), vmin = 0, vmax = .75)
for x in range(len(predictors)):
    for y in range(len(predictors)):
        plt.text(y, x, f'{(round(corrList[x][y], 3))}', size=12, color='black', weight = 'bold', horizontalalignment = 'center', verticalalignment = 'center', path_effects=[pe.withStroke(linewidth = 1, foreground="white")])#, transform = ccrs.PlateCarree(central_longitude = 0))

cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02)
cbar.set_label("R^2")

ax.set_title(f'Predictor vs Tilt\nTC-RADAR', fontweight='bold', fontsize=9, loc='left')  
ax.set_title(f'RF\nDeelan Jariwala', fontsize=9, loc='right')
plt.savefig(r"C:\Users\deela\Downloads\corrmatrixthingtcradar.png", dpi = 400, bbox_inches = 'tight')
plt.show()
