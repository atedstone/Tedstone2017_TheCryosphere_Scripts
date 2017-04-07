from prep_env_vars import *

from matplotlib import dates

plt.style.use('default')

rcParams['legend.fontsize'] = 6
rcParams['xtick.labelsize'] = 6
rcParams['figure.titlesize'] = 6
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.size'] = 6

fig = plt.figure(figsize=(5.5, 3))


## Copied from analyse_snow.py
SHSN2_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.SHSN2.sel(X=x_slice, 
		Y=y_slice))
snow_above_ice = SHSN2_all.sel(SECTOR1_1=1.0).where(mar_mask_dark.r > 0).where((SHSN2_all['TIME.month'] >= 4) & (SHSN2_all['TIME.month'] < 9)).mean(dim=('X', 'Y')).to_pandas()


# Plot amount of snow above ice on the same axes as above
# (requires data import from analyze_snow.py)
from matplotlib import dates
n = 1
for year, data in snow_above_ice.groupby(snow_above_ice.index.year):
	ax = plt.subplot(4, 5, n)
	plt.plot(data.index, data, color='#1D91C0', lw=2)
	#plt.title(year)
	plt.ylim(-0.05, 1.5)
	plt.grid('off')
	# if n in (9, 18):
	# 	plt.ylabel('Snow depth above ice (m)')
	# else:
	# 	yticks, ylabels = plt.yticks()
	# 	plt.yticks(yticks, [])

	ax.yaxis.tick_left()

	if n in (1, 6, 11, 16):
		plt.yticks([0, 0.5, 1, 1.5], [0, 0.5, 1, 1.5])
		ax.tick_params(axis='y', direction='out')

	else:
		plt.yticks([])
		ax.spines['left'].set_visible(False)
		plt.tick_params(axis='y', left='off', right='off')

	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)

	if n < 13:
		plt.tick_params(axis='x', bottom='off', top='off')
	else:
		plt.tick_params(axis='x', bottom='on', top='off')


	n += 1

csum_store = []
n = 1
for year in onset.TIME:

	ax = plt.subplot(4, 5, n)
	ax2 = ax.twinx()
	y = pd.to_datetime(year.values).strftime('%Y')

	hist, bin_edges = np.histogram(onset.sel(TIME=year).dark.where(mask_dark > 0).where(onset.dark < 240).values,
		range=(152, 239), bins=239-152)

	hist = hist * 0.377
	bin_dates = [dt.datetime.strptime('%s %s' %(y, int(b)), '%Y %j') for b in bin_edges]
	csum = np.cumsum(hist)
	plt.plot(bin_dates[:-1], csum, '-', color='#CB181D', lw=2, alpha=0.8)
	csum_pd = pd.Series(csum, index=bin_dates[:-1])
	csum_pd.to_csv(store_path + 'darkice_cumulative_%s.csv' %y)
	csum_store.append(csum_pd)

	# change this to only be plotted when there are 'sufficient' good quality obs.
	#plt.plot(bin_edges[:-1], np.cumsum(hist), 'o', mec='#08306B', mfc='none', markersize=4, alpha=0.4)

	plt.ylim(-5000, 120000)
	
	# if n in (1, 10):
	# 	plt.ylabel('x 10$^4$ km$^3$')
	# else:
	# 	yticks, ylabels = plt.yticks()
	# 	plt.yticks(yticks, [])
	ax2.xaxis.set_major_locator(dates.MonthLocator())
	ax2.xaxis.set_major_formatter(dates.DateFormatter('%m'))   
	#plt.xticks([150, 170, 190, 210, 230], [150, 170, 190, 210, 230])
	plt.grid('off')

	ax2.annotate(str(y), fontsize=6, fontweight='bold', xy=(0.5, 0.95), xycoords='axes fraction',
           horizontalalignment='center', verticalalignment='top',zorder=300)


	ax2.yaxis.tick_right()
	if n in (5, 10, 15, 17):
		plt.yticks([0, 40000, 80000, 120000], [0, 4, 8, 12])
		ax2.tick_params(axis='y', direction='out')
	else:
		plt.yticks([])
		ax2.spines['right'].set_visible(False)
		plt.tick_params(axis='y', left='off', right='off')

	ax2.spines['top'].set_visible(False)
	ax2.spines['left'].set_visible(False)

	if n < 13:	
		ax.spines['bottom'].set_visible(False)
		ax2.spines['bottom'].set_visible(False)
		plt.xticks(ax.xaxis.get_ticklocs(), [])
	else:
		ax2.tick_params(direction='out')
		ax.tick_params(direction='out')
		plt.tick_params(axis='x', bottom='on', top='off')

	if n == 17:
		plt.yticks([0, 40000, 80000], [0, 4, 8])
		
	n += 1


plt.subplots_adjust(wspace=0.1, hspace=0.2, bottom=0.1, top=0.98)

# Axis labels
fig.text(0.06, 0.61, 'Mean Snow Depth (m)', ha='center', va='center', 
	color='#1D91C0', rotation='vertical') 
fig.text(0.966, 0.63, 'Dark Ice Extent (x 10$^4$ km$^3$)', ha='center', 
	va='center', color='#CB181D', rotation='vertical') 
fig.text(0.51, 0.03, 'Month of Year', ha='center', va='center', color='black') 

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/snowdepth_darkice.pdf')

csum_all = pd.concat(csum_store)
csum_all.to_csv(store_path + 'cumulative_darkice.csv')





