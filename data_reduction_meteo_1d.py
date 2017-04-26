"""

Export 1-D time series to csv (i.e. no spatial data)

Basically, anything that can be represented as a Pandas DataFrame or Series

"""

from prep_env_vars import *

mar_path_anomalies = '/scratch/MARv3.6.2-7.5km-v2-ERA/ICE.*nc'

# # FROM STATISTICS.PY --------------------------------------------------------

# # Melt anomaly
ME_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.ME.sel(X=x_slice, 
		Y=y_slice))

ME_JJA_clim = ME_all_long.sel(TIME=slice('1981', '2000')) \
	.isel(SECTOR1_1=0) \
	.where(mar_mask_dark.r > 0) \
	.where(ME_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME')).to_pandas()

ME_JJA = ME_all_long.sel(TIME=slice('2000', '2016')) \
	.isel(SECTOR1_1=0) \
	.where(mar_mask_dark.r > 0) \
	.where(ME_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
ME_JJA.to_csv(store_path + 'ME_JJA_meandailyrate.csv')

ME_bare = ME_all_long.sel(TIME=slice('2000', '2016')) \
	.isel(SECTOR1_1=0) \
	.where(mar_mask_dark.r > 0) \
	.where(periods_bare2end) \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
ME_bare.to_csv(store_path + 'ME_bare_meandailyrate.csv')

ME_JJA_anom = ME_JJA - ME_JJA_clim
ME_JJA_anom.to_csv(store_path + 'ME_JJA_meandailyrateanomaly.csv')


# TTMIN

ttmin_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.TTMIN.sel(X=x_slice, 
		Y=y_slice))

ttmin_JJA = ttmin_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(ttmin_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y'))

ttmin_JJA_count = ttmin_JJA.where(ttmin_JJA > 0) \
	.groupby('TIME.year').count(dim='TIME')

ttmin_JJA_count_pd = ttmin_JJA_count.to_pandas().squeeze()
ttmin_JJA_count_pd.index = pd.date_range('2000-01-01', '2016-01-01', freq='1AS')
ttmin_JJA_count_pd.to_csv(store_path + 'TTMIN_JJA_count.csv')


## TT

TT_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.TT.sel(X=x_slice, 
		Y=y_slice))

TT_JJA = TT_all.sel(TIME=slice('2000', '2016')) \
	.isel(ATMLAY=2) \
	.where(mar_mask_dark.r > 0) \
	.where(TT_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
TT_JJA.to_csv(store_path + 'TT_JJA_mean.csv')



# # Radiative fluxes -----------------------------------------------------------
SW_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SWD.sel(X=x_slice, 
		Y=y_slice))

LW_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.LWD.sel(X=x_slice, 
		Y=y_slice))

# Absolute fluxes for Andy
SW_abs = SW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')) \
	.to_pandas().resample('24H').first()
SW_abs.to_csv(store_path + 'SW_abs.csv')	

LW_abs = LW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')) \
	.to_pandas().resample('24H').first()
LW_abs.to_csv(store_path + 'LW_abs.csv')	

SWD_JJA_clim = SW_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME')).to_pandas()

LWD_JJA_clim = LW_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME')).to_pandas()

SWD_JJA = SW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
SWD_JJA.to_csv(store_path + 'SWD_JJA_absolute_mean.csv')

LWD_JJA = LW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(LW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
LWD_JJA.to_csv(store_path + 'LWD_JJA_absolute_mean.csv')

SWD_JJA_anom = (SWD_JJA - SWD_JJA_clim)
SWD_JJA_anom.to_csv(store_path + 'SWD_JJA_anomalies.csv')
LWD_JJA_anom = (LWD_JJA - LWD_JJA_clim)
LWD_JJA_anom.to_csv(store_path + 'LWD_JJA_anomalies.csv')


# # SHF anomalies --------------------------------------------------------------

SHF_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SHF.sel(X=x_slice, 
		Y=y_slice)) * -1

SHF_JJA_clim = SHF_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SHF_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME')).to_pandas()

SHF_JJA = SHF_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(SHF_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
SHF_JJA.to_csv(store_path + 'SHF_JJA_absolute_mean.csv')

SHF_JJA_anom = (SHF_JJA - SHF_JJA_clim)
SHF_JJA_anom.to_csv(store_path + 'SHF_JJA_anomalies.csv')


# Absolute SHF - for Andy
SHF_abs = SHF_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')) \
	.to_pandas().resample('24H').first()
SHF_abs.to_csv(store_path + 'SHF_abs.csv')	


# Precip ---------------------------------------------------------------------
RF_all = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.RF.sel(X=x_slice, 
		Y=y_slice))

RF_JJA_sum = RF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(RF_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').to_pandas()
RF_JJA_sum.to_csv(store_path + 'RF_JJA_sum.csv')

SF_all = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SF.sel(X=x_slice, 
		Y=y_slice))

SF_JJA_sum = SF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(RF_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').to_pandas()
SF_JJA_sum.to_csv(store_path + 'SF_JJA_sum.csv')

SF_bare_sum = SF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(periods_bare2end) \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').to_pandas()
SF_bare_sum.to_csv(store_path + 'SF_bare_sum.csv')


## From precip_events.py -----------------------------------------------------

# Rainfall event markers
RF_avg = RF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')).to_pandas()
RF_avg.to_csv(store_path + 'RF_daily_common_mean.csv')

# Snowfall
SF_avg = SF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')).to_pandas()
SF_avg.to_csv(store_path + 'SF_daily_common_mean.csv')





##############################################################################
## Xavier-suggested way of computing anomlies
SHF_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SHF.sel(X=x_slice, 
		Y=y_slice)) * -1

SHF_clim_daily = SHF_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y')) \
	.load() \
	.rolling(TIME=10).mean(dim='TIME')
SHF_clim_daily = SHF_clim_daily.groupby('TIME.dayofyear').mean('TIME')


SHF_daily = SHF_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.mean(dim=('X', 'Y'))

SHF_bare_anom_daily = (SHF_daily.groupby('TIME.dayofyear') - SHF_clim_daily) \
	.where(periods_bare2end) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
SHF_JJA_anom_daily.to_csv(store_path + 'SHF_anomalies_bare.csv')