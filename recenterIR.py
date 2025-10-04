#Import libraries:
import numpy as np
from scipy import ndimage
import warnings
warnings.filterwarnings("ignore")

# Try to import numba if available, otherwise use non-numba versions
try:
    import numba as nb
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    print("Numba not found. Using non-compiled versions of functions.")

### Define optimized utility functions ###

# Define numba versions if available, otherwise fall back to non-compiled versions
if HAS_NUMBA:
    @nb.njit
    def distance_vectorized(center_lat, center_lng, lats, lons):
        """
        Vectorized and JIT-compiled function to compute distances from a center point to all grid points.
        
        Args:
            center_lat: Center latitude in degrees
            center_lng: Center longitude in degrees
            lats: 2D array of latitudes in degrees
            lons: 2D array of longitudes in degrees
        
        Returns:
            2D array of distances in km
        """
        # approximate radius of earth in km
        R = 6373.0
        
        # Pre-allocate output array
        result = np.zeros(lats.shape, dtype=np.float64)
        
        for i in range(lats.shape[0]):
            for j in range(lats.shape[1]):
                # Convert to radians
                s_lat = center_lat * np.pi/180.0
                s_lng = center_lng * np.pi/180.0
                e_lat = lats[i, j] * np.pi/180.0
                e_lng = lons[i, j] * np.pi/180.0
                
                d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
                result[i, j] = 2 * R * np.arcsin(np.sqrt(d))
                
        return result

    @nb.njit
    def bearing_vectorized(center_lat, center_lng, lats, lons):
        """
        Vectorized and JIT-compiled function to compute bearings from a center point to all grid points.
        
        Args:
            center_lat: Center latitude in degrees
            center_lng: Center longitude in degrees
            lats: 2D array of latitudes in degrees
            lons: 2D array of longitudes in degrees
        
        Returns:
            2D array of bearings in radians
        """
        # Pre-allocate output array
        result = np.zeros(lats.shape, dtype=np.float64)
        
        for i in range(lats.shape[0]):
            for j in range(lats.shape[1]):
                # Convert to radians
                s_lat = center_lat * np.pi/180.0
                s_lng = center_lng * np.pi/180.0
                e_lat = lats[i, j] * np.pi/180.0
                e_lng = lons[i, j] * np.pi/180.0
                
                # meridional distance:
                md_raw = np.sin((e_lat - s_lat)/2)**2
                md_sign = np.sign(e_lat - s_lat) # Acquire integer sign of distance (i.e., -1, 0, or 1)
                
                # zonal distance:
                zd_raw = np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
                zd_sign = np.sign(e_lng - s_lng) # Acquire integer sign of distance
                
                # Calculate bearing
                bearing = np.arctan2(md_sign * np.sqrt(md_raw), zd_sign * np.sqrt(zd_raw))
                result[i, j] = bearing
                
        return result

    @nb.njit
    def correct_angle_differences_numba(angle_diff):
        """
        Corrects angle differences to fall within -π to π
        Uses explicit looping for Numba compatibility
        """
        result = np.copy(angle_diff)
        
        for i in range(result.shape[0]):
            for j in range(result.shape[1]):
                if np.isfinite(result[i, j]):
                    # Correct angles less than -π
                    if result[i, j] < -np.pi:
                        result[i, j] = 2.0 * np.pi + result[i, j]
                    # Correct angles greater than π
                    elif result[i, j] > np.pi:
                        result[i, j] = result[i, j] - 2.0 * np.pi
                        
        return result
else:
    # Non-numba versions
    def distance_vectorized(center_lat, center_lng, lats, lons):
        """Non-JIT version of distance calculation"""
        # approximate radius of earth in km
        R = 6373.0
        
        # Convert to radians
        s_lat = center_lat * np.pi/180.0
        s_lng = center_lng * np.pi/180.0
        e_lat = lats * np.pi/180.0
        e_lng = lons * np.pi/180.0
        
        d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
        
        return 2 * R * np.arcsin(np.sqrt(d))

    def bearing_vectorized(center_lat, center_lng, lats, lons):
        """Non-JIT version of bearing calculation"""
        # Convert to radians
        s_lat = center_lat * np.pi/180.0
        s_lng = center_lng * np.pi/180.0
        e_lat = lats * np.pi/180.0
        e_lng = lons * np.pi/180.0
        
        # meridional distance calculation
        md_raw = np.sin((e_lat - s_lat)/2)**2
        md_sign = np.sign(e_lat - s_lat)
        
        # zonal distance calculation
        zd_raw = np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
        zd_sign = np.sign(e_lng - s_lng)
        
        # Calculate bearing
        bearing = np.arctan2(md_sign * np.sqrt(md_raw), zd_sign * np.sqrt(zd_raw))
        
        return bearing

# Common functions that don't need numba
def correct_angle_differences(angle_diff):
    """
    Non-JIT version that corrects angle differences to fall within -π to π
    """
    corrected = angle_diff.copy()
    
    # Correct angles less than -π
    mask_low = corrected < -np.pi
    corrected[mask_low] = 2.0 * np.pi + corrected[mask_low]
    
    # Correct angles greater than π
    mask_high = corrected > np.pi
    corrected[mask_high] = corrected[mask_high] - 2.0 * np.pi
    
    return corrected

# Function to find value of array closest to specified value
def find_nearest(array, value):
    array = np.asarray(array)
    X = np.abs(array - value)
    idx = np.where(X == np.nanmin(X))
    return array[idx]

# Function to find index of array closest to specified value
def find_nearest_ind(array, value):
    array = np.asarray(array)
    X = np.abs(array - value)
    idx = np.where(X == np.nanmin(X))
    return idx

def recenter_ir(irb,xdist,ydist,num_iterations,lons,lats,spad=5):
    # irb is a 2D array of IR brightness temps
    # xdist is a 1D array of eastward distance
    # ydist is a 1D array of northward distance
    # lons is a two-dimensional array of the longitudinal coordinates
    # lats is a two-dimensional array of the latitudinal coordinates

    core_dist = 50. # distance (km) to perform core calculations
    if xdist.ndim == 2:
        # print('Dimensions = 2')
        X, Y = xdist, ydist
    else:
        X, Y = np.meshgrid(xdist,ydist)
    dist = np.sqrt(X**2 + Y**2)
    angle = np.arctan2(Y,X)

    radii = np.arange(0,core_dist+1,2)
    dr = radii[1] - radii[0]

    # pnyi = np.where(Y == 0)[0][0]
    # pnxi = np.where(X == 0)[1][0]
    r = np.hypot(X, Y)  # distance to (0,0) in km
    pnyi, pnxi = np.unravel_index(np.nanargmin(r), r.shape)

    # Initialize parameters for iteration
    yloc = np.nan  # Meridional index of TC center
    xloc = np.nan  # Zonal index of TC center
    mean_score = 0 # This is the initial mean standard deviation to try to beat
    final_ir_rad_dif = 0
    final_core_std = 0
    final_eye_score = 0
    final_ir_grad = 0

    domain_score = np.full((irb.shape[0],irb.shape[1]),np.nan)

    ### Begin TC center search ###
    
    for n in range(num_iterations):

        # print('current iteration is:',n)
        
        # If first iteration has been completed, copy center estimate from previous iteration:
        if n >= 1:
            if mean_score > 0:
                pnyi = np.copy(yloc)
                pnxi = np.copy(xloc)
            else:
                tc_center_lon = np.nan
                tc_center_lat = np.nan
                break
            
        # Establish range of grid points to search for TC center:
        range_y = np.arange(pnyi - spad,pnyi + spad+1,1)
        range_x = np.arange(pnxi - spad,pnxi + spad+1,1)
        
        # Loop over meridional grid points:
        for ybi in range_y:
            
            # Ensure the algorithm isn't searching outside the bounds of the domain:
            if ybi >= int(irb.shape[0]):
                continue
            if ybi < 0:
                continue

            # Loop over zonal grid points:
            for xbi in range_x:
                
                # Ensure the algorithm isn't searching outside the bounds of the domain:
                if xbi >= int(irb.shape[1]):
                    continue
                if xbi < 0:
                    continue
                
                # Ensure the mean error at this grid point hasn't been computed already:
                if n >= 1:
                    if domain_score[ybi,xbi] >= 0:
                        continue


                ### Perform error calculations ###
                
                # Compute the distance from each grid point relative to hypothetical TC center:
                
                # Get lat/lon of current center guess
                center_lat = lats[ybi, xbi]
                center_lon = lons[ybi, xbi]
                
                # Compute distances and angles using vectorized functions
                curr_dist = distance_vectorized(center_lat, center_lon, lats, lons)

                curr_std = np.full((np.size(radii)),np.nan)
                curr_mean = np.full((np.size(radii)),np.nan)

                # Loop over all radii in core:
                for radi in range(np.size(radii)):
                    min_rad = np.nanmax([0.,radii[radi]-(0.5*dr)])
                    max_rad = (0.5*dr) + radii[radi]
            
                    ryi = np.where(np.logical_and(curr_dist >= min_rad, curr_dist < max_rad))[0]
                    rxi = np.where(np.logical_and(curr_dist >= min_rad, curr_dist < max_rad))[1]

                    curr_std[radi]  = np.nanstd(irb[ryi,rxi])
                    curr_mean[radi] = np.nanmean(irb[ryi,rxi])

                radm = np.nanmax([4,np.where(curr_mean == np.nanmin(curr_mean))[0][0]])
                curr_grad = -1.*np.nanmean(np.gradient(curr_mean[0:radm+1],dr))      
                ir_rad_dif = np.nanmean(curr_mean[0:2]) - np.nanmin(curr_mean) # Note here is 4x4-km box eye average
                
                curr_mean_score = 100.*((1./np.nanmean(curr_std))**2)*curr_grad

                domain_score[ybi,xbi] = curr_mean_score

                if curr_mean_score > mean_score:
                    #print(ybi,xbi)
                    mean_score = np.copy(curr_mean_score)
                    del curr_mean_score

                    # Store TC location estimate
                    tc_center_lon = center_lon
                    tc_center_lat = center_lat

                    # Store indices of estimated TC center
                    yloc = ybi
                    xloc = xbi

                    final_ir_rad_dif = np.copy(ir_rad_dif)
                    final_core_std = np.copy(np.nanmean(curr_std))
                    final_eye_score = np.copy(domain_score[ybi,xbi])
                    final_ir_grad = np.copy(curr_grad)
        
        # Check for convergence
        if n >= 1 and yloc == pnyi and xloc == pnxi:
            if (final_ir_rad_dif >= 10) & (final_eye_score >= 1.0):
                # print(f"ir_rad_dif: {final_ir_rad_dif:.2f}")
                # print(f"ir_grad: {final_ir_grad:.2f}")
                # print(f"curr_std: {final_core_std:.2f}")
                # print(f"eye_score: {final_eye_score:.2f}")
                
                tc_center_lat = lats[int(yloc), int(xloc)]
                tc_center_lon = lons[int(yloc), int(xloc)]

            if (final_ir_rad_dif < 10) | (final_eye_score < 1.0):
                # print(f"ir_rad_dif: {final_ir_rad_dif:.2f}")
                # print(f"ir_grad: {final_ir_grad:.2f}")
                # print(f"curr_std: {final_core_std:.2f}")
                # print(f"eye_score: {final_eye_score:.2f}")
                
                tc_center_lat = np.nan
                tc_center_lon = np.nan
                yloc = np.nan
                xloc = np.nan

            # print('Done.')

            break

    return tc_center_lon, tc_center_lat, yloc, xloc, mean_score