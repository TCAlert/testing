import xarray as xr
import matplotlib.pyplot as plt
import satcmaps as cmaps 
import numpy as np 
from matplotlib import rcParams 
import cartopy, cartopy.crs as ccrs 
import bdeck as bdeck 
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import cmaps as cmap 
from scipy.ndimage import gaussian_filter
from scipy import ndimage

labelsize = 9

def add_storm_dim(dataset):
    dataset = dataset.assign_coords(case=("case", dataset["case_number_global"].values))
    
    return dataset

def _rotate2d(arr2d, angle_deg):
    # Rotate around the array center, keep same shape
    # Use cval=np.nan so empty corners become NaN rather than 0
    return ndimage.rotate(arr2d,
                          angle=float(angle_deg),
                          reshape=False,
                          order=1,          # bilinear; use 0 for nearest
                          mode='constant',
                          cval=np.nan)

def getAngles(dataset, caseList):
    l = []
    for x in range(len(caseList)):
        value = caseList[x]
        # if value >= 710:
        #     value = value - 710
        temp = dataset.isel(num_cases = value)
        l.append(temp.values)
    
    return np.array(l)

def meanError(data, tilts):    
    print(np.mean(np.abs(data - tilts)))

print([r"C:\Users\deela\Downloads\split" + str(x) +"_analysis.nc" for x in range(1, 5)])

data = xr.open_mfdataset([r"C:\Users\deela\Downloads\split" + str(x) +"_analysis.nc" for x in range(1, 5)], preprocess = add_storm_dim)
print(list(data.variables))

tcradar = xr.open_mfdataset([r"C:\Users\deela\Downloads\tc_radar_v3m_1997_2019_xy_rel_swath_ships.nc", r"C:\Users\deela\Downloads\tc_radar_v3m_2020_2024_xy_rel_swath_ships.nc"], concat_dim='num_cases', combine='nested')
sddc = tcradar["sddc_ships"].sel(ships_lag_times=0)
angles = getAngles(sddc, data.case_number_global.values)

tilt = data['density_model']
meanError(((data['predx_mean'].values)**2 + (data['predy_mean'].values**2))**0.5, ((data['obsx'].values)**2 + (data['obsy'].values**2))**0.5)
meanError(((data['climoXsv'].values)**2 + (data['climoYsv'].values**2))**0.5, ((data['obsx'].values)**2 + (data['obsy'].values**2))**0.5)

tilt = xr.apply_ufunc(
    _rotate2d,
    tilt,                 # (case,y,x)
    angles,               # (case,)
    input_core_dims=[['density_y','density_x'], []],
    output_core_dims=[['density_y','density_x']],
    vectorize=True,       # iterate over non-core dims (i.e., 'case')
    dask='parallelized',
    output_dtypes=[tilt.dtype],
)
# plt.imshow(tilt)
# plt.show()

clim = data['density_climosv']
clim = xr.apply_ufunc(
    _rotate2d,
    clim,                 # (case,y,x)
    angles,               # (case,)
    input_core_dims=[['density_y', 'density_x'], []],
    output_core_dims=[['density_y','density_x']],
    vectorize=True,       # iterate over non-core dims (i.e., 'case')
    dask='parallelized',
    output_dtypes=[clim.dtype],
)

caseNum = 1044

diff = (tilt).sel(case = caseNum)
# diff.values = gaussian_filter(diff, sigma = .5)

meanOX = data['obsx'].sel(case = caseNum)
meanOY = data['obsy'].sel(case = caseNum)

meanCX = data['climoXsv'].sel(case = caseNum)
meanCY = data['climoYsv'].sel(case = caseNum)

meanMX = data['predx_mean'].sel(case = caseNum)
meanMY = data['predy_mean'].sel(case = caseNum)

plt.figure(figsize = (14, 12))
ax = plt.axes()
ax.set_frame_on(False)
plt.grid(linewidth = .5, color='black', alpha=0.5, linestyle='--')   
# ax.set_xlim(-75, 75)
ax.set_xlabel('Zonal Distance', fontsize = labelsize)
# ax.set_ylim(-75, 75)
ax.set_ylabel('Meridional Distance', fontsize = labelsize)

c = plt.pcolormesh(diff.density_x, diff.density_y, diff.values, vmin = 0.0, vmax = 0.05, cmap = cmap.probs())
# c = plt.contourf(diff.density_x, diff.density_y, diff.values, levels = np.arange(-0.01, 0.01 + 0.0001, 0.0001), cmap = cmap.tempAnoms3(), extend = 'both')

# plt.scatter(meanOX, meanOY, c = 'black', label = 'Observed MLC')
# plt.scatter(meanCX, meanCY, c = 'Magenta', label = 'Climo MLC')
# plt.scatter(meanMX, meanMY, c = 'green', label = 'TILT MLC')

# plt.legend()

plt.title(f'TILT RF Model Prediction Density\nAverage of Splits' , fontweight='bold', fontsize=labelsize, loc='left')
plt.title(f'TC-RADAR', fontsize=labelsize, loc='right')  
cbar = plt.colorbar(c, orientation = 'vertical', aspect = 50, pad = .02)
# plt.savefig(r"C:\Users\deela\Downloads\tiltValueAll.png", dpi = 400, bbox_inches = 'tight')
plt.show()