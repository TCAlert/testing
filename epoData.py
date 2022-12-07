import pandas as pd 
import urllib.request as urllib
import numpy as np 

# Read in text file from PSL and convert it to a Pandas dataframe for ease of access
data = pd.read_fwf('https://downloads.psl.noaa.gov/Public/map/teleconnections/epo.reanalysis.t10trunc.1948-present.txt', header = None, names = ['year', 'month', 'day', 'values'])
year = data['year']
month = data['month']
day = data['day']

# Loop through data and convert the individual year, month, and day information into Numpy datetime64 objects
for x in range(len(data['day'])):
    data['day'][x] = np.datetime64(f'{year[x]}-{str(month[x]).zfill(2)}-{str(day[x]).zfill(2)}')

# Resample daily data to obtain monthly means
data = data.resample('M', on = 'day').mean()

# Clean up remaining data
data = data.reset_index()
data = data.drop(['day'], axis = 1)

# Append data to a list of lists to make it easier to reformat
years = [[] for x in range(0, 13)]
for x in range(len(data['year'])):
    if x % 12 == 0:
        years[0].append(int(data['year'][x]))
    years[int(data['month'][x])].append(round(data['values'][x], 2))

# Pass data to a new Pandas dataframe and transpose it (reverse columns and rows)
reformattedData = (pd.DataFrame(years[1:], columns = years[0], index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])).transpose()
print(reformattedData)

# Locally download the data as a CSV 
reformattedData.to_csv(r'C:\Users\Username\Downloads\epo.csv')
