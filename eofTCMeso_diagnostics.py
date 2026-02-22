import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


def _set_pub_style():
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )

def story_panel(dataset, cmap=None):
    """
    Narrative multi-panel diagnostic.

    Parameters
    ----------
    dataset : xarray.Dataset
        Must contain variable 'data' with dims (time, radius, theta).
    cmap : module or object, optional
        If provided, uses cmap.tempAnoms3() for anomaly panel.
    """
    data = dataset['data']

    # Azimuthal mean (time, radius)
    azm = data.mean('theta', skipna=True)

    # Radius of max azimuthal mean at each time (robust to all-NaN slices)
    azm_safe = azm.where(np.isfinite(azm), other=-np.inf)
    rmax_idx = azm_safe.argmax('radius')
    rmax = dataset.radius.isel(radius=rmax_idx)

    # Time-theta slice at the instantaneous rmax
    theta_slice = data.isel(radius=rmax_idx)

    # Symmetry proxy over time
    mean_theta = data.mean('theta')
    std_theta = data.std('theta')
    sym = 1 - (std_theta / mean_theta.clip(min=1e-6)).mean('radius')

    # Pick 3 key times: early, mid, late
    t0 = data.time.isel(time=0)
    t1 = data.time.isel(time=data.sizes['time'] // 2)
    t2 = data.time.isel(time=-1)

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.8])

    # Panel A: Time-Radius Hovmoller (azimuthal mean)
    ax0 = fig.add_subplot(gs[0, 0])
    im0 = ax0.contourf(azm.time, azm.radius, azm.T, levels=60, cmap='viridis')
    ax0.set_title('Azimuthal Mean (time-radius)')
    ax0.set_xlabel('Time')
    ax0.set_ylabel('Radius')
    fig.colorbar(im0, ax=ax0, orientation='vertical', pad=0.02)

    # Panel B: Time-Theta at rmax(t) (structure drift)
    ax1 = fig.add_subplot(gs[0, 1])
    im1 = ax1.contourf(theta_slice.time, theta_slice.theta, theta_slice.T, levels=60, cmap='viridis')
    ax1.set_title('Azimuthal Structure at rmax(t)')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Theta (rad)')
    fig.colorbar(im1, ax=ax1, orientation='vertical', pad=0.02)

    # Panel C: Polar snapshots early/late
    ax2 = fig.add_subplot(gs[1, 0], projection='polar')
    snap0 = data.sel(time=t0)
    cf2 = ax2.contourf(dataset.theta, dataset.radius, snap0, levels=50, cmap='viridis')
    ax2.set_title(f'Snapshot Early: {np.datetime_as_string(t0.values)}')
    fig.colorbar(cf2, ax=ax2, orientation='horizontal', pad=0.08)

    ax3 = fig.add_subplot(gs[1, 1], projection='polar')
    snap2 = data.sel(time=t2)
    cf3 = ax3.contourf(dataset.theta, dataset.radius, snap2, levels=50, cmap='viridis')
    ax3.set_title(f'Snapshot Late: {np.datetime_as_string(t2.values)}')
    fig.colorbar(cf3, ax=ax3, orientation='horizontal', pad=0.08)

    # Panel D: Storyline metrics
    ax4 = fig.add_subplot(gs[2, :])
    ax4.plot(azm.time, rmax, label='rmax(t)', color='tab:blue')
    ax4.set_ylabel('Radius of Max Mean')
    ax4b = ax4.twinx()
    ax4b.plot(sym.time, sym, label='Symmetry Index', color='tab:orange')
    ax4b.set_ylabel('Symmetry Index')

    # Mark key times
    for t in [t0, t1, t2]:
        ax4.axvline(t.values, color='k', alpha=0.2, lw=1)

    ax4.set_title('Evolution: Structure & Symmetry')
    ax4.set_xlabel('Time')

    # Combined legend
    lines = ax4.get_lines() + ax4b.get_lines()
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left')

    plt.tight_layout()
    return fig


def story_panel_from_globals(globals_dict=None, cmap=None):
    """
    Convenience wrapper for notebooks that already define `dataset`.
    Call with `story_panel_from_globals(globals())`.
    """
    g = globals_dict or globals()
    if "dataset" not in g:
        raise KeyError("Expected `dataset` in globals. Pass globals() from the notebook.")
    return story_panel(g["dataset"], cmap=cmap)

def publication_panel_bt(dataset, inner_radius=60, max_mode=8):
    """
    Creative, publication-quality diagnostic focused on inner-core symmetry breaking.

    Panels:
    A) Inner-core polar anomaly snapshot at peak eyewall time.
    B) Azimuthal energy spectrum (m=1..max_mode) at peak time.
    C) Mode-1 phase drift (time-radius) to reveal rotation/phase locking.
    D) Mode-1/2 power + inner-core asymmetry time series.
    """
    _set_pub_style()

    data = dataset["data"]
    time = data.time
    radius = data.radius
    theta = data.theta

    # Azimuthal mean and std (skip NaNs)
    azm = data.mean("theta", skipna=True)
    std = data.std("theta", skipna=True)

    # Focus on inner core
    inner = azm.sel(radius=slice(0, inner_radius))
    inner_std = std.sel(radius=slice(0, inner_radius))

    # Peak eyewall time = time of coldest inner-core mean Tb
    t_peak = inner.mean("radius", skipna=True).argmin("time")
    t_peak_val = time.isel(time=t_peak)

    # Inner-core asymmetry index: std / |mean|
    asym = (inner_std / np.clip(np.abs(inner), 1e-6, None)).mean("radius")

    # Azimuthal mode power via FFT along theta
    # Assumes theta is evenly spaced
    inner_data = data.sel(radius=slice(0, inner_radius))
    vals = inner_data.transpose("time", "radius", "theta").values
    vals = np.where(np.isfinite(vals), vals, np.nanmean(vals))
    fft = np.fft.rfft(vals, axis=-1)
    power = (np.abs(fft) ** 2).mean(axis=1)  # average over radius
    modes = np.arange(power.shape[-1])
    power = power[:, 1 : max_mode + 1]  # skip mode 0
    modes = modes[1 : max_mode + 1]

    # Mode-1 complex amplitude (time, radius)
    a1 = fft[:, :, 1]
    phase1 = np.angle(a1)
    phase1 = np.unwrap(phase1, axis=0)
    phase1 = np.unwrap(phase1, axis=1)

    # Mode-2 power (time)
    mode1_power = power[:, 0]
    mode2_power = power[:, 1] if power.shape[1] > 1 else power[:, 0] * 0.0

    fig = plt.figure(figsize=(12, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])

    # Panel A: Polar anomaly snapshot at peak eyewall time (inner core only)
    ax0 = fig.add_subplot(gs[0, 0], projection="polar")
    snap = data.sel(time=t_peak_val).sel(radius=slice(0, inner_radius))
    snap_anom = snap - snap.mean("theta", skipna=True)
    levels = np.linspace(np.nanpercentile(snap_anom, 2), np.nanpercentile(snap_anom, 98), 50)
    cf0 = ax0.contourf(theta, snap.radius, snap_anom, levels=levels, cmap="coolwarm")
    ax0.set_title(f"Inner-Core Tb Anomaly: {np.datetime_as_string(t_peak_val.values)}")
    fig.colorbar(cf0, ax=ax0, orientation="horizontal", pad=0.08, label="Tb Anomaly")

    # Panel B: Azimuthal energy spectrum at peak time
    ax1 = fig.add_subplot(gs[0, 1])
    snap_fft = np.fft.rfft(snap.values, axis=-1)
    snap_power = (np.abs(snap_fft) ** 2).mean(axis=0)
    m = np.arange(snap_power.shape[-1])[1 : max_mode + 1]
    ax1.plot(m, snap_power[1 : max_mode + 1], marker="o", color="black")
    ax1.set_title("Azimuthal Energy Spectrum (inner core)")
    ax1.set_xlabel("Azimuthal Mode (m)")
    ax1.set_ylabel("Power")
    ax1.grid(True, alpha=0.3)

    # Panel C: Mode-1 phase drift (time-radius)
    ax2 = fig.add_subplot(gs[1, 0])
    im2 = ax2.contourf(time, inner.radius, phase1.T, levels=60, cmap="twilight")
    ax2.set_title("Mode-1 Phase Drift (inner core)")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Radius")
    fig.colorbar(im2, ax=ax2, orientation="vertical", pad=0.02, label="Phase (rad)")

    # Panel D: Inner-core asymmetry + mode-1/2 power
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(time, asym, color="tab:orange", label="Inner-core asymmetry")
    ax3.set_ylabel("Asymmetry (std/|mean|)")
    ax3b = ax3.twinx()
    ax3b.plot(time, mode1_power, color="tab:green", label="Mode-1 power")
    ax3b.plot(time, mode2_power, color="tab:blue", label="Mode-2 power")
    ax3b.set_ylabel("Mode Power")
    ax3.set_title("Asymmetry & Low-Mode Power")
    ax3.set_xlabel("Time")

    lines = ax3.get_lines() + ax3b.get_lines()
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper left", frameon=False)

    plt.tight_layout()
    return fig


def eye_bt_time_analysis(dataset, inner_radius=60, ring_width=10):
    """
    Define the eye at each time and analyze brightness temperatures inside it.

    Eye definition:
    - Compute azimuthal-mean Tb within inner_radius.
    - Eye boundary = largest radius where azimuthal-mean Tb >= midpoint
      between warm-eye maximum and cold-eyewall minimum at that time.
    """
    _set_pub_style()

    data = dataset["data"]
    time = data.time
    radius = data.radius

    # Inner-core azimuthal mean
    azm = data.mean("theta", skipna=True)
    inner = azm.sel(radius=slice(0, inner_radius))
    inner_vals = inner.values
    rad_vals = inner.radius.values

    nt = inner_vals.shape[0]
    r_eye = np.full(nt, np.nan)

    warm = np.nanmax(inner_vals, axis=1)
    cold = np.nanmin(inner_vals, axis=1)
    thresh = (warm + cold) / 2.0

    for i in range(nt):
        if not np.isfinite(thresh[i]):
            continue
        mask = inner_vals[i, :] >= thresh[i]
        if np.any(mask):
            r_eye[i] = rad_vals[np.where(mask)[0].max()]

    # Compute stats inside the eye and just outside (eyewall ring) for each time
    data_vals = data.values
    eye_mean = np.full(nt, np.nan)
    eye_std = np.full(nt, np.nan)
    ring_mean = np.full(nt, np.nan)
    ring_std = np.full(nt, np.nan)
    boundary_grad = np.full(nt, np.nan)

    for i in range(nt):
        if not np.isfinite(r_eye[i]):
            continue
        rmask = radius.values <= r_eye[i]
        eye_vals = data_vals[i, rmask, :].ravel()
        eye_vals = eye_vals[np.isfinite(eye_vals)]
        if eye_vals.size == 0:
            continue
        eye_mean[i] = np.nanmean(eye_vals)
        eye_std[i] = np.nanstd(eye_vals)

        # Eyewall ring just outside the eye
        r_out = r_eye[i] + ring_width
        rmask_ring = (radius.values > r_eye[i]) & (radius.values <= r_out)
        ring_vals = data_vals[i, rmask_ring, :].ravel()
        ring_vals = ring_vals[np.isfinite(ring_vals)]
        if ring_vals.size > 0:
            ring_mean[i] = np.nanmean(ring_vals)
            ring_std[i] = np.nanstd(ring_vals)

        # Eye boundary sharpness (radial gradient magnitude at boundary)
        # Approximate with centered finite difference on azimuthal mean
        if np.isfinite(r_eye[i]):
            ridx = np.argmin(np.abs(radius.values - r_eye[i]))
            if 0 < ridx < inner_vals.shape[1] - 1:
                boundary_grad[i] = 0.5 * (
                    inner_vals[i, ridx + 1] - inner_vals[i, ridx - 1]
                ) / (rad_vals[ridx + 1] - rad_vals[ridx - 1])

    fig = plt.figure(figsize=(12, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])

    # Panel A: Inner-core Hovmoller with eye boundary
    ax0 = fig.add_subplot(gs[0, 0])
    im0 = ax0.contourf(time, inner.radius, inner.T, levels=60, cmap="magma_r")
    ax0.plot(time, r_eye, color="cyan", lw=1.5, label="Eye boundary")
    ax0.set_title("Inner-Core Azimuthal Mean Tb + Eye Boundary")
    ax0.set_xlabel("Time")
    ax0.set_ylabel("Radius")
    fig.colorbar(im0, ax=ax0, orientation="vertical", pad=0.02, label="Brightness Temperature")
    ax0.legend(frameon=False, loc="upper right")

    # Panel B: Eye boundary sharpness (gradient)
    ax1 = fig.add_subplot(gs[0, 1])
    ax1.plot(time, boundary_grad, color="black", label="Boundary gradient")
    ax1.set_title("Eye Boundary Sharpness")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("dTb/dr at Boundary")
    ax1.legend(frameon=False, loc="upper right")

    # Panel C: Eye vs Eyewall Tb (contrast)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(time, eye_mean, color="tab:red", label="Eye mean Tb")
    ax2.plot(time, ring_mean, color="tab:blue", label=f"Eyewall ring mean (r+{ring_width})")
    ax2.set_title("Eye vs Eyewall Tb")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Brightness Temperature")
    ax2.legend(frameon=False, loc="upper right")

    # Panel D: Eye stability (variability inside vs outside)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(time, eye_std, color="tab:orange", label="Eye Tb std")
    ax3.plot(time, ring_std, color="tab:green", label=f"Eyewall ring std (r+{ring_width})")
    ax3.set_ylabel("Tb Std")
    ax3b = ax3.twinx()
    ax3b.plot(time, r_eye, color="tab:blue", label="Eye radius")
    ax3b.set_ylabel("Eye Radius")
    ax3.set_title("Eye Stability (Inside vs Outside)")
    ax3.set_xlabel("Time")
    lines = ax3.get_lines() + ax3b.get_lines()
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper left", frameon=False)

    plt.tight_layout()
    return fig


def eye_cdo_time_analysis(dataset, inner_radius=200, edge_frac=0.5):
    """
    For each time: compute eye radius and CDO radius, mean Tb of both,
    plus CDO symmetry (azimuthal std/|mean| within the CDO ring).

    CDO radius definition (outer edge of cold ring):
    - Use azimuthal-mean Tb profile within inner_radius.
    - Find coldest radius outside the eye.
    - Define a cold-cloud threshold: T_cold + edge_frac*(T_warm - T_cold),
      where T_warm is the 75th percentile outside the eye.
    - CDO radius = outermost radius in the contiguous cold region
      around the coldest radius that stays below the threshold.
    """
    _set_pub_style()

    data = dataset["data"]
    time = data.time
    radius = data.radius

    # Azimuthal mean within inner core
    azm = data.mean("theta", skipna=True)
    inner = azm.sel(radius=slice(0, inner_radius))
    inner_vals = inner.values
    rad_vals = inner.radius.values
    nt = inner_vals.shape[0]

    r_eye = np.full(nt, np.nan)
    r_cdo = np.full(nt, np.nan)
    r_cdo_inner = np.full(nt, np.nan)
    eye_mean = np.full(nt, np.nan)
    cdo_mean = np.full(nt, np.nan)
    cdo_sym = np.full(nt, np.nan)
    eye_grad = np.full(nt, np.nan)
    cdo_grad = np.full(nt, np.nan)
    eye_uniform = np.full(nt, np.nan)
    cdo_cov = np.full(nt, np.nan)

    # Eye boundary: largest radius where azm Tb >= midpoint between warm max and cold min
    warm = np.nanmax(inner_vals, axis=1)
    cold = np.nanmin(inner_vals, axis=1)
    thresh = (warm + cold) / 2.0

    data_vals = data.values
    for i in range(nt):
        if not np.isfinite(thresh[i]):
            continue

        # Eye radius
        mask_eye = inner_vals[i, :] >= thresh[i]
        if np.any(mask_eye):
            r_eye[i] = rad_vals[np.where(mask_eye)[0].max()]

        # CDO radius: outer edge of contiguous cold ring outside the eye
        if np.isfinite(r_eye[i]):
            mask_outer = (rad_vals > r_eye[i]) & (rad_vals <= inner_radius)
        else:
            mask_outer = rad_vals <= inner_radius

        if np.any(mask_outer):
            outer_vals = inner_vals[i, mask_outer]
            if np.isfinite(outer_vals).any():
                cold_min = np.nanmin(outer_vals)
                warm_ref = np.nanpercentile(outer_vals, 75)
                threshold = cold_min + edge_frac * (warm_ref - cold_min)
                cdo_threshold = threshold

                # Index of coldest radius in full array
                outer_idx = np.where(mask_outer)[0]
                idx_cold = outer_idx[np.nanargmin(outer_vals)]

                # Contiguous cold region around the minimum
                cold_mask = (inner_vals[i, :] <= threshold) & mask_outer
                left = idx_cold
                right = idx_cold
                while left - 1 >= 0 and cold_mask[left - 1]:
                    left -= 1
                while right + 1 < len(rad_vals) and cold_mask[right + 1]:
                    right += 1

                r_cdo_inner[i] = rad_vals[left]
                r_cdo[i] = rad_vals[right]

        # Eye mean Tb (inside eye)
        if np.isfinite(r_eye[i]):
            rmask_eye = radius.values <= r_eye[i]
            eye_vals = data_vals[i, rmask_eye, :].ravel()
            eye_vals = eye_vals[np.isfinite(eye_vals)]
            if eye_vals.size > 0:
                eye_mean[i] = np.nanmean(eye_vals)
                eye_std_i = np.nanstd(eye_vals)
                eye_uniform[i] = 1.0 / (1.0 + eye_std_i / np.clip(np.abs(eye_mean[i]), 1e-6, None))

        # Eye boundary sharpness (radial gradient of azimuthal mean)
        if np.isfinite(r_eye[i]):
            ridx = np.argmin(np.abs(rad_vals - r_eye[i]))
            if 0 < ridx < len(rad_vals) - 1:
                eye_grad[i] = 0.5 * (
                    inner_vals[i, ridx + 1] - inner_vals[i, ridx - 1]
                ) / (rad_vals[ridx + 1] - rad_vals[ridx - 1])

        # CDO mean Tb and symmetry (within contiguous cold ring)
        if np.isfinite(r_cdo[i]) and np.isfinite(r_cdo_inner[i]):
            rmask_ring = (radius.values >= r_cdo_inner[i]) & (radius.values <= r_cdo[i])
            ring = data_vals[i, rmask_ring, :]
            ring = ring[:, np.isfinite(ring).any(axis=0)]
            if ring.size > 0:
                cdo_mean[i] = np.nanmean(ring)
                mean_theta = np.nanmean(ring, axis=1)
                std_theta = np.nanstd(ring, axis=1)
                ratio = std_theta / np.clip(np.abs(mean_theta), 1e-6, None)
                cdo_sym[i] = 1.0 / (1.0 + np.nanmean(ratio))

                # CDO cold-cloud coverage fraction
                ring_theta_mean = np.nanmean(ring, axis=0)
                if np.isfinite(cdo_threshold):
                    cdo_cov[i] = np.mean(ring_theta_mean <= cdo_threshold)

        # CDO edge sharpness
        if np.isfinite(r_cdo[i]):
            ridx = np.argmin(np.abs(rad_vals - r_cdo[i]))
            if 0 < ridx < len(rad_vals) - 1:
                cdo_grad[i] = 0.5 * (
                    inner_vals[i, ridx + 1] - inner_vals[i, ridx - 1]
                ) / (rad_vals[ridx + 1] - rad_vals[ridx - 1])

    # Derived metrics
    contrast = eye_mean - cdo_mean
    separation = r_cdo - r_eye

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])

    # Panel A: Inner-core Hovmoller with eye and CDO radii
    ax0 = fig.add_subplot(gs[0, 0])
    im0 = ax0.contourf(time, inner.radius, inner.T, levels=60, cmap="magma_r")
    ax0.plot(time, r_eye, color="cyan", lw=1.5, label="Eye radius")
    ax0.plot(time, r_cdo, color="lime", lw=1.5, label="CDO edge")
    ax0.set_title("Azimuthal-Mean Tb + Eye/CDO Radii")
    ax0.set_xlabel("Time")
    ax0.set_ylabel("Radius")
    fig.colorbar(im0, ax=ax0, orientation="vertical", pad=0.02, label="Brightness Temperature")
    ax0.legend(frameon=False, loc="upper right")

    # Panel B: Edge sharpness (eye vs CDO)
    ax1 = fig.add_subplot(gs[0, 1])
    ax1.plot(time, eye_grad, color="tab:orange", label="Eye boundary dTb/dr")
    ax1.plot(time, cdo_grad, color="tab:green", label="CDO edge dTb/dr")
    ax1.set_title("Edge Sharpness (Radial Gradient)")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("dTb/dr")
    ax1.legend(frameon=False, loc="upper right")

    # Panel C: Eye–CDO contrast + separation
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.plot(time, contrast, color="tab:purple", label="Eye - CDO Tb")
    ax2.set_title("Eye–CDO Contrast & Separation")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Tb Contrast")
    ax2b = ax2.twinx()
    ax2b.plot(time, separation, color="tab:blue", label="CDO - Eye radius")
    ax2b.set_ylabel("Radius Separation")
    lines = ax2.get_lines() + ax2b.get_lines()
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc="upper right", frameon=False)

    # Panel D: CDO symmetry + ring thickness
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(time, cdo_sym, color="black", label="CDO symmetry (higher = more symmetric)")
    ax3.set_title("CDO Symmetry & Thickness")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Symmetry")
    thickness = r_cdo - r_cdo_inner
    ax3b = ax3.twinx()
    ax3b.plot(time, thickness, color="tab:red", label="CDO ring thickness")
    ax3b.set_ylabel("Thickness")
    lines = ax3.get_lines() + ax3b.get_lines()
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper right", frameon=False)

    # Panel E: Eye thermal state (mean + uniformity)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(time, eye_mean, color="tab:red", label="Eye mean Tb")
    ax4.set_title("Eye Thermal State")
    ax4.set_xlabel("Time")
    ax4.set_ylabel("Brightness Temperature")
    ax4b = ax4.twinx()
    ax4b.plot(time, eye_uniform, color="tab:orange", label="Eye uniformity")
    ax4b.set_ylabel("Uniformity (higher = smoother)")
    lines = ax4.get_lines() + ax4b.get_lines()
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc="upper right", frameon=False)

    # Panel F: CDO closure fraction
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.plot(time, cdo_cov, color="tab:green", label="CDO cold-cloud coverage")
    ax5.set_title("CDO Closure Fraction")
    ax5.set_xlabel("Time")
    ax5.set_ylabel("Coverage (0–1)")
    ax5.set_ylim(0, 1)
    ax5.legend(frameon=False, loc="upper right")

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    fulldataset = xr.open_dataset(r"C:\Users\deela\Downloads\mel1028netcdfv2.nc")
    dataset = fulldataset.sel(time=slice(np.datetime64("2025-10-28T18")), radius=slice(0, 200))
    print(dataset)

    eye_cdo_time_analysis(dataset)
    plt.show()
