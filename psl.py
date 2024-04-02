import xarray as xr 
import numpy as np
        
def createClimoMonthly(allYears, months, var, type, mean = True):    
    allYears = [np.datetime64(f'{year}-{str(month).zfill(2)}-01') for year in allYears for month in months]
    data = []
    for x in range(len(var)):
        if type[x].lower() == 'sigma':
            file = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/sigma/{var[x]}.mon.mean.nc'
        elif type[x].lower() == 'tropopause':
            file = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/tropopause/{var[x]}.mon.mean.nc'
        else:
            file = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.derived/pressure/{var[x]}.mon.mean.nc'
        tempDataset = xr.open_dataset(file)
        tempDataset = tempDataset[var[x]].sel(time = allYears)
        
        if mean == True:
            data.append(tempDataset.mean(['time']))
        else:
            data.append(tempDataset)
    return data 


def getHourlyData(year, month, day, hour, var, level):
    if str(level).lower() == 'surface' and var.lower() != 'slp':
        link = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis/surface/{var}.sig995.{year}.nc'
    elif str(level).lower() == 'surface' and var.lower() == 'slp':
        link = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis/surface/{var}.{year}.nc'
    else:
        link = f'http://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis/pressure/{var}.{year}.nc'
    data = xr.open_dataset(link)
    
    try:
        data = data[var].sel(time = np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'), level = level)
    except:
        data = data[var].sel(time = np.datetime64(f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}'))

    return data

#data = createClimoMonthly([1983], '01', ['omega', 'uwnd', 'chi'], [False, False, True])
#print(data)