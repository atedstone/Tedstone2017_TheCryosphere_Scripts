from prep_env_vars import *

plt.style.use('seaborn-white')
plt.figure()
n = 1
for year in onset.TIME:

	ax = subplot(2, 9, n)
	y = pd.to_datetime(year.values).strftime('%Y')

	hist, bin_edges = np.histogram(onset.sel(TIME=year).dark.where(mask_dark > 0).where(onset.dark < 240).values,
		range=(152, 239), bins=239-152)

	hist = hist * 0.377
	bin_dates = [dt.datetime.strptime('%s %s' %(y, int(b)), '%Y %j') for b in bin_edges]
	plt.plot(bin_dates[:-1], np.cumsum(hist), '-', color='#08306B')
	# change this to only be plotted when there are 'sufficient' good quality obs.
	#plt.plot(bin_edges[:-1], np.cumsum(hist), 'o', mec='#08306B', mfc='none', markersize=4, alpha=0.4)
	plt.title(y)

	plt.ylim(0, 100000)
	plt.yticks([0, 20000, 40000, 60000, 80000, 100000], [0, 2, 4, 6, 8, 10])
	if n in (1, 10):
		plt.ylabel('x 10$^4$ km$^3$')
	else:
		yticks, ylabels = plt.yticks()
		plt.yticks(yticks, [])
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('%m'))   
	#plt.xticks([150, 170, 190, 210, 230], [150, 170, 190, 210, 230])
	plt.grid('off')



	n += 1

# Plot amount of snow above ice on the same axes as above
# (requires data import from analyze_snow.py)
from matplotlib import dates
n = 1
for year, data in snow_above_ice.groupby(snow_above_ice.index.year):
	ax = plt.subplot(2, 9, n)
	ax2 = ax.twinx()
	plt.plot(data.index, data)
	#plt.title(year)
	plt.ylim(0, 1.5)
	plt.grid('off')
	if n in (9, 18):
		plt.ylabel('Snow depth above ice (m)')
	else:
		yticks, ylabels = plt.yticks()
		plt.yticks(yticks, [])
	n += 1








