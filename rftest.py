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

def genShear(u, v):
    print(u.shape)
    meanU = np.mean(u, axis = 1)
    meanV = np.mean(v, axis = 1)

    sum = np.sum(np.sqrt((u - meanU[:, np.newaxis])**2 + (v - meanV[:, np.newaxis])**2), axis = 1)
    print(sum.shape)

    return sum

def norm(data):
    return (data - np.nanmean(data)) / np.nanstd(data)

ds = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_EOF.nc")
EOFs = ds['eof'].values

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1987-2023.nc")
print(list(dataset.variables))
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.landfall == False, drop=True)
dataset = dataset.where(dataset.dist_land >= 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.lats > 0, drop = True)
validCases = dataset['case']
print(dataset)

data = np.stack([dataset['u_data'], dataset['v_data']], axis = 1)
anom = np.nan_to_num((data))
pcseries = np.dot(anom.reshape(32250, 28), EOFs.reshape(28, 28).T)

variable = 'delta_vmax'
gShear = norm(genShear(dataset['u_data'].values, dataset['v_data'].values))
dShear = norm(dataset['sh_mag'].sel(upper = 200, lower = 850))
uShear = norm(dataset['sh_mag'].sel(upper = 200, lower = 500))
mShear = norm(dataset['sh_mag'].sel(upper = 500, lower = 850))
vmax = norm(np.nan_to_num(dataset['vmax']))
dist = norm(np.nan_to_num(dataset['dist_land']))
rhlm = norm(np.nan_to_num(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper')))
sst = norm(np.nan_to_num(dataset.sst))
mpi = norm(np.nan_to_num(dataset.mpi))

# Let's re-create our features array to include these core variables:
# Establish the variables we wish to train on:
features = np.transpose(np.array([gShear, dShear, uShear, mShear, vmax, dist, rhlm, sst, mpi])) # We transpose the array to be in the order that the RF package likes
features = np.nan_to_num(features)

print(np.shape(features))

# Establish the variable we wish to predict (vortex tilt magnitude):
y = np.copy(np.nan_to_num(dataset[variable]))
print(np.shape(y))


train_inds = features[:25000]
trainOut = y[:25000]
test_inds = features[25000:]
testOut = y[25000:]


print('The number of training cases is:',np.shape(train_inds))
print('The number of testing cases is:',np.shape(test_inds))

rf = RandomForestRegressor(n_estimators=100)
rf.fit(train_inds, trainOut) 
predictions = rf.predict(test_inds)

# # Check predictions:
# c = 0
# for i in test_inds:
#     print(swath_storm_name[i],swath_flight_id[i], tc_dt[i], round(y[i],1), round(predictions[c],1), testPred[i])
#     c = c+1

print('Done.')

print("Mean Error  : ", np.nanmean(np.abs(predictions - testOut)))
print("Median Error: ", np.nanmedian(np.abs(predictions - testOut)))

# Print the importance of each "feature"/predictor:
print(rf.feature_importances_)

# In this instance, we can see the second feature has the highest value (MSLP)