import pandas as pd 
import urllib.request as urllib
import numpy as np 

data = pd.read_fwf('https://downloads.psl.noaa.gov/Public/map/teleconnections/epo.reanalysis.t10trunc.1948-present.txt', header = None, names = ['year', 'month', 'day', 'values'])
year = data['year']
month = data['month']
day = data['day']

for x in range(len(data['day'])):
    data['day'][x] = np.datetime64(f'{year[x]}-{str(month[x]).zfill(2)}-{str(day[x]).zfill(2)}')

data = data.resample('M', on = 'day').mean()
data = data.reset_index()
data = data.drop(['day'], axis = 1)

years = [[] for x in range(0, 13)]
for x in range(len(data['year'])):
    if x % 12 == 0:
        years[0].append(int(data['year'][x]))
    years[int(data['month'][x])].append(round(data['values'][x], 2))

reformattedData = (pd.DataFrame(years[1:], columns = years[0], index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])).transpose()
print(reformattedData)

reformattedData.to_csv(r'C:\Users\deela\Downloads\epo.txt')