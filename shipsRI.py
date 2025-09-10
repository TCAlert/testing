import pickle
import numpy as np 
from matplotlib import patheffects 
import matplotlib.pyplot as plt  # Plotting library
import satcmaps as cmaps 
import SHIPSRetrieve as ships

with open(r"C:\Users\deela\Downloads\SHIPS_RF_RI.cpickle", 'rb') as f:
    regr = pickle.load(f)

def plot(stime, SST, VMax, RH, DSHR, DDIR, MPI, LAT, SLAT, CLAT, RH24, VMAXd12, SHR24, DIST12, DIST24, DIV, T200, OHC, TADV):
       feature = np.array([SST, VMax, RH, DSHR, DDIR, VMax - MPI, SLAT, CLAT, RH24, VMAXd12, SHR24, DIST12, DIST24, DIV, T200, OHC, TADV])
       feat = np.array(feature).reshape(1, -1)
       fig = plt.figure(figsize=(14, 7))

       # Add the map and set the extent
       ax = plt.axes()
       ax.set_frame_on(False)
       ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
       ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
       ax.set_ylabel('Density', weight = 'bold', size = 9)
       ax.set_xlabel(f'Prediction (kt)', weight = 'bold', size = 9)
       ax.set_ylim(0, 0.05)

       predArray = np.array([tree.predict(feat) for tree in regr.estimators_]) + VMax# Shape: (n_trees, test)
       predSTD = np.nanstd(predArray, axis = 0)[0] 
       pred = regr.predict(feat)[0] + VMax

       # print(np.sum(predArray - VMax >= 30))
       count = int((np.sum(predArray - VMax >= 30) / len(predArray)) * 100)

       text = f"\nVMax:             {VMax} kt\n" \
              f"ML RH:                {RH}%\n" \
              f"MPI:                {MPI} kt\n" \
              f"LAT:                 {LAT}N\n" \
              f"SST:                  {SST}C" 
       ax.text(-7.5, 0.0035, text, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75})
       ax.text(-7.5, 0.002, f"-------------------------------", bbox={'facecolor': 'None', 'edgecolor': 'None', 'alpha': 0.75})
       ax.text(-7.5, 0.0004, f"Prediction:   {round(pred, 1)} kt", color = 'red', bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75})


       u, v = -DSHR * np.sin(DDIR), -DSHR * np.cos(DDIR)

       ax.text(2.5, 0.0485, f'200-850mb', color = 'black', fontsize = 8, ha = 'center', fontweight = 'bold', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75})
       ax.quiver(2.5, 0.046, np.array([u]) / DSHR, np.array([v]) / DSHR, pivot = 'middle', scale = 30, minshaft = 3, minlength=0, headaxislength = 3, headlength = 3, color = '#ff5959', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="black")])
       ax.text(2.5, 0.0425, f'{round(DSHR, 1)} knots', fontsize = 8, color = 'black', ha = 'center', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.75})

       plt.title(f'SHIPS-Based Random Forest 24hr Intensity Prediction\nNumber of Predictions: {len(predArray)}' , fontweight='bold', fontsize=8 + 1, loc='left')
       plt.title(f'Forecast Time: {stime}', fontsize=8 + 1, loc='center')
       plt.title(f'RI Probability: {count}%\nDeelan Jariwala & Zach Nice', fontsize=8 + 1, loc='right')  
       plt.hist(predArray, bins = np.arange(0, 160, 5), color = '#9f80ff', alpha = 0.5, density = True)
       plt.axvspan(pred - predSTD, pred + predSTD, color = 'red', alpha = 0.25, zorder = 0)
       plt.axvline(pred, color = 'red', label = f'Prediction: {round(pred, 1)}kt')
       length = pred - VMax
       
       if length > 0:
              length = length - 2
       else:
              length = length + 2
       ax.text((VMax + pred) / 2, 0.026, f'{round(pred - VMax, 1)} kt', fontsize = 8, color = 'black', ha = 'center', path_effects = [patheffects.withStroke(linewidth=1.25, foreground="white")], zorder = 20)#, bbox={'facecolor': 'white', 'edgecolor': 'None', 'alpha': 0.25})
       ax.quiver((VMax + pred) / 2, 0.025, length, 0, pivot = 'middle', scale = 1, scale_units = 'xy', minshaft = 4, minlength=0, headaxislength = 3, headlength = 3, color = '#000000', zorder = 20, path_effects = [patheffects.withStroke(linewidth=1.25, foreground="black")])
       plt.axvline(VMax, color = 'black', label = f'Current Intensity: {round(VMax, 1)}kt')
       plt.savefig(r"C:\Users\deela\Downloads\shipsRIRF.png", dpi = 400, bbox_inches = 'tight')
       plt.legend(loc = 'upper right')
    #    plt.show()


def getShips(storm, year, month, day, hour):
    try:
          line, stime, ri, an, link, VMAXd12 = ships.ships(storm, str(year)[2:4], str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2))
    except:
          line, stime, ri, an, link, VMAXd12 = ships.ships(storm, str(year)[2:4], str(month).zfill(2), str(day).zfill(2))

    SST = float(line[6, 1])
    VMax = float(line[1, 1])
    RH = float(line[11, 1])
    DSHR = float(line[3, 1])
    DDIR = float(line[5, 1])
    MPI = float(line[7, 1])
    lat = float(line[17, 1])
    SLAT, CLAT = np.sin(np.deg2rad(lat)), np.cos(np.deg2rad(lat))
    RH24 = float(line[11, 5])
    SHR24 = float(line[3, 5])
    DIST12 = float(line[16, 3])
    DIST24 = float(line[16, 5])
    DIV = float(line[14, 1])
    T200 = float(line[8, 1])
    TADV = float(line[15, 1])
    OHC = float(line[20, 1])
    VMAXd12 = VMax - VMAXd12
    print(f'12 Hour Trend: {VMAXd12}kt')

    plot(stime, SST, VMax, RH, DSHR, DDIR, MPI, lat, SLAT, CLAT, RH24, VMAXd12, SHR24, DIST12, DIST24, DIV, T200, OHC, TADV)