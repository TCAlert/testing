import pandas as pd
import numpy as np 

def loadCSV():
    try:
        CSV = pd.read_csv('https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv')
    except:
        CSV = pd.read_csv('https://data.humdata.org/dataset/96b309bf-cedb-4f63-8ca3-eb56cdcae876/resource/d1b9b02a-53c7-4134-ada5-234efd2efec2/download/ibtracs_all_list_v04r01.csv')
    prefixes = ('TOKYO', 'TD9635', 'CMA', 'HKO', 'KMA', 'NEWDELHI', 'REUNION', 'BOM', 'NADI', 'TD9636', 'WELLINGTON', 'DS824', 'NEUMANN', 'MLC')
    CSV = CSV.loc[:, ~CSV.columns.str.startswith(prefixes)]

    return CSV


def getCoords(CSV, date, time, storm = None, ID = None):
    stormData = CSV[((CSV.NAME.str.lower() == storm[0].lower()) & (CSV.SEASON.astype(str) == str(storm[1]))) | (CSV.USA_ATCF_ID.astype(str) == str(ID))]
    stormData.ISO_TIME = pd.to_datetime(stormData.ISO_TIME)

    date = str(date).split('/')
    requestDT = pd.Timestamp(f'{date[2]}-{date[0].zfill(2)}-{date[1].zfill(2)}T{time[0:2]}')

    data = stormData[stormData.ISO_TIME == requestDT]

    return data.LAT.values[0], data.LON.values[0]

def getATCF(CSV, date, time, storm, ID = None):
    stormData = CSV[((CSV.NAME.str.lower() == storm[0].lower()) & (CSV.SEASON.astype(str) == str(storm[1]))) | (CSV.USA_ATCF_ID.astype(str) == str(ID))]
    stormData.ISO_TIME = pd.to_datetime(stormData.ISO_TIME)

    date = str(date).split('/')
    requestDT = pd.Timestamp(f'{date[2]}-{date[0].zfill(2)}-{date[1].zfill(2)}')

    data = stormData[stormData.ISO_TIME == requestDT]

    return data.USA_ATCF_ID.values[0]

# print(getATCF(loadCSV(), '9/5/2017', '1800', ['Irma', 2017]))