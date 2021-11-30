import matplotlib.pyplot as plt  
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy as np
import pandas as pd
from datetime import datetime
from cartopy.io import shapereader
import cartopy.io.shapereader as shpreader
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.patches as mpatches

def casesP(cdate, ctotal, ctdeath, cvax, country, fig):
    ax1 = fig.add_subplot(2, 2, 2)
    ax1.set_facecolor('whitesmoke')

    ax1.get_yaxis().get_major_formatter().set_scientific(False)
    ax1.set_ylabel(r'$\bf{Total}$' + " " + r'$\bf{Cases}$')

    ax2 = ax1.twinx()
    ax2.set_ylabel(r'$\bf{Total}$' + " " + r'$\bf{Deaths}$')

    ax1.plot(cdate, ctotal, linewidth = 4, color = 'purple')
    #ax1.plot(cdate, cvax, linewidth = 4, color = 'mediumaquamarine')
    ax2.plot(cdate, ctdeath, linewidth = 4, color = 'plum')

    tc = mpatches.Patch(color = 'purple', label = "Total Cases")
    td = mpatches.Patch(color = 'plum', label = "Total Deaths")
    ax1.legend(handles=[tc, td])        

    ax1.grid(True)
    ax1.set_xlim(xmin = cdate[40])
    ax1.set_title(f"Cumulative Cases, and Deaths\n{country.upper()}", fontweight='bold', fontsize=10, loc = 'left')
    ax1.set_title(f"As of {cdate[-1]}", fontsize=10, loc = 'right')
    ax1.axes.xaxis.set_ticklabels([])
    ax1.grid(True)

def cases(cdate, cndeath, cnew, country, fig):
    total = fig.add_subplot(2, 2, 4)
    total.set_facecolor('whitesmoke')

    total.get_yaxis().get_major_formatter().set_scientific(False)
    total.set_ylabel(r'$\bf{Daily}$' + " " + r'$\bf{Deaths}$')

    daily = total.twinx()
    daily.set_ylabel(r'$\bf{Daily}$' + " " + r'$\bf{Cases}$')

    total.bar(cdate, cndeath, color = 'lightslategrey')
    daily.plot(cdate, cnew, linewidth = 4, color = 'darkslateblue')
    daily.scatter(cdate[-1], cnew[-1], color = 'salmon', zorder = 9)
    daily.scatter(cdate[-8], cnew[-8], color = 'salmon', zorder = 9)
    daily.plot([cdate[-1], cdate[-8]], [cnew[-1], cnew[-8]], linewidth = 3, color = 'black')
    daily.annotate(f"{str(cnew[-1])} Cases\n(7 Day Change: {str(round(cnew[-1] - cnew[-8], 1))})", xy = (cdate[-1], cnew[-1]), xytext=(cdate[int(len(cdate) * -0.75)], cnew[-1] - (cnew[-1] * 0.5)))

    tc = mpatches.Patch(color = 'lightslategrey', label = "New Deaths")
    tn = mpatches.Patch(color = 'darkslateblue', label = "New Cases")
    total.legend(handles=[tc, tn])        
    
    total.set_xlabel(r"$\bf{Date}$", labelpad=4)
    total.set_xlim(xmin = cdate[40])
    total.grid(True)
    total.set_title(f"Smoothed Daily Cases and Deaths\n{country.upper()}", fontweight='bold', fontsize=10, loc = 'left')
    total.set_title(f"As of {cdate[-1]}", fontsize=10, loc = 'right')
    total.grid(True)

def covid(country):
    fig = plt.figure(figsize=(24, 10))

    data = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")

    loc = data['location']
    date = data['date']
    total = data['total_cases']
    new = data['new_cases_smoothed']
    pop = data['population']
    tdeath = data['total_deaths']
    ndeath = data['new_deaths_smoothed']
    dens = data['population_density']
    life = data['life_expectancy']
    gdp = data['gdp_per_capita']
    vax = data['total_vaccinations']
    print('Data retrieved')

    cdate = []
    ctotal = []
    cnew = []
    ctdeath = []
    cndeath = []
    cvax = []
    for x in range(len(loc)):
        if loc[x].lower() == country.lower():
            cdate.append(date[x])
            ctotal.append(total[x])
            cnew.append(round(new[x], 2))
            ctdeath.append(tdeath[x])
            cndeath.append(ndeath[x])
            cvax.append(vax[x])
        
            gdppc = gdp[x]
            expectancy = life[x]
            density = dens[x]
            population = pop[x]
    cdate = [datetime.strptime(date, '%Y-%m-%d').date() for date in cdate]

    print('Plotting data')
    fig.set_facecolor('snow')

    text = fig.add_subplot(1, 2, 1)
    text.set_xticks([])
    text.set_yticks([])
    text.set_title('SARS-CoV-2 (COVID-19) Data', fontweight = 'bold', fontsize = 20, loc = 'left')
    text.set_title('Made by TCAlert \nUsing data from https://ourworldindata.org', fontstyle = 'italic', fontsize = 10, color = "gray", loc = 'right')
    text.set_facecolor('whitesmoke')

    text.text(0.18, 0.93, f'Latest Data',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 17, color = "black")
    text.text(0.18, 0.84, f'Total Cases: {str((ctotal[-1]))}\nTotal Deaths: {str((ctdeath[-1]))}\nNew Cases: {str((cnew[-1]))}\nNew Deaths: {str(round(cndeath[-1], 0))}',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, color = "gray")
    text.text(0.82, 0.93, f'Country Stats',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 17, color = "black")
    text.text(0.82, 0.84, f'Population: {str((population))}\nPop Density: {str(round(density, 2))}\nLife Expentancy: {str((expectancy))}\nGDP Per Capita: {str(round(gdppc, 2))}',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, color = "gray")

    text.text(0.5, 0.70, f'Data Sources per OWD',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 17, color = "black")
    text.text(0.5, 0.61, f'Confirmed cases and deaths\nHospitalizations and ICU admissions\nTesting\nVaccinations',
            horizontalalignment= 'center', verticalalignment = 'center', fontsize = 15, color = "gray")


    mp = fig.add_subplot(2, 2, 3, projection=ccrs.PlateCarree(central_longitude=0))

    shpfilename = shpreader.natural_earth(resolution='10m',
                                      category='cultural',
                                      name='admin_0_countries')
    reader = shpreader.Reader(shpfilename)
    countries = reader.records()

    for x in countries:
        if x.attributes['NAME_LONG'].lower() == country.lower():
            mp.add_geometries(x.geometry, ccrs.PlateCarree(),
                              facecolor = 'salmon',
                              label=x.attributes['NAME_LONG'])
    mp.add_feature(cartopy.feature.COASTLINE.with_scale('10m'))
    mp.add_feature(cartopy.feature.BORDERS.with_scale('10m'))
    mp.add_feature(cartopy.feature.OCEAN, facecolor = 'whitesmoke')
    mp.add_feature(cartopy.feature.LAND, facecolor = 'whitesmoke')

    mp.outline_patch.set_visible(False)
    mp.set_facecolor('whitesmoke')
    mp.set_title("Map", fontweight = 'bold')
    cases(cdate, cndeath, cnew, country, fig)
    casesP(cdate, ctotal, ctdeath, cvax, country, fig)

    print('Plotting complete')
    plt.savefig(r"C:\Users\[Username]\Downloads\covidMap.png", dpi = 300, bbox_inches = 'tight', facecolor=fig.get_facecolor())
    plt.show()
    plt.close()
    
# Sample Usage
# covid("United States")
