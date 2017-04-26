from prep_env_vars import *
#from statistics import *


## Re-implement data loading logic here, remove to_pandas() calls below

# ============================================================================


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
rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(3.5, 4))
xticks = ['2000-01-01', '2002-01-01', '2004-01-01', '2006-01-01', '2008-01-01', '2010-01-01', '2012-01-01', '2014-01-01', '2016-01-01']


## Subplot: radiative fluxes -------------------------------------------------
ax_rad = plt.subplot(3, 1, 1)

plt.axhline(y=0, color='gray', linewidth=0.5)

LWD_JJA_anom_pd = read_data(store_path + 'LWD_JJA_anomalies.csv', 'LWD')
plt.plot(LWD_JJA_anom_pd.index, LWD_JJA_anom_pd, label='LW$\downarrow\prime$', marker='o', color='#E31A1C', markersize=4, mec='none')
SWD_JJA_anom_pd = read_data(store_path + 'SWD_JJA_anomalies.csv', 'SWD')
plt.plot(SWD_JJA_anom_pd.index, SWD_JJA_anom_pd, label='SW$\downarrow\prime$', marker='o', color='#377EB8', markersize=4, mec='none')
SHF_JJA_anom_pd = read_data(store_path + 'SHF_JJA_anomalies.csv', 'SHF')
plt.plot(SHF_JJA_anom_pd.index, SHF_JJA_anom_pd, label='SHF$\prime$', marker='o', color='black', markersize=4, mec='none')
plt.legend(numpoints=1, loc=8, frameon=False, ncol=3)
plt.ylim(-25, 25)
plt.ylabel('W m$^{-2}$', labelpad=7)

plt.xticks(xticks, [])
plt.xlim('1999-01-01', '2017-06-01')

#ax_rad.spines['left'].axis.axes.tick_params(direction='outward')
ax_rad.tick_params(axis='y', direction='out')
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

dark_norm = read_data(store_path + 'dark_norm_JJA.csv','dark_norm')
plt.plot(dark_norm.index, dark_norm, color='black', markersize=4, mec='none', marker='o', label='Norm. Dark.', zorder=5)
plt.ylim(0, 1.4)
plt.yticks([0, 0.4, 0.8, 1.2, 1.6], [0, 0.4, 0.8, 1.2, 1.6])
plt.tick_params(axis='x', bottom='off', top='off')
plt.ylabel('$D_N$', labelpad=8)
plt.xticks(xticks, [])
plt.xlim('1999-01-01', '2017-06-01')

ax_precip = plt.twinx()

precip_pd = read_data(store_path + 'RF_JJA_sum.csv', 'RF').to_frame()
precip_pd = precip_pd.assign(width=132.5)
snow_pd = read_data(store_path + 'SF_bare_sum.csv', 'SF').to_frame()
snow_pd = snow_pd.assign(width=132.5)
# Deal with leap years
#precip_pd.loc[precip_pd.index.is_leap_year, 'width'] = 366 - 100
plt.bar(snow_pd.index, snow_pd['SF'], width=snow_pd['width'], color='#6A51A3', linewidth=0, label='Snow', zorder=2)
plt.bar(precip_pd.index + dt.timedelta(days=132.5), precip_pd['RF'], width=precip_pd['width'], color='#377EB8', linewidth=0, label='Rain', zorder=2)
plt.legend(numpoints=1, loc=9, frameon=False, ncol=2)

plt.ylim(0, 200)
plt.yticks([0, 40, 80, 120, 160], [0, 40, 80, 120, 160])
plt.tick_params(axis='x', bottom='off', top='off')
plt.ylabel('mm W.E. y$^{-1}$')
plt.xticks(xticks, [])
plt.xlim('1999-01-01', '2017-06-01')

ax_dark.set_zorder(ax_precip.get_zorder() + 1)
ax_dark.patch.set_visible(False)

#ax_dark.spines['left'].axis.axes.tick_params(direction='outward')
ax_dark.tick_params(axis='y', direction='out')
ax_dark.yaxis.tick_left()
ax_dark.spines['top'].set_visible(False)
ax_dark.spines['right'].set_visible(False)
ax_dark.spines['bottom'].set_visible(False)
ax_dark.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top', zorder=10)

#ax_precip.spines['right'].axis.axes.tick_params(direction='outward')
ax_precip.tick_params(axis='y', direction='out')
ax_precip.yaxis.tick_right()
plt.tick_params(axis='x', bottom='off', top='off')
ax_precip.spines['top'].set_visible(False)
ax_precip.spines['left'].set_visible(False)
ax_precip.spines['bottom'].set_visible(False)



## Subplot: MOF --------------------------------------------------------------

ax_ratios = plt.subplot(3, 1, 3)

LWout = 315.6  # Cuffey & Paterson (2010) p.148

# Read CSV created by export_df_hodson.py
df = pd.read_csv(store_path + 'b01_shf_lw_sw_al_cusum.csv', 
	index_col=0, parse_dates=True)

SWnet = df['SW'] * (1 - (df['AL'] / 100))

MOF = df['SHF'] + df['LW'] - LWout - SWnet
MOF = MOF[:'2016-08-31'] #cull september so that periods match with MAR data

MOF_JJA_mean = MOF.where((MOF.index.month >= 6) & (MOF.index.month < 9)) \
	.resample('1AS') \
	.mean()
MOF_JJA_mean.to_csv(store_path + 'MOF_JJA_mean.csv')	

MOF_bare_mean = MOF.where(periods_bare2end) \
	.resample('1AS') \
	.mean()
MOF_bare_mean.to_csv(store_path + 'MOF_bare_mean.csv')	

MOF_JJA_std = MOF.where((MOF.index.month >= 6) & (MOF.index.month < 9)) \
	.resample('1AS') \
	.std()

MOF_bare_std = MOF.where(periods_bare2end) \
	.resample('1AS') \
	.std()

# MOF_JJA_max = MOF.where((MOF.index.month >= 6) & (MOF.index.month < 9)) \
# 	.resample('1AS') \
# 	.max()	

plt.errorbar(MOF_JJA_mean.index, MOF_JJA_mean, yerr=MOF_JJA_std * 3, 
	marker='o', color='black', markersize=4, mec='none',
	elinewidth=0.5, ecolor='gray', 
	label='$SHF + LW_{net} - SW_{net}$')

# plt.plot(MOF_JJA_max.index, MOF_JJA_max, marker='o', mfc='none', mec='black', 
# 	markersize=3, color='none')

#plt.legend(numpoints=0, loc=7, frameon=False, ncol=2)
plt.ylabel('MOF (W m$^{-2}$)')
#plt.ylim(-230, 0)
#plt.yticks([-, -80, -60, -40, -20, 0], [-100, -80, -60, -40, -20, 0])

plt.xlabel('Year')

#ax_ratios.spines['left'].axis.axes.tick_params(direction='outward')
ax_ratios.tick_params(axis='y', direction='out')
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
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/energy_fluxes_MOF.pdf')