import xarray as xr
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import cmaps as cmap
from scipy.stats import pearsonr

dataset = xr.open_dataset(r"C:\Users\deela\Downloads\SHEARS_1997-2021.nc")
dataset = dataset.where(dataset.system_type.isin(['TD', 'TS', 'HU', 'TY', 'ST', 'TC']), drop=True)
dataset = dataset.where(dataset.sst > 26, drop=True)
dataset = dataset.where(dataset.dist_land != 0, drop=True)
dataset = dataset.where(dataset.rlhum.sel(upper = slice(300, 700)).mean('upper') > 40, drop = True)
dataset['case'] = np.arange(0, len(dataset.case.values))

uData = dataset['u_data']

max_num = 14
case_profile = uData[0,:]

fig, ax = plt.subplots(figsize=(5,5))

pca = PCA(n_components = max_num)
pca.fit(uData)

print(pca.components_.shape)
ax.plot(pca.explained_variance_ratio_[0:10]*100)
ax.plot(pca.explained_variance_ratio_[0:10]*100,'ro')
ax.set_title("% of variance explained", fontsize=14)
ax.grid()

fig, ax1 = plt.subplots(figsize=(5,5))

for i in range(1, max_num):
    X_train_pca2 = (uData.values - pca.mean_).dot(pca.components_[:i,:].T)
    print(X_train_pca2.shape)
    X_projected2 = X_train_pca2.dot(pca.components_[:i,:]) + pca.mean_
    print(X_projected2.shape)
    print(f"Error: {np.abs(X_projected2[0,:] - case_profile).sum().item()}")
    ax1.plot(X_projected2[0,:], case_profile.upper, label=f'EOF {i}')

ax1.legend()
case_profile.plot(y="upper", ax=ax1, label='Case profile', lw=2)
plt.show()