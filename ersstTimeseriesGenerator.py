import xarray as xr
import numpy as np 
import pandas as pd 
import helper 

def computeClimo(data, month, year, constantClimo = False):
    if year - 30 < 1854:
        allYears = range(1854, 1883)
    elif constantClimo == True:
        allYears = range(1991, 2021)
    else:
        allYears = range(year - 30, year - 1)
    allYears = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in allYears]
    data = data.sel(time = allYears)

    return data

def timeseries(month, years, lats, lons, constantClimo = False, dataset = False):
    try:
        if dataset == False:
            dataset = ((xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']).sel(lat = lats, lon = lons)).mean(['lat', 'lon'])
        else:
            dataset = dataset.sel(lat = lats, lon = lons).mean(['lat', 'lon'])
    except:
        dataset = dataset.sel(lat = lats, lon = lons).mean(['lat', 'lon'])

    if constantClimo == True:
        climo = computeClimo(dataset, month, 2020, constantClimo = True)

        anomalies = []
        for year in years:
            anomalies.append(float((dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])).values))
    else:
        anomalies = []
        for year in years:
            climo = computeClimo(dataset, month, int(year))
            anomalies.append(float((dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])).values))

    data = pd.DataFrame({'Year' : years, helper.numToMonth(month)[0:3] : anomalies})
    # print(data.to_string())
    
    return data

#timeseries('8', range(1883, 2024), slice(55, 35), slice(285, 330))