from prep_env_vars import *

mar_path_anomalies = '/scratch/MARv3.6.2-7.5km-v2-ERA/ICE.*nc'

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

SHF_JJA = (SHF_all_long.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(SHF_all_long['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='mean') - SHF_JJA_clim).load()


# Precip ---------------------------------------------------------------------
RF_all = mar_raster.open_mfxr(mar_path_anomalies,
	dim='TIME', transform_func=lambda ds: ds.RF.sel(X=x_slice, 
		Y=y_slice))

RF_avg = RF_all.sel(TIME=slice('2000', '2016')) \
	.where(mar_mask_dark.r > 0) \
	.where(RF_all['TIME.season'] == 'JJA') \
	.mean(dim=('X', 'Y')) \
	.resample('1AS', dim='TIME', how='sum').load()


# ============================================================================

fig = plt.figure(figsize=(3.5, 4))

## Subplot: radiative fluxes -------------------------------------------------
ax_rad = plt.subplot(3, 1, 1)

plt.axhline(y=0, color='gray', linewidth=0.5)

LWD_JJA_anom.plot(label='LWd', marker='o', color='#E31A1C', markersize=4, mec='none')
SWD_JJA_anom.plot(label='SWd', marker='o', color='#377EB8', markersize=4, mec='none')
#plt.legend(numpoints=1)
plt.ylim(-25, 25)
plt.ylabel('W m$^{-2}$')



ax_rad.spines['left'].axis.axes.tick_params(direction='outward')
ax_rad.yaxis.tick_left()
#ax_rad.xaxis.tick_bottom()
plt.tick_params(axis='x', bottom='off', top='off')
ax_rad.spines['top'].set_visible(False)
ax_rad.spines['right'].set_visible(False)
ax_rad.spines['bottom'].set_visible(False)
ax_rad.annotate('a', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')



## Subplot: other fluxes -----------------------------------------------------
ax_precip = plt.subplot(3, 1, 2, sharex=ax_rad)
precip_pd = RF_avg.to_pandas().to_frame()
precip_pd = precip_pd.assign(width=(365 - 100))
# Deal with leap years
precip_pd.loc[precip_pd.index.is_leap_year, 'width'] = 366 - 100
plt.bar(precip_pd.index, precip_pd[0], width=precip_pd['width'], color='#377EB8', linewidth=0)
plt.ylabel('mmWE / year')
plt.ylim(0, 200)
plt.yticks([0, 40, 80, 120, 160], [0, 40, 80, 120, 160])
plt.tick_params(axis='x', bottom='off', top='off')

# JJA total precip
ax_shf = plt.twinx()
SHF_JJA.plot(label='SHF', marker='o', color='black', markersize=4, mec='none')
plt.ylabel('W m$^{-2}$')

ax_precip.spines['left'].axis.axes.tick_params(direction='outward')
ax_precip.yaxis.tick_left()
#ax_precip.xaxis.tick_bottom()
ax_precip.spines['top'].set_visible(False)
ax_precip.spines['right'].set_visible(False)
ax_precip.spines['bottom'].set_visible(False)
ax_precip.annotate('b', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

ax_shf.spines['right'].axis.axes.tick_params(direction='outward')
ax_shf.yaxis.tick_right()
#ax_shf.xaxis.tick_bottom()
plt.tick_params(axis='x', bottom='off', top='off')
ax_shf.spines['top'].set_visible(False)
ax_shf.spines['left'].set_visible(False)
ax_shf.spines['bottom'].set_visible(False)

## Subplot: ratios (of absolute fluxes, not anomalies) -----------------------

ax_ratios = plt.subplot(3, 1, 3, sharex=ax_rad)
(LWD_JJA / SWD_JJA).plot(label='LWD : SWD', marker='o', color='black', markersize=4, mec='none')
((LWD_JJA + SHF_JJA) / SWD_JJA).plot(label='LWD+SHF : SWD', marker='o', color='black', linestyle=(0, (2,1)), markersize=4, mec='none')

plt.ylabel('Ratio')

plt.xlabel('Year')

ax_ratios.spines['left'].axis.axes.tick_params(direction='outward')
ax_ratios.yaxis.tick_left()
ax_ratios.xaxis.tick_bottom()
ax_ratios.spines['top'].set_visible(False)
ax_ratios.spines['right'].set_visible(False)
ax_ratios.spines['bottom'].set_position(('outward', 10))
ax_ratios.annotate('c', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

plt.tight_layout()
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/radiative_fluxes.pdf')