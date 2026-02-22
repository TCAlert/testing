import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import h5py

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    CARTOPY_AVAILABLE = True
except Exception:
    CARTOPY_AVAILABLE = False

try:
    from scipy.ndimage import gaussian_filter

    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False
    gaussian_filter = None

try:
    from scipy import stats as sp_stats
except Exception:
    sp_stats = None

DATA_PATH = r"C:\Users\deela\Downloads\HURDAT2DensityNATL.nc"

# Variables to plot (spatial trend of anomalies).
VARS = ["ACE", "wind", "RI", "24hrChange"]

# Satellite-era start (use to reduce observational bias).
SAT_START_YEAR = 1980

# Minimum number of valid years required per grid cell.
MIN_YEARS = 10

# Dynamic climatology window (prior N years).
CLIM_WINDOW_YEARS = 30

# Smoothing settings to reduce noise without blockiness.
SMOOTH_METHOD = "gaussian"  # "gaussian", "block", or "none"
SMOOTH_SIGMA = 1.2
SMOOTH_FACTOR = 2  # used only when SMOOTH_METHOD == "block"

# Significance settings
SIGNIFICANCE_LEVEL = 0.05
STIPPLE_STRIDE = 2

# Style settings
TITLE_COLOR = "#2d2a2a"
OCEAN_COLOR = "#dfeaf2"
LAND_COLOR = "#efe6da"
COAST_COLOR = "#3d3d3d"


def decode_time(units, values):
    if isinstance(units, bytes):
        units = units.decode("utf-8")
    origin = units.split("since")[-1].strip().split(" ")[0]
    return pd.to_datetime(values, unit="D", origin=pd.Timestamp(origin))


def compute_annual_totals(arr, year_groups):
    # Aggregate to annual totals (one value per year).
    y_size, x_size = arr.shape[1], arr.shape[2]
    annual = np.full((len(year_groups), y_size, x_size), np.nan, dtype=np.float64)
    for j, sel in enumerate(year_groups):
        if sel.size == 0:
            continue
        data = arr[sel]
        valid_count = np.sum(np.isfinite(data), axis=0)
        annual_sum = np.nansum(data, axis=0)
        annual_sum[valid_count == 0] = np.nan
        annual[j] = annual_sum
    return annual


def dynamic_baseline(annual, window):
    # Mean of the prior N years at each grid cell (exclusive of current year).
    valid = np.isfinite(annual)
    a0 = np.where(valid, annual, 0.0)
    csum = np.cumsum(a0, axis=0)
    ccount = np.cumsum(valid.astype(float), axis=0)

    baseline = np.full_like(annual, np.nan, dtype=np.float64)
    for i in range(annual.shape[0]):
        if i < window:
            continue
        end = i - 1
        start = i - window
        sum_window = csum[end] - (csum[start - 1] if start > 0 else 0.0)
        cnt_window = ccount[end] - (ccount[start - 1] if start > 0 else 0.0)
        baseline[i] = sum_window / np.where(cnt_window == 0, np.nan, cnt_window)
    return baseline


def slope_from_anom(anom, years, idx):
    # Linear trend on annual anomalies.
    anom_sel = anom[idx]
    t = years[idx].astype(float)
    t0 = t - t.mean()

    valid = np.isfinite(anom_sel)
    count = np.sum(valid, axis=0)
    sum_t = np.sum(t0[:, None, None] * valid, axis=0)
    sum_y = np.nansum(anom_sel, axis=0)
    sum_tt = np.sum((t0[:, None, None] ** 2) * valid, axis=0)
    sum_ty = np.nansum(anom_sel * t0[:, None, None], axis=0)
    sum_y2 = np.nansum(anom_sel ** 2, axis=0)

    denom = sum_tt - (sum_t ** 2) / np.where(count == 0, np.nan, count)
    numer = sum_ty - (sum_t * sum_y) / np.where(count == 0, np.nan, count)
    slope = np.where(denom != 0, numer / denom, np.nan)
    intercept = np.where(count != 0, (sum_y - slope * sum_t) / count, np.nan)

    sse = (
        sum_y2
        - 2 * intercept * sum_y
        - 2 * slope * sum_ty
        + count * intercept ** 2
        + 2 * slope * intercept * sum_t
        + slope ** 2 * sum_tt
    )
    dof = count - 2
    mse = np.where(dof > 0, sse / dof, np.nan)
    se_slope = np.sqrt(mse / denom)
    t_stat = slope / se_slope

    if sp_stats is not None:
        p_val = 2 * (1 - sp_stats.t.cdf(np.abs(t_stat), df=dof))
    else:
        p_val = 2 * (1 - 0.5 * (1 + np.erf(np.abs(t_stat) / np.sqrt(2))))

    slope[count < MIN_YEARS] = np.nan
    p_val[count < MIN_YEARS] = np.nan
    return slope, p_val


def block_mean_1d(arr, factor):
    if factor <= 1:
        return arr
    n = (arr.shape[0] // factor) * factor
    arr = arr[:n]
    return arr.reshape(n // factor, factor).mean(axis=1)


def block_mean_2d(arr, factor):
    if factor <= 1:
        return arr
    y = (arr.shape[0] // factor) * factor
    x = (arr.shape[1] // factor) * factor
    arr = arr[:y, :x]
    arr = arr.reshape(y // factor, factor, x // factor, factor)
    return np.nanmean(arr, axis=(1, 3))


def smooth_map(arr):
    if SMOOTH_METHOD == "gaussian":
        if SCIPY_AVAILABLE:
            return gaussian_filter(arr, sigma=SMOOTH_SIGMA, mode="nearest")
        return block_mean_2d(arr, SMOOTH_FACTOR) if SMOOTH_FACTOR > 1 else arr
    if SMOOTH_METHOD == "block":
        return block_mean_2d(arr, SMOOTH_FACTOR) if SMOOTH_FACTOR > 1 else arr
    return arr


def mask_to_plot_grid(mask):
    if SMOOTH_METHOD == "block" and SMOOTH_FACTOR > 1:
        return block_mean_2d(mask.astype(float), SMOOTH_FACTOR) > 0.5
    return mask


with h5py.File(DATA_PATH, "r") as f:
    time = f["time"][:]
    time_units = f["time"].attrs.get("units", b"")
    dates = decode_time(time_units, time)
    years = dates.year.values
    uniq_years = np.unique(years)
    year_groups = [np.where(years == yr)[0] for yr in uniq_years]

    lat = f["latitude"][:].astype(float)
    lon = f["longitude"][:].astype(float)
    if SMOOTH_METHOD == "block" and SMOOTH_FACTOR > 1:
        lat_plot = block_mean_1d(lat, SMOOTH_FACTOR)
        lon_plot = block_mean_1d(lon, SMOOTH_FACTOR)
    else:
        lat_plot = lat
        lon_plot = lon

    idx_full = np.arange(len(uniq_years))
    idx_sat = np.where(uniq_years >= SAT_START_YEAR)[0]

    periods = [
        ("Full record", idx_full),
        (f"{SAT_START_YEAR}+", idx_sat),
    ]

    slopes = {}
    pvals = {}
    for var in VARS:
        if var not in f:
            print(f"Skipping {var}: not found in dataset.")
            continue
        data = np.asarray(f[var][:], dtype=np.float32)
        annual = compute_annual_totals(data, year_groups)
        baseline = dynamic_baseline(annual, CLIM_WINDOW_YEARS)
        anom = annual - baseline

        slopes[var] = []
        pvals[var] = []
        for _, idx in periods:
            slope, p_val = slope_from_anom(anom, uniq_years, idx)
            slopes[var].append(slope * 10.0)  # per decade
            pvals[var].append(p_val)


mpl.rcParams.update(
    {
        "figure.figsize": (16, 12),
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.edgecolor": "#2f2f2f",
        "axes.facecolor": "#fbf7f2",
        "figure.facecolor": "#fbf7f2",
        "grid.color": "#c9c2b8",
        "grid.linewidth": 0.6,
        "font.size": 11,
        "savefig.dpi": 120,
    }
)

cmap = mpl.cm.get_cmap("RdYlBu_r")


def plot_group(vars_group, title):
    if CARTOPY_AVAILABLE:
        proj = ccrs.PlateCarree()
        fig, axes = plt.subplots(
            len(vars_group),
            len(periods),
            figsize=(16, 12),
            constrained_layout=True,
            subplot_kw={"projection": proj},
        )
    else:
        print("Cartopy not available. Falling back to plain pcolormesh (no coastlines).")
        fig, axes = plt.subplots(len(vars_group), len(periods), figsize=(16, 12), constrained_layout=True)

    if len(vars_group) == 1:
        axes = np.array([axes])

    if CARTOPY_AVAILABLE:
        lon2d_plot, lat2d_plot = np.meshgrid(lon_plot, lat_plot)

    if SMOOTH_METHOD == "gaussian":
        if SCIPY_AVAILABLE:
            smooth_desc = f"gaussian (sigma={SMOOTH_SIGMA})"
        else:
            smooth_desc = f"block-mean fallback ({SMOOTH_FACTOR}x)"
    elif SMOOTH_METHOD == "block":
        smooth_desc = f"block-mean ({SMOOTH_FACTOR}x)"
    else:
        smooth_desc = "none"

    for r, var in enumerate(vars_group):
        if var not in slopes:
            for c in range(len(periods)):
                axes[r, c].axis("off")
            continue

        slope_maps = [smooth_map(s) for s in slopes[var]]
        sig_maps = [mask_to_plot_grid(p < SIGNIFICANCE_LEVEL) for p in pvals[var]]
        all_vals = np.concatenate([s.ravel() for s in slope_maps])
        all_vals = all_vals[np.isfinite(all_vals)]
        if all_vals.size == 0:
            vmax = 1.0
        else:
            vmax = np.nanpercentile(np.abs(all_vals), 98)
            if vmax == 0:
                vmax = 1.0
        norm = mpl.colors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
        levels = np.linspace(-vmax, vmax, 23)

        for c, (label, _) in enumerate(periods):
            ax = axes[r, c]
            if CARTOPY_AVAILABLE:
                im = ax.contourf(
                    lon2d_plot,
                    lat2d_plot,
                    slope_maps[c],
                    levels=levels,
                    cmap=cmap,
                    norm=norm,
                    transform=proj,
                    extend="both",
                )
                ax.add_feature(cfeature.OCEAN, facecolor=OCEAN_COLOR, edgecolor="none", zorder=0)
                ax.add_feature(cfeature.LAND, facecolor=LAND_COLOR, edgecolor="none", zorder=1)
                ax.add_feature(cfeature.COASTLINE, linewidth=0.7, edgecolor=COAST_COLOR, zorder=2)
                ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="#666666", zorder=2)
                ax.set_extent([lon_plot.min(), lon_plot.max(), lat_plot.min(), lat_plot.max()], crs=proj)

                gl = ax.gridlines(draw_labels=True, linewidth=0.2, color="#888888", alpha=0.5, linestyle="--")
                gl.top_labels = False
                gl.right_labels = False
                gl.left_labels = c == 0
                gl.bottom_labels = r == len(vars_group) - 1
                gl.xlabel_style = {"size": 9}
                gl.ylabel_style = {"size": 9}
            else:
                im = ax.contourf(
                    lon_plot,
                    lat_plot,
                    slope_maps[c],
                    levels=levels,
                    cmap=cmap,
                    norm=norm,
                    extend="both",
                )
                ax.set_xlabel("lon")
                if c == 0:
                    ax.set_ylabel("lat")

            sig = sig_maps[c]
            if STIPPLE_STRIDE > 1:
                sig = sig[::STIPPLE_STRIDE, ::STIPPLE_STRIDE]
                if CARTOPY_AVAILABLE:
                    lon_s = lon2d_plot[::STIPPLE_STRIDE, ::STIPPLE_STRIDE]
                    lat_s = lat2d_plot[::STIPPLE_STRIDE, ::STIPPLE_STRIDE]
                else:
                    lon_s = lon_plot[::STIPPLE_STRIDE]
                    lat_s = lat_plot[::STIPPLE_STRIDE]
                    lon_s, lat_s = np.meshgrid(lon_s, lat_s)
            else:
                if CARTOPY_AVAILABLE:
                    lon_s = lon2d_plot
                    lat_s = lat2d_plot
                else:
                    lon_s, lat_s = np.meshgrid(lon_plot, lat_plot)

            if np.any(sig):
                if CARTOPY_AVAILABLE:
                    ax.scatter(
                        lon_s[sig],
                        lat_s[sig],
                        s=6,
                        c="#111111",
                        alpha=0.35,
                        linewidths=0,
                        transform=proj,
                        zorder=3,
                    )
                else:
                    ax.scatter(
                        lon_s[sig],
                        lat_s[sig],
                        s=6,
                        c="#111111",
                        alpha=0.35,
                        linewidths=0,
                        zorder=3,
                    )

            ax.set_title(f"{var} anomaly trend - {label}", color=TITLE_COLOR)
            ax.grid(False)

        fig.colorbar(
            im,
            ax=axes[r, :],
            orientation="horizontal",
            pad=0.04,
            fraction=0.05,
            label=f"{var} trend per decade (anomalies)",
        )

    fig.suptitle(
        title,
        x=0.01,
        ha="left",
        fontsize=15,
        color=TITLE_COLOR,
    )
    fig.text(
        0.01,
        0.95,
        f"Annual totals with dynamic {CLIM_WINDOW_YEARS}-year climatology (prior years) removed. "
        f"MIN_YEARS={MIN_YEARS}. Smoothing: {smooth_desc}. "
        f"Stippling = p < {SIGNIFICANCE_LEVEL}.",
        fontsize=9,
        color="#555555",
    )

    plt.show()


strength_vars = ["ACE", "wind"]
intensity_vars = ["RI", "24hrChange"]

plot_group(strength_vars, "Spatial trend of strength anomalies (dynamic 30-year climatology)")
plot_group(intensity_vars, "Spatial trend of intensification anomalies (dynamic 30-year climatology)")
