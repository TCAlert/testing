import xarray as xr
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature
import cmaps as cmap 
import numpy as np 
import helper 
import pandas as pd 

# Create a map using Cartopy
def map(interval, labelsize):
    fig = plt.figure(figsize=(16, 6))

    # Add the map and set the extent
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_frame_on(False)
    
    # Add state boundaries to plot
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth = 0.5)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth = 0.25)
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth = 0.25)
    ax.set_xticks(np.arange(-180, 181, interval), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, interval), crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())
    ax.xaxis.set_major_formatter(cticker.LongitudeFormatter())
    ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)

    return ax 

def computeClimo(data, month, year):
    if year - 30 < 1854:
        allYears = range(1854, 1883)
    else:
        allYears = range(year - 30, year - 1)
    allYears = [np.datetime64(f'{y}-{month.zfill(2)}-01') for y in allYears]
    data = data.sel(time = allYears)

    return data

def std(dataset, average):
    dev = []
    for x in range(29):
        temp = dataset.isel(time = x)
        dev.append((average.values - temp.values)**2)
    dataset = dataset.mean('time')
    dataset.values = np.sqrt(sum(dev) / len(dev))
    stddev = dataset
    return stddev

def anomalies(months, years, sd = False):
    dataset = xr.open_dataset('http://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc')['sst']
    finalData = []
    for month in months:
        allData = []
        for year in years:
            climo = computeClimo(dataset, month, int(year))

            data = dataset.sel(time = np.datetime64(f'{year}-{month.zfill(2)}-01')) - climo.mean(['time'])
            if sd == True:
                sdata = std(climo, climo.mean(['time']))
                allData.append((data / sdata).values)
                title = 'Standardized Anomalies'
            else:
                globalMean = data.mean()
                allData.append((data - globalMean).values)
                title = 'Global Mean Anomalies'    
        allData = sum(allData) / len(allData)
        finalData.append(allData)
    finalData = sum(finalData) / len(finalData)

    labelsize = 8 
    ax = map(20, labelsize)    
    #ax.set_extent([240, 359, 0, 70])

    plt.contourf(data.lon, data.lat, allData, origin='lower', levels = np.arange(-5, 5, .1), cmap = cmap.tempAnoms(), extend = 'both', transform=ccrs.PlateCarree(central_longitude=0))
    plt.title(f'ERSSTv5 {title}\n30-Year Sliding Climatology' , fontweight='bold', fontsize=labelsize, loc='left')
    plt.title(f'ASO {str(years)}', fontsize = labelsize, loc = 'center')
    plt.title('Deelan Jariwala', fontsize=labelsize, loc='right')  
    cbar = plt.colorbar(orientation = 'vertical', aspect = 50, pad = .02)
    cbar.ax.tick_params(axis='both', labelsize=labelsize, left = False, bottom = False)
    plt.savefig(r"C:\Users\deela\Downloads\ersstComposite.png", dpi = 400, bbox_inches = 'tight')
    plt.show()

# ens = pd.read_csv(r"C:\Users\deela\Downloads\ensoni - Sheet 1.csv")
# djf, aso, y = ens['DJF'], ens['ASO'], ens['Year']
# mdr = [-0.052272796630859375, -0.17194366455078125, 0.23615455627441406, 0.1637439727783203, -0.11080551147460938, 0.28420257568359375, -0.032947540283203125, 0.036407470703125, 0.0627899169921875, -0.5536613464355469, -0.6816844940185547, -0.08378219604492188, -0.9515323638916016, 0.17174911499023438, -0.3789501190185547, -0.0043125152587890625, 0.3968162536621094, -0.37538719177246094, -1.1127910614013672, -0.15764427185058594, -0.21110916137695312, 0.26096343994140625, 0.1300048828125, 0.8224601745605469, 1.311086654663086, 0.6103782653808594, -0.10337257385253906, 0.4593963623046875, 0.03600502014160156, -0.30264854431152344, -0.1669158935546875, -0.040843963623046875, -0.1558399200439453, 0.10546684265136719, 0.10534286499023438, -0.18398475646972656, -0.9181976318359375, 0.2702484130859375, -0.47132110595703125, -0.1476612091064453, -0.37827110290527344, -0.13409042358398438, 0.40207672119140625, 0.009111404418945312, -0.2497692108154297, -0.07927131652832031, -0.17272567749023438, 0.12897300720214844, -0.217041015625, -0.12728118896484375, -0.7999095916748047, -0.5454349517822266, -0.2010326385498047, -0.41636085510253906, -0.4693260192871094, -0.255401611328125, -0.31694984436035156, -0.4347400665283203, -0.22397804260253906, -0.6558589935302734, -0.1484241485595703, 0.6273002624511719, -0.09363365173339844, -0.5197734832763672, -0.01348876953125, 0.12992286682128906, -0.15722274780273438, -0.2911415100097656, -0.4525108337402344, -0.41232872009277344, -0.14225196838378906, -0.15987777709960938, 0.5073585510253906, 0.6921482086181641, 0.1989116668701172, -0.01030731201171875, 0.2746753692626953, 0.3604412078857422, 0.8169898986816406, 0.3772754669189453, 0.1409015655517578, 0.028041839599609375, 0.3537254333496094, 0.8067340850830078, 0.24578285217285156, 0.45827293395996094, 0.8267631530761719, 0.6225547790527344, 0.44991493225097656, 0.4356231689453125, 0.47699546813964844, 0.9758453369140625, 0.05226898193359375, -0.40227317810058594, -0.08351516723632812, 0.10346412658691406, 0.12612533569335938, 0.28884315490722656, 0.39818763732910156, 0.22906112670898438, -0.15210533142089844, 0.2504138946533203, -0.3334236145019531, 0.22816085815429688, 0.3836536407470703, -0.12410545349121094, -0.026163101196289062, 0.059661865234375, 0.019884109497070312, 0.08376312255859375, -0.256072998046875, -0.24162864685058594, 0.0077610015869140625, -0.15767478942871094, -0.19249343872070312, 0.26544952392578125, -0.17751121520996094, -0.3070945739746094, -0.48943138122558594, -0.21806716918945312, -0.41579437255859375, -0.2805347442626953, 0.086181640625, -0.12661361694335938, -0.10929679870605469, 0.13247299194335938, 0.3542976379394531, 0.20751380920410156, -0.1129608154296875, 0.13679122924804688, -0.12450981140136719, -0.0044841766357421875, -0.11985015869140625, 0.4623298645019531, 0.17912673950195312, 0.166778564453125, 0.5561923980712891, 0.0667266845703125, -0.108489990234375, -0.056308746337890625, -0.2806282043457031, 0.5209617614746094, 0.13951492309570312, 0.28435325622558594, 0.5256443023681641, 0.5369968414306641, 0.05571174621582031, 0.3815021514892578, 0.13848114013671875, 0.6026573181152344, 0.5722713470458984, 0.8663558959960938, 0.5587921142578125, -0.014001846313476562, 0.4936637878417969, 0.3950233459472656, 0.7067661285400391, 0.3381481170654297, 0.5847930908203125, 0.4680500030517578, 0.1382770538330078, 0.5295295715332031, 0.4210376739501953, 0.5455951690673828, -0.1617450714111328, 0.232696533203125, 0.3630256652832031, 0.19945526123046875, 0.2746295928955078, 1.1485710144042969]
# ninos = []
# ninas = []
# warmn = []
# cooln = []
# years = []
# for x in range(len(aso)):
#     if aso[x] > 0.5 and mdr[x] > 0.25:# and djf[x] < 0:
#         print(y[x], '\nMDR:', round(mdr[x], 2), '\nDJF ENSO:', djf[x], '\nASO ENSO:', aso[x], '\n')
#         years.append(y[x])
# #     if aso[x] > 0.5 and ndj[x] > 0.5:
# #         ninos.append(y[x])
# #     elif aso[x] < -0.5 and ndj[x] < -0.5:
# #         ninas.append(y[x])
# #     elif (aso[x] > 0 and aso[x] < 0.5) and (ndj[x] > 0 and ndj[x] < 0.5):
# #         warmn.append(y[x])
# #     elif (aso[x] < 0 and aso[x] > -0.5) and (ndj[x] < 0 and ndj[x] > -0.5):
# #         cooln.append(y[x])
# # print('El Nino', ninos, '\nWarm Neutral', warmn, '\nCool Neutral', cooln, '\nLa Nina', ninas)
# print(years)
    
#anomalies('9', years)#[2010, 1999, 2020, 1995, 1955, 2017, 2022, 2021, 1988, 1942, 1889, 1856, 1998])
analogs = [1878, 1933, 1942, 1995, 1998, 2005, 2010, 2020]
anomalies(['8', '9', '10'], analogs)#, True)