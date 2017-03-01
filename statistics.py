from prep_env_vars import *

from plot_energy_fluxes import *
from plot_b01_heatmap import *

import statsmodels.api as sm


### Import additional data  --------------------------------------------------

# Dark ice percentage
# Copied from plot_annual_duration_basemap.py - make sure they stay the same!
as_perc = (100. / ((243-152)-onset.bad_dur)) * onset.dark_dur
toplot = as_perc \
	.sel(TIME=slice('2000','2016')) \
	.where(onset.dark_dur > 5) \
	.where(mask_dark == 1)


# Melt anomaly
ME_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.ME.sel(X=x_slice, 
		Y=y_slice))

ME_JJA_clim = ME_all_long.sel(TIME=slice('1981', '2000')) \
	.isel(SECTOR1_1=0) \
	.where(mar_mask_dark.r > 0) \
	.where(ME_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME'))

ME_JJA = ME_all_long.sel(TIME=slice('2000', '2016')) \
	.isel(SECTOR1_1=0) \
	.where(mar_mask_dark.r > 0) \
	.where(ME_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').load()	

ME_JJA_anom = (ME_JJA - ME_JJA_clim).load()


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




### Construct data frames ----------------------------------------------------

# ideally need some flickering metric as well.
df_jja = pd.DataFrame({
		'SWD_anom': SWD_JJA_anom.to_pandas(),
		'LWD_anom': LWD_JJA_anom.to_pandas(),
		'SHF_anom': SHF_JJA.to_pandas(),
		'RF_avg': RF_avg.to_pandas(),
		'dark_perc': toplot.median(dim=('X', 'Y')).to_pandas(),
		'B01_avg': b01_avg.where(b01_avg['TIME.season'] == 'JJA').resample('1AS', dim='TIME', how='mean').to_pandas(),
		'melt': ME_JJA_anom.to_pandas().squeeze(),
		'snow_clear_doy': onset.bare.where(mask_dark > 0).mean(dim=['X','Y']).to_pandas(),
		'ttmin_count': ttmin_JJA_count_pd,
		'LWD_SHF_vs_SWD': ((LWD_JJA + SHF_JJA) / SWD_JJA).to_pandas()
	})

print(df.corr())

## Implement tests for normality...but do they actually tell us anything? (see belog post...)




### Regression for JJA annual values -----------------------------------------

X_vars = ('SHF_anom', 'melt', 'snow_clear_doy', 'ttmin_count', 'LWD_SHF_vs_SWD')

for X_var in X_vars:
	X = df_jja[X_var]
	y = df_jja.dark_perc #or B01_avg
	X = sm.add_constant(X)
	model = sm.OLS(y, X) # or QuantReg
	results = model.fit() # if QuantReg, can pass p=percentile here
	print(results.summary())

