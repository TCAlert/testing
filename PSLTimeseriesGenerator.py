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

def PSLtimeseries(month, years, lats, lons, level, var, levelType = 'pressure', constantClimo = False):
    link = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/{levelType}/{var}.mon.mean.nc'
    dataset = xr.open_dataset(link)
    if lons[1] > 360:
        lons[1] = lons[1] - 360
        lons[0] = lons[0] - 360
        dataset = dataset.assign_coords(lon=(((dataset.lon + 180) % 360) - 180)).sortby('lon')
    # print(dataset[var].sel(lat = slice(lats[0], lats[1]), lon = slice(lons[0], lons[1]), level = level))
    dataset = dataset[var].sel(lat = slice(lats[0], lats[1]), lon = slice(lons[0], lons[1]), level = level).mean(['lat', 'lon'])

    if constantClimo == True:
        climo = computeClimo(dataset, month, 2020, constantClimo = True).mean('time')

        times = [np.datetime64(f'{year}-{month.zfill(2)}-01') for year in years]
        anomalies = (dataset.sel(time = times) - climo).values
    else:
        anomalies = []
        for year in years:
            climo = computeClimo(dataset, month, int(year))
            anomalies.append(float((dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])).values))

    data = pd.DataFrame({'Year' : years, helper.numToMonth(month)[0:3] : anomalies})
    # print(data.to_string())
    
    return data

# data = PSLtimeseries('8', range(1991, 2024), [15, -15], [345, 375], '.2101', 'chi', levelType = 'sigma', constantClimo = True)
# print(data)