from prep_env_vars import *

mod10 = xr.open_mfdataset('/scratch/MOD10A1.006.SW/*.nc', chunks={'TIME':366})

b01 = ds_refl.sur_refl_b01_1.where(mask_dark > 0)
b02 = ds_refl.sur_refl_b02_1.where(mask_dark > 0)
al = mod10.Snow_Albedo_Daily_Tile.where(mask_dark > 0)

tot_px = mask_dark.where(mask_dark > 0).count(dim=('X', 'Y'))
cloudy = al.where(al == 150).where(mask_dark > 0).count(dim=('X', 'Y'))
daily_perc_cloudy = (100 / tot_px) * cloudy

ice = b02.where(b02 < 0.6).where(mask_dark > 0).count(dim=('X', 'Y'))
daily_perc_ice = (100 / tot_px) * ice

b01_avg = b01.where(al <= 100).where(mask_dark > 0).mean(dim=('X', 'Y'))

#b01_avg = b01_avg.where(daily_perc_cloudy <= 50).where(daily_perc_ice > 90)
b01_avg = b01_avg.where(daily_perc_cloudy <= 50)

SF_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.SF.sel(X=x_slice, 
		Y=y_slice))

RF_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.RF.sel(X=x_slice, 
		Y=y_slice))		


# Snowline clearing markers
bare_doy_med_masked_common = onset.bare.where(mask_dark > 0).median(dim=['X','Y'])
# Remove the window duration from the date to get the true snowline retreat date
bare_doy_med_masked_common -= 4 
# compare to mar?
# kinda a fiddle at the moment
# and the point is to understand what MODIS is seeing, so its version of snow clearing might be more helpful


# Snowfall event markers
sf = SF_all.where(mar_mask_dark.r > 0).mean(dim=('X', 'Y'))
sf_pd = sf.to_pandas().to_frame()
sf_pd['Year'] = sf_pd.index.year
sf_pd['DOY'] = sf_pd.index.dayofyear
sf_piv = pd.pivot_table(sf_pd, index='DOY', columns='Year', values=0)
sf_piv[sf_piv >= 1] = 1
sf_piv[sf_piv < 1] = 0
sf_piv = sf_piv


# Rainfall event markers
RF = RF_all.sel(TIME=slice('2000', '2016')).where(mar_mask_dark.r > 0).mean(dim=('X', 'Y'))
RF_pd = RF.to_pandas().to_frame()
RF_pd['Year'] = RF_pd.index.year
RF_pd['DOY'] = RF_pd.index.dayofyear
RF_piv = pd.pivot_table(RF_pd, index='DOY', columns='Year', values=0)
RF_piv[RF_piv >= 1] = 1
RF_piv[RF_piv < 1] = 0
RF_piv = RF_piv

combined = RF_piv + sf_piv

if __name__ == '__main__':

	import seaborn as sns

	b01_pd = b01_avg.to_pandas().to_frame()
	b01_pd['Year'] = b01_pd.index.year
	b01_pd['DOY'] = b01_pd.index.dayofyear
	b01_piv = pd.pivot_table(b01_pd, index='DOY', columns='Year', values=0)

	rcParams['font.size'] = 6
	rcParams['axes.labelsize'] = 6 # sets colorbar label size
	rcParams['legend.fontsize'] = 6
	rcParams['xtick.labelsize'] = 6
	rcParams['ytick.labelsize'] = 6
	rcParams['xtick.direction'] = 'in'
	rcParams['xtick.major.pad'] = 3
	rcParams['figure.titlesize'] = 6

	fig = plt.figure(figsize=(5.5, 2.5))
	ax = plt.subplot(111)
	plt.subplots_adjust(right=0.88, bottom=0.15)
	#cb_ax = fig.add_axes((0.9, 0.15, 0.02, 0.75))
	h = sns.heatmap(b01_piv.T, ax=ax, cmap='YlOrRd_r', vmin=0.1, vmax=0.9, cbar_kws=dict(label='B01 reflectance', ticks=(0.1, 0.3, 0.5, 0.7, 0.9))) 
	plt.yticks(rotation=0)
	plt.xlabel('Date', fontsize=6)
	plt.ylabel('Year', fontsize=6)
	plt.xlim(0, 273-121)
	plt.xticks(np.array([121, 152, 182, 213, 244])-121, ['1 May', '1 Jun', '1 Jul', '1 Aug', '1 Sep'])

	ax.xaxis.set_tick_params(length=3, pad=1, width=0.5)
	ax.spines['bottom'].axis.axes.tick_params(direction='outward')

	# n = 17
	# x = np.arange(0, 273-121)
	# for year, series in sf_piv[121:273].T.iterrows():
	# 	data = np.where(series == 1, n - 0.9, np.nan)
	# 	plt.plot(x + 0.5, data, 's', markersize=1.5, mfc='black', mec='none')
	# 	n -= 1

	# n = 17
	# x = np.arange(0, 273-121)
	# for year, series in RF_piv[121:273].T.iterrows():
	# 	data = np.where(series == 1, n - 0.7, np.nan)
	# 	plt.plot(x + 0.5, data, 's', markersize=1.5, mfc='#737373', mec='none')
	# 	n -= 1

	# n = 17
	# x = np.arange(0, 273-121)
	# for year, series in combined[121:273].T.iterrows():
	# 	series_clean = series[series > 0]
	# 	#pos = np.where(series > 0, n - 0.1, np.nan)
	# 	series_x = series_clean.index.values - 121
	# 	y = np.zeros(len(series_x))
	# 	y[y == 0] = n - 0.1
	# 	plt.scatter(series_x + 0.5, y, s=1.5, c=series_clean.values, cmap='Set1', vmin=-1, vmax=3, edgecolors='none')
	# 	n -= 1

	n = 17
	for year in range(2000, 2017):
		clear = bare_doy_med_masked_common.sel(TIME=str(year)).values[0] - 121
		plt.plot(clear + 0.5, n - 0.5, '>', mfc='black', mec='none', markersize=3)
		n -= 1

	plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/B01.pdf')



