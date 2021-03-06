import matplotlib.pyplot as plt  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy as np
import goesRequest as goes

# Mesoscale Floater plotting tool              #
# ----------- Variable Description ----------- #
# Satt - Satellite chose, either east or west  #
# Loc - Floater one or floater two             #
# Bands - List of bands to use in a composite  #
# Flag - Make this to "t" use synthetic green  #
def run(satt, loc, bands, flag = 'f'):
    data = ["", "", ""]
    datl = []
    avg = []
    for x in range(len(bands)):
        satellite = satt.capitalize()
        band = bands[x]
        sector = f'Mesoscale-{loc}'
        data[x], time, info, center = goes.getData(satellite.lower(), str(abs(int(band))), sector)
        datl.append(int(band))

        if int(band) < 0:
            data[x].values = 1 - data[x].values
            band = str(abs(int(band)))

        avg.append(np.average(data[0]))

        if (flag).lower() == 't' and int(band) == 3:
            b, time, info, center = goes.getData(satellite.lower(), '1', sector)
            r, time, info, center = goes.getData(satellite.lower(), '2', sector)
            g, time, info, center = goes.getData(satellite.lower(), '3', sector)

            data[x].values = 0.45 * r[::2, ::2].values + 0.1 * g.values + 0.45 * b.values

        if int(band) >= 7:
            data[x] = (data[x] - data[x].max())/(data[x].min() - data[x].max())
        else:
            data[x] = np.clip(data[x], 0, 1)

        if (int(bands[0]) != int(bands[1])) or (int(bands[1]) != int(bands[2])):
            if all(y in ['1', '2', '3', '5'] for y in bands) == True:
                if int(band) == 2:
                    data[x] = data[x][::2, ::2]
            else:
                if int(band) == 2:
                    data[x] = data[x][::4, ::4]
                if int(band) in [1, 3, 5]:
                    data[x] = data[x][::2, ::2]

    composite = np.dstack(data)
    if bands == ['2', '2', '2'] or bands == ['2', '3', '1']:
        if (avg[2]) > 0.3:
            composite = (composite**(4/3))   
        else:
            composite = (composite**(3/4))         

    l = list(composite.shape)
    plt.figure(figsize = (10, 10))

    bands = [int(x) for x in bands]

    if l[0] == 500:
        l[0] = '2km'
    elif l[0] == 1000:
        l[0] = '1km'
    else: 
        l[0] = '0.5km' 

    ax = plt.axes(projection=ccrs.Geostationary(central_longitude=-75.0, satellite_height=35786023.0))
    ax.imshow(composite, origin = 'upper')
    if 3 in bands and flag == 't':
        plt.title(f'GOES {satellite.capitalize()} Channel {bands} Mesoscale Sector {loc} w/ Modified Band 03 data\n{time}' , fontweight='bold', fontsize=10, loc='left')
    else:
        plt.title(f'GOES {satellite.capitalize()} Channel {bands} Mesoscale Sector {loc}\n{time}' , fontweight='bold', fontsize=10, loc='left')
    plt.title(f'TCAlert\nResolution: {l[0]}', fontsize=10, loc='right')
    plt.savefig(r"C:\Users\Username\Downloads\goesmeso.png", dpi = 400, bbox_inches = 'tight')
    plt.show()
    plt.close()
