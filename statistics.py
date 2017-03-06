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

# B01 average post-bare
B01_avg_bare = b01_avg.where(modis_periods_bare2end) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()


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


dark_perc = toplot.median(dim=('X', 'Y')).to_pandas()
B01_avg = b01_avg.where(b01_avg['TIME.season'] == 'JJA').resample('1AS', dim='TIME', how='mean').to_pandas()
dark_norm = dark_perc / (B01_avg * 100)

### Construct data frames ----------------------------------------------------

# ideally need some flickering metric as well.
df_jja = pd.DataFrame({
		'SWD_anom': SWD_JJA_anom.to_pandas(),
		'LWD_anom': LWD_JJA_anom.to_pandas(),
		'SHF_anom': SHF_JJA_anom.to_pandas(),
		'RF_avg': RF_avg.to_pandas(),
		'dark_perc': dark_perc,
		'B01_avg': B01_avg,
		'B01_avg_bare': B01_avg_bare,
		'dark_norm': dark_norm,
		'melt': ME_JJA_anom.to_pandas().squeeze(),
		'snow_clear_doy': onset.bare.where(mask_dark > 0).mean(dim=['X','Y']).to_pandas(),
		'ttmin_count': ttmin_JJA_count_pd,
		'LWD_SHF_vs_SWD': ((LWD_JJA + SHF_JJA) / SWD_JJA).to_pandas()
	})

print(df_jja.corr(method='spearman').round(2))

df_jja.to_excel('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/statistics_df_jja.xls')
## Implement tests for normality...but do they actually tell us anything? (see belog post...)




### Regression for JJA annual values -----------------------------------------

X_vars = ('SHF_anom', 'melt', 'snow_clear_doy', 'ttmin_count', 'LWD_SHF_vs_SWD')
Y_vars = ('B01_avg', 'B01_avg_bare', 'dark_perc', 'dark_norm')

for Y_var in Y_vars:
	for X_var in X_vars:
		X = df_jja[X_var]
		y = df_jja[Y_var]
		X = sm.add_constant(X)
		model = sm.OLS(y, X) # or QuantReg
		results = model.fit() # if QuantReg, can pass p=percentile here
		print(results.summary())



### Scatters of most important variables only --------------------------------

plt.figure()
n = 1
for y_var in Y_vars:
	for x_var in X_vars:
		ax = subplot(4, 5, n)
		plt.plot(df_jja[x_var], df_jja[y_var], 'o', mfc='#377EB8', mec='none', alpha=0.8)
		if y_var == 'dark_norm':
			plt.xlabel(x_var)
		
		if x_var == 'SHF_anom':
			plt.ylabel(y_var)
		else:
			yticks, ylabels = plt.yticks()
			plt.yticks(yticks, [])
		n += 1

