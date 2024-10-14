import numpy as np
import matplotlib.pyplot as plt
import datetime as DT
import xarray as xr
import scipy.stats as stats
import sklearn
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import warnings 
warnings.simplefilter(action='ignore', category=RuntimeWarning)

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

# Combine dataset using xarray:
TDRData = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')
MIRData = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_swath_mergIR_v3l.nc")

rirb = MIRData["IR_brightness_recentered_grid"] # These are the IR brightness temps on a TC centered grid
pirb = MIRData['IR_brightness_recentered_polar_grid']

tc_dt = times(TDRData)
tc_year = TDRData["swath_year"].values
swath_flight_id = TDRData["mission_ID"].values
swath_storm_name = TDRData["storm_name"].values

vmax_init, pres_init, shdc_init, shgc_init = getSHIPS(TDRData, ["vmax_ships", "pres_ships", "shdc_ships", "shgc_ships"], [0, 0, 0, 0])

# Establish the variable we wish to predict (in this case the max vortex tilt magnitude in the middle troposphere):
vTiltMax = np.nanmax(TDRData["tc_tilt_magnitude"].sel(height = [5, 5.5, 6.0, 6.5]).values, axis = 1)
print(np.shape(vTiltMax))

# Specify some "core" distance (km)
core_dist = 50.

# Create a "distance" array, where distance is relative to the TC center on the recentered grids:
X, Y = np.meshgrid(TDRData['eastward_distance'].values, TDRData['northward_distance'].values)
dist = np.sqrt(X**2 + Y**2)

# Find the x and y indices where the distance is less than our "core_distance" variable:
core_y = np.where(dist <= core_dist)[0]
core_x = np.where(dist <= core_dist)[1]

# Now let's create some new core IR features:
min_core_irb = np.nanmin(rirb.values[:,core_y ,core_x],axis=(1)) 
max_core_irb = np.nanmax(rirb.values[:,core_y, core_x],axis=(1)) 
mean_core_irb = np.nanmean(rirb.values[:,core_y, core_x],axis=(1)) 
std_core_irb = np.nanmean(rirb.values[:,core_y, core_x],axis=(1))
min_irb = rirb.min(dim = ['recentered_lons', 'recentered_lats'], skipna = True) # Take the minimum brightness temperature in the entire domain for each case
max_irb = rirb.max(dim = ['recentered_lons', 'recentered_lats'], skipna = True) # Take the maximum brightness temperature in the entire domain for each case
avg_irb = rirb.mean(dim = ['recentered_lons', 'recentered_lats'], skipna = True) # Take the mean brightness temperature in the entire domain for each case
std_irb = rirb.std(dim = ['recentered_lons', 'recentered_lats'], skipna = True) # Take the standard deviation of brightness temperatures in the entire domain for each case

# Polar Parameters
radialSTD = pirb.std(dim = 'azimuth', skipna = True)
imaxSTD = np.argmax(radialSTD.values, axis = 1)
testPred = []
for x in range(len(imaxSTD)):
    testPred.append(np.nanmin(radialSTD.sel(num_cases = x, radius = slice(imaxSTD[x], 200))))

print(np.shape(std_core_irb))

# Let's re-create our features array to include these core variables:
# Establish the variables we wish to train on:
features = np.transpose(np.array([pres_init, shgc_init, min_irb, avg_irb, std_irb, testPred])) # We transpose the array to be in the order that the RF package likes
features = np.nan_to_num(features)

print(np.shape(features))

# Establish the variable we wish to predict (vortex tilt magnitude):
y = np.copy(vTiltMax)
print(np.shape(y))

# Let's train on the years of interest and we must also make sure we have real data there (not a NaN):
train_inds = np.where((tc_year < 2023) & (y >= 0.))[0]

# We will test our model on cases in 2023:
test_inds  = np.where(tc_year == 2023)[0]

print('The number of training cases is:',np.shape(train_inds))
print('The number of testing cases is:',np.shape(test_inds))

rf = RandomForestRegressor(n_estimators=100)
rf.fit(features[train_inds,:],y[train_inds]) 
predictions = rf.predict(features[test_inds,:])

# Check predictions:
c = 0
for i in test_inds:
    print(swath_storm_name[i],swath_flight_id[i], tc_dt[i], round(y[i],1), round(predictions[c],1), testPred[i])
    c = c+1

print('Done.')

print("Mean Error:   ", np.nanmean(np.abs(predictions - y[test_inds])))
print("Median Error: ", np.nanmedian(np.abs(predictions - y[test_inds])))

# Print the importance of each "feature"/predictor:
print(rf.feature_importances_)

# In this instance, we can see the second feature has the highest value (MSLP)