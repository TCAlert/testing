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
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

datafile1 = r"C:\Users\deela\Downloads\tc_radar_v3l_1997_2019_xy_rel_swath_ships.nc"
datafile2 = r"C:\Users\deela\Downloads\tc_radar_v3l_2020_2023_xy_rel_swath_ships.nc"

# Combine dataset using xarray:
ds = xr.open_mfdataset([datafile1,datafile2], concat_dim='num_cases', combine='nested')
dsi = xr.open_dataset(r"C:\Users\deela\Downloads\tc_radar_swath_mergIR_v3l.nc")

rirb = dsi["IR_brightness_recentered_grid"].values # These are the IR brightness temps on a TC centered grid
oirb = dsi["IR_brightness_orig_grid"].values # These are the IR brightness temps for a domain centered on original TDR analysis domain center

tc_dt = np.full((ds.swath_year.shape[0]),np.nan,dtype='object')

for i in range(tc_dt.shape[0]):
    # Make sure valid data exists:
    if np.isfinite(ds.swath_year.isel(num_cases=i)):
        try:
            tc_dt[i] = DT.datetime(ds.swath_year.isel(num_cases=i).values,\
                                   ds.swath_month.isel(num_cases=i).values,\
                                   ds.swath_day.isel(num_cases=i).values,\
                                   ds.swath_hour.isel(num_cases=i).values,\
                                   ds.swath_min.isel(num_cases=i).values,0)
        except ValueError:
            print('Weird value for index',i)
        
print(np.shape(tc_dt))

height = ds["height"].values

vtilt  = ds["tc_tilt_magnitude"].values
vtiltx = ds["tc_eastward_tilt"].values
vtilty = ds["tc_northward_tilt"].values

x_dist = ds["eastward_distance"].values
y_dist = ds["northward_distance"].values

swath_flight_id = ds["mission_ID"].values
swath_storm_name = ds["storm_name"].values

tc_lon = ds["tc_center_longitudes"].values
tc_lat = ds["tc_center_latitudes"].values

olon = ds["original_fix_longitude"].values
olat = ds["original_fix_latitude"].values

# Let's use some best track and SHIPS environmental predictors:
vmax_init = ds["vmax_ships"].sel(ships_lag_times=0).values # Best-track max winds
pres_init = ds["pres_ships"].sel(ships_lag_times=0).values # Best-track central pressure
shdc_init = ds["shdc_ships"].sel(ships_lag_times=0).values # SHIPS deep-layer shear magnitude
shgc_init = ds["shgc_ships"].sel(ships_lag_times=0).values # SHIPS vertically-integrated shear metric


# Establish the variable we wish to predict (in this case the max vortex tilt magnitude in the middle troposphere):
levb = np.where(height == 5.0)[0][0] # Index for bottom layer to consider
levt = np.where(height == 6.5)[0][0] # Index for top layer to consider

vtilt_max = np.nanmax(vtilt[:,levb:levt+1],axis=-1) # Remember, Python indexing is inclusive
print(np.shape(vtilt_max))


tc_year = ds["swath_year"].values

# Specify some "core" distance (km)
core_dist = 50.

# Create a "distance" array, where distance is relative to the TC center on the recentered grids:
X,Y = np.meshgrid(x_dist,y_dist)
dist = np.sqrt(X**2 + Y**2)

# Find the x and y indices where the distance is less than our "core_distance" variable:
core_y = np.where(dist <= core_dist)[0]
core_x = np.where(dist <= core_dist)[1]

# Now let's create some new core IR features:
min_core_irb = np.nanmin(rirb[:,core_y,core_x],axis=(1)) 
max_core_irb = np.nanmax(rirb[:,core_y,core_x],axis=(1)) 
mean_core_irb = np.nanmean(rirb[:,core_y,core_x],axis=(1)) 
std_core_irb = np.nanmean(rirb[:,core_y,core_x],axis=(1))
min_irb = np.nanmin(rirb,axis=(1,2)) # Take the minimum brightness temperature in the entire domain for each case
max_irb = np.nanmax(rirb,axis=(1,2)) # Take the maximum brightness temperature in the entire domain for each case
mean_irb = np.nanmean(rirb,axis=(1,2)) # Take the mean brightness temperature in the entire domain for each case
std_irb = np.nanmean(rirb,axis=(1,2)) # Take the standard deviation of brightness temperatures in the entire domain for each case

print(np.shape(std_core_irb))


# Let's re-create our features array to include these core variables:
# Establish the variables we wish to train on:
features = np.transpose(np.array([pres_init, shgc_init, min_irb, mean_irb, std_irb])) # We transpose the array to be in the order that the RF package likes

features = np.nan_to_num(features)

print(np.shape(features))

# Establish the variable we wish to predict (vortex tilt magnitude):
y = np.copy(vtilt_max)
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
    print(swath_storm_name[i],swath_flight_id[i],tc_dt[i],round(y[i],1),round(predictions[c],1))
    c = c+1

print('Done.')

print(np.nanmean(np.abs(predictions - y[test_inds])))
print(np.nanmedian(np.abs(predictions - y[test_inds])))

# Print the importance of each "feature"/predictor:
print(rf.feature_importances_)

# In this instance, we can see the second feature has the highest value (MSLP)