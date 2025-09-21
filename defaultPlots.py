import matplotlib.pyplot as plt
import numpy as np 
from sklearn import linear_model
import scipy
import cmaps as cmap 

LABELSIZE = 8

def scatter(x, y, vline = True, hline = True, title = None, z = None):    
    fig = plt.figure(figsize=(14, 11))
    ax = plt.axes()

    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=LABELSIZE, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_xlabel(f'{x[0]}', weight = 'bold', size = 9)
    ax.set_ylabel(f'{y[0]}', weight = 'bold', size = 9)
    
    if vline == True:
        ax.axvline(color = 'black')
    if hline == True:
        ax.axhline(color = 'black')

    print(len(x[1]), y[1].shape)
    if z == None:
        ax.scatter(x[1], y[1], c = 'black', linewidth = 2)
    else:
        s = ax.scatter(x[1], y[1], c = z[1], cmap = cmap.probs2(), linewidth = 2)
        cbar = plt.colorbar(s, orientation = 'vertical', aspect = 50, pad = .02, extend = 'max')
        cbar.set_label(z[0])

    tempX, tempY = x[1][(~np.isnan(x[1]) & ~np.isinf(x[1])) & (~np.isnan(y[1]) & ~np.isinf(y[1]))], y[1][(~np.isnan(x[1]) & ~np.isinf(x[1])) & (~np.isnan(y[1]) & ~np.isinf(y[1]))]
    corr, sig = scipy.stats.pearsonr(np.nan_to_num(tempX), np.nan_to_num(tempY))
    
    regr = linear_model.LinearRegression()
    regr.fit(tempX.reshape(-1, 1), tempY.reshape(-1, 1))
    coef, intr = regr.coef_[0][0], regr.intercept_[0]
    print(regr.coef_)

    print(np.nanmin(tempX), np.nanmax(tempX))
    bogusX = np.linspace(np.nanmin(tempX), np.nanmax(tempX))

    ax.plot(bogusX, (coef * bogusX) + intr, linewidth = 2, color = 'black')

    if title == None:
        ax.set_title(f'{x[0]}/{y[0]} Scatterplot\nn = {len(x[1])}, R^2 = {str(round(corr**2, 2))}, y = {coef}x + ({intr})', fontweight='bold', fontsize=LABELSIZE + 1, loc='left')      
    else:
        ax.set_title(f'{title} {x[0]}/{y[0]} Scatterplot\nn = {len(x[1])}, R^2 = {str(round(corr**2, 2))}, y = {coef}x + ({intr})', fontweight='bold', fontsize=LABELSIZE + 1, loc='left')  
    ax.set_title(f'Deelan Jariwala', fontsize=LABELSIZE + 1, loc='right')  
    try:
        plt.savefig(r"C:\Users\deela\Downloads\scatter" + x[0] + r"_" + y[0] + r".png", dpi = 400, bbox_inches = 'tight')
    except:
        pass
    plt.show()

def histogram(data, bounds = None, title = None, save = False):
    if bounds == None:
        bounds = [0, 1, 2]
        bounds[0] = np.nanmin(data[1])
        bounds[1] = np.nanmax(data[1])
        bounds[2] = (bounds[1] - bounds[0]) / 10

    fig = plt.figure(figsize=(14, 7))

    # Add the map and set the extent
    ax = plt.axes()
    ax.set_frame_on(False)
    ax.tick_params(axis='both', labelsize=8, left = False, bottom = False)
    ax.grid(linestyle = '--', alpha = 0.5, color = 'black', linewidth = 0.5, zorder = 9)
    ax.set_ylabel('Count', weight = 'bold', size = 9)
    ax.set_xlabel(f'{data[0]}', weight = 'bold', size = 9)

    if title == None:
        plt.title(f'Histogram of {data[0]}\nNumber of Valid Datapoints: {len(data[1])}' , fontweight='bold', fontsize=LABELSIZE + 1, loc='left')
    else:
        plt.title(f'{title}\nNumber of Valid Datapoints: {len(data[1])}' , fontweight='bold', fontsize=LABELSIZE + 1, loc='left')
    plt.title(f'Deelan Jariwala', fontsize=LABELSIZE + 1, loc='right')  
    plt.hist(data[1], bins = np.arange(bounds[0], bounds[1], bounds[2]), color = '#9f80ff', alpha = 0.75)
    if save == True:
        plt.savefig(r"C:\Users\deela\Downloads\histogram_" + str(data[0]) + ".png", dpi = 400, bbox_inches = 'tight')
    plt.show()