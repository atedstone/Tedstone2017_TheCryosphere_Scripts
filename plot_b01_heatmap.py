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
	cb_ax = fig.add_axes((0.9, 0.15, 0.02, 0.75))
	h = sns.heatmap(b01_piv.T, ax=ax, cmap='YlOrRd_r', vmin=0.1, vmax=0.9, cbar_ax=cb_ax, cbar_kws=dict(label='B01 reflectance', ticks=(0.1, 0.3, 0.5, 0.7, 0.9)))
	plt.yticks(rotation=0)
	plt.xlabel('Date', fontsize=6)
	plt.ylabel('Year', fontsize=6)
	plt.xlim(0, 273-121)
	plt.xticks(np.array([121, 152, 182, 213, 244])-121, ['1 May', '1 Jun', '1 Jul', '1 Aug', '1 Sep'])

	ax.xaxis.set_tick_params(length=3, pad=1, width=0.5)
	ax.spines['bottom'].axis.axes.tick_params(direction='outward')

	plt.savefig('/home/at15963/Dropbox/work/black_and_bloom/papers/tedstone_darkice/submission1/figures/B01.pdf')