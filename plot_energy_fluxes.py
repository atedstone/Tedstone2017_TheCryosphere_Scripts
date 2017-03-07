from prep_env_vars import *
from statistics import *

mar_path_anomalies = '/scratch/MARv3.6.2-7.5km-v2-ERA/ICE.*nc'

# Radiative fluxes -----------------------------------------------------------
SW_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SWD.sel(X=x_slice, 
		Y=y_slice))

LW_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.LWD.sel(X=x_slice, 
		Y=y_slice))

SWD_JJA_clim = SW_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME'))

LWD_JJA_clim = LW_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME'))

SWD_JJA = SW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(SW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').load()

LWD_JJA = LW_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(LW_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').load()

SWD_JJA_anom = (SWD_JJA - SWD_JJA_clim).load()
LWD_JJA_anom = (LWD_JJA - LWD_JJA_clim).load()


# SHF anomalies --------------------------------------------------------------

SHF_all_long = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SHF.sel(X=x_slice, 
		Y=y_slice)) * -1

SHF_JJA_clim = SHF_all_long.sel(TIME=slice('1981', '2000')) \
	.where(mar_mask_dark.r > 0) \
	.where(SHF_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y', 'TIME'))

SHF_JJA = SHF_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(SHF_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean').load()

SHF_JJA_anom = (SHF_JJA - SHF_JJA_clim).load()


# Precip ---------------------------------------------------------------------
RF_all = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.RF.sel(X=x_slice, 
		Y=y_slice))

RF_avg = RF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(RF_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').load()

SF_all = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.SF.sel(X=x_slice, 
		Y=y_slice))

SF_avg = SF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(RF_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').load()


# ============================================================================

if __name__ == '__main__':

	plt.style.use('default')
	rcParams['font.size'] = 6
	rcParams['font.sans-serif'] = 'Arial'
	rcParams['axes.labelsize'] = 6 # sets colorbar label size
	rcParams['legend.fontsize'] = 6
	rcParams['xtick.labelsize'] = 6
	rcParams['ytick.labelsize'] = 6
	#rcParams['xtick.direction'] = 'in'
	rcParams['xtick.major.pad'] = 3
	rcParams['figure.titlesize'] = 6

	fig = plt.figure(figsize=(3.5, 4))
	xticks = ['2000-01-01', '2002-01-01', '2004-01-01', '2006-01-01', '2008-01-01', '2010-01-01', '2012-01-01', '2014-01-01', '2016-01-01']

	## Subplot: radiative fluxes -------------------------------------------------
	ax_rad = plt.subplot(3, 1, 1)

	plt.axhline(y=0, color='gray', linewidth=0.5)

	LWD_JJA_anom_pd = LWD_JJA_anom.to_pandas()
	plt.plot(LWD_JJA_anom_pd.index, LWD_JJA_anom_pd, label='LWd', marker='o', color='#E31A1C', markersize=4, mec='none')
	SWD_JJA_anom_pd = SWD_JJA_anom.to_pandas()
	plt.plot(SWD_JJA_anom_pd.index, SWD_JJA_anom_pd, label='SWd', marker='o', color='#377EB8', markersize=4, mec='none')
	SHF_JJA_anom_pd = SHF_JJA_anom.to_pandas()
	plt.plot(SHF_JJA_anom_pd.index, SHF_JJA_anom_pd, label='SHF', marker='o', color='black', markersize=4, mec='none')
	plt.legend(numpoints=1, loc=8, frameon=False, ncol=3)
	plt.ylim(-25, 25)
	plt.ylabel('W m$^{-2}$')

	plt.xticks(xticks, [])
	plt.xlim('1999-01-01', '2017-06-01')

	ax_rad.spines['left'].axis.axes.tick_params(direction='outward')
	ax_rad.yaxis.tick_left()
	#ax_rad.xaxis.tick_bottom()
	plt.tick_params(axis='x', bottom='off', top='off')
	ax_rad.spines['top'].set_visible(False)
	ax_rad.spines['right'].set_visible(False)
	ax_rad.spines['bottom'].set_visible(False)
	ax_rad.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
	           horizontalalignment='left', verticalalignment='top')




	## Subplot: other fluxes -----------------------------------------------------
	ax_dark = plt.subplot(3, 1, 2)
	
	plt.plot(dark_norm.index, dark_norm, color='black', markersize=4, mec='none', marker='o', label='Norm. Dark.', zorder=5)
	plt.ylim(0, 1.4)
	plt.yticks([0, 0.4, 0.8, 1.2, 1.6], [0, 0.4, 0.8, 1.2, 1.6])
	plt.tick_params(axis='x', bottom='off', top='off')
	plt.ylabel('Normalised Darkness')
	plt.xticks(xticks, [])
	plt.xlim('1999-01-01', '2017-06-01')

	ax_precip = plt.twinx()

	precip_pd = RF_avg.to_pandas().to_frame()
	precip_pd = precip_pd.assign(width=132.5)
	snow_pd = SF_avg.to_pandas().to_frame()
	snow_pd = snow_pd.assign(width=132.5)
	# Deal with leap years
	#precip_pd.loc[precip_pd.index.is_leap_year, 'width'] = 366 - 100
	plt.bar(snow_pd.index, snow_pd[0], width=snow_pd['width'], color='#6A51A3', linewidth=0, label='Snow', zorder=2)
	plt.bar(precip_pd.index + dt.timedelta(days=132.5), precip_pd[0], width=precip_pd['width'], color='#377EB8', linewidth=0, label='Rain', zorder=2)
	plt.legend(numpoints=1, loc=9, frameon=False, ncol=2)

	plt.ylim(0, 200)
	plt.yticks([0, 40, 80, 120, 160], [0, 40, 80, 120, 160])
	plt.tick_params(axis='x', bottom='off', top='off')
	plt.ylabel('mmWE / year')
	plt.xticks(xticks, [])
	plt.xlim('1999-01-01', '2017-06-01')

	ax_dark.set_zorder(ax_precip.get_zorder() + 1)
	ax_dark.patch.set_visible(False)

	ax_dark.spines['left'].axis.axes.tick_params(direction='outward')
	ax_dark.yaxis.tick_left()
	ax_dark.spines['top'].set_visible(False)
	ax_dark.spines['right'].set_visible(False)
	ax_dark.spines['bottom'].set_visible(False)
	ax_dark.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
	           horizontalalignment='left', verticalalignment='top', zorder=10)

	ax_precip.spines['right'].axis.axes.tick_params(direction='outward')
	ax_precip.yaxis.tick_right()
	plt.tick_params(axis='x', bottom='off', top='off')
	ax_precip.spines['top'].set_visible(False)
	ax_precip.spines['left'].set_visible(False)
	ax_precip.spines['bottom'].set_visible(False)

	## Subplot: ratios (of absolute fluxes, not anomalies) -----------------------

	ax_ratios = plt.subplot(3, 1, 3)

	rat1 = (LWD_JJA / SWD_JJA).to_pandas()
	rat2 = ((LWD_JJA + SHF_JJA) / SWD_JJA).to_pandas()
	plt.plot(rat1.index, rat1, label='LWD:SWD', marker='o', color='black', markersize=4, mec='none')
	plt.plot(rat2.index, rat2, label='LWD+SHF : SWD', marker='o', color='black', linestyle=(0, (2,1)), markersize=4, mec='none')

	plt.ylabel('Ratio')
	plt.ylim(0.7, 1.1)
	plt.yticks([0.7, 0.8, 0.9, 1.0, 1.1], [0.7, 0.8, 0.9, 1.0, 1.1])

	plt.xlabel('Year')

	ax_ratios.spines['left'].axis.axes.tick_params(direction='outward')
	ax_ratios.yaxis.tick_left()
	ax_ratios.xaxis.tick_bottom()
	ax_ratios.spines['top'].set_visible(False)
	ax_ratios.spines['right'].set_visible(False)
	ax_ratios.spines['bottom'].set_position(('outward', 10))
	ax_ratios.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
	           horizontalalignment='left', verticalalignment='top')

	plt.xlim('1999-01-01', '2017-06-01')
	plt.xticks(xticks, ['2000', '2002', '2004', '2006', '2008', '2010', '2012', '2014', '2016'])


	plt.tight_layout()
	plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/energy_fluxes.pdf')