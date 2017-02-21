"""
Script focussed around analysing annual dark/bare ice presence, duration and
onset.

Load all the variables which are useful for various analyses for this paper
into the IPython environment. 
	> For running in batch on the command line does just importing it work?

Analysis includes comparison with climatological information derived from 
MAR 7.5 km data.


Mask variable naming schema:

	Prefixed with mar_ : mask is at MAR resolution (7.5km)
	If mask contains multiple TIME points, variable name should reflect this
	If mask only 2-D (no TIME component), drop time refs from variable name.

""" 

import numpy as np
from osgeo import gdal
from scipy import ndimage
import datetime as dt
import statsmodels.api as sm
import calendar
#import seaborn as sns
import cartopy.crs as ccrs
from matplotlib import rcParams
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

import mar_raster

#rcParams['font.sans-serif'] = 'Segoe UI'
rcParams['font.size'] = 6
plt.style.use('seaborn-paper')
rcParams['lines.linewidth'] = 1

# ---------------------------------------------------------------------------- 
## Load in data and set global parameters 
ds_refl = xr.open_mfdataset('/scratch/MOD09GA.006.SW/*b1234q.nc',
		chunks={'TIME':366})

onset = xr.open_dataset('/scratch/physical_controls/MOD09GA.006.2000-2016.dark45.postsnow.MayAug.nc')

mar_path = '/scratch/MARv3.6.2-7.5km-v2-ERA/ICE.20*nc'
x_slice = slice(-586678,-254545)
y_slice = slice(-949047,69833)

min_dark_days = 10


# ----------------------------------------------------------------------------
## Improve ICE MARGINS mask prior to generating any statistics

# Erode the mask in order to remove dark pixels along the ice sheet margins
# binary_erosion does not work with nans, so convert them to zeros
mtmp = np.where(np.isnan(onset.mask.values), 0, 1)
# Do the erosion
mask_erode = ndimage.binary_erosion(mtmp, iterations=10)
# Convert zeros back to nans
mask_erode = np.where(mask_erode == 0, np.nan, 1)
# Calculate the difference
mask_erode_diff = np.where(np.isnan(onset.mask),0,1) + np.where(np.isnan(mask_erode),0,1)



## ---------------------------------------------------------------------------
## Dark ice masks

# First create the 600 m masks, 1 per year
masks_annual_dark = onset.dark_dur \
			.where((onset.dark_dur > min_dark_days) & (mask_erode == 1)) \
			.notnull()

# Need to load in a MAR XY layer to get coordinates, the MAR ice mask will do
## Obtain mask from first nc file time point (via isel)
mar_MSK = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.MSK.sel(X=x_slice, 
		Y=y_slice)).isel(TIME=0).squeeze()

# Finally generate MAR-resolution masks
# Dict of info to pass in
mar_kws = {'nx': 45, 'ny': 136, 
	'xmin': -585000, 'ymax': 67500,
	'xres': 7500, 'yres': -7500 }
mar_masks_annual_dark = mar_raster.create_annual_mar_res(masks_annual_dark, mar_MSK, mar_kws, gdal.GDT_Byte)


# Alternatively, create a single spatial mask for the complete time series
# Base it on the years of high melt, pixel needs to be classed as dark for 
# 4 years in 7.
mask_dark  = masks_annual_dark.sum(dim='TIME')
mask_dark = mask_dark.where(mask_dark >= 4).notnull()
mar_mask_dark = mar_raster.create_mar_res(mask_dark, mar_kws, gdal.GDT_Byte)
mask_dark_nan = np.where(mask_dark == 0, np.nan, 1)



## ---------------------------------------------------------------------------
## Define periods

# Need to set zeros to nans otherwise they interfere with median calculation
masks_annual_dark_nan = np.where(masks_annual_dark == 0, np.nan, masks_annual_dark)
bare_doy_med_masked = (onset.bare * masks_annual_dark_nan).median(dim=['X','Y'])
dark_doy_med_masked = (onset.dark * masks_annual_dark_nan).median(dim=['X','Y'])

# Convert the DOYs to timedeltas, then calculate start and end dates for 
# various periods
deltas_bare = [np.timedelta64(int(v), 'D') for v in bare_doy_med_masked.values.tolist()]
dates_bare = mar_masks_annual_dark.TIME.values + deltas_bare
deltas_dark = [np.timedelta64(int(v), 'D') for v in dark_doy_med_masked.values.tolist()]
dates_dark = mar_masks_annual_dark.TIME.values + deltas_dark
dates_pre_bare = dates_bare - np.timedelta64(14, 'D')
dates_post_bare = dates_bare + np.timedelta64(14, 'D')

# Convert onset dates to string representations so that we can use 
# xarray .loc syntax
dates_pre_bare_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in dates_pre_bare]
dates_bare_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in dates_bare]
dates_post_bare_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in dates_post_bare]
dates_dark_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in dates_dark]
dates_st_summer_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in pd.date_range('2000-05-01', periods=17, freq=pd.DateOffset(years=1))]
dates_en_summer_str = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in pd.date_range('2000-08-30', periods=17, freq=pd.DateOffset(years=1))]


# Periods creation function
def create_periods(mar_data, dates_start_str, dates_end_str):
	# Create time-mask of periods
	doys = mar_data.groupby(mar_data['TIME.dayofyear']).apply(lambda x: x).dayofyear
	# Convert all values to False
	doys = doys.isnull()
	for ds,de in zip(dates_start_str, dates_end_str):
		str_ds = pd.to_datetime(ds).strftime('%Y-%m-%d')
		str_de = pd.to_datetime(de).strftime('%Y-%m-%d')
		doys.loc[str_ds:str_de] = True

	return doys


# Generic loader function for importing masked time series data
def get_periods(var_name, periods_mask, mean=False):
	var_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds[var_name].sel(X=x_slice, 
		Y=y_slice))

	var_period = var_all \
		.where((periods_mask)) \
		.where((mar_mask_dark.r > 0)) \
		.mean(dim=('X', 'Y'))

	if mean:
		var_period = var_period.resample('1AS', dim='TIME', how='mean')

	return var_period


# Define periods...
# Need to load in a 'dummy' time series to do this

periods_ts = mar_raster.open_mfxr(mar_path,	dim='TIME', 
	transform_func=lambda ds: ds.MM)

periods_bare2dark = create_periods(periods_ts, dates_bare_str, dates_dark_str)
periods_bare2pb = create_periods(periods_ts, dates_bare_str, dates_post_bare_str)
periods_bare2end = create_periods(periods_ts, dates_bare_str, dates_en_summer_str)
periods_dark2end = create_periods(periods_ts, dates_dark_str, dates_en_summer_str)
periods_summer = create_periods(periods_ts, dates_st_summer_str, dates_en_summer_str)

# MODIS data have different duration and are only April-September so need to 
# compute period time-masks separately
ds_refl_yr = xr.open_mfdataset('/scratch/MOD09GA.006.SW/*b1234q.nc',
		chunks={'TIME':5})
modis_periods_ts = ds_refl_yr.sur_refl_b01_1.TIME
modis_periods_bare2pb = create_periods(modis_periods_ts, dates_bare_str, dates_post_bare_str)
modis_periods_bare2end = create_periods(modis_periods_ts, dates_bare_str, dates_en_summer_str)


# ============================================================================
# Pre-processing code ends here
# ============================================================================
