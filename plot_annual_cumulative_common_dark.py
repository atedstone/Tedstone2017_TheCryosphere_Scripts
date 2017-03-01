from prep_env_vars import *

plt.figure()
n = 1
for year in onset.TIME:

	ax = subplot(2, 9, n)

	hist, bin_edges = np.histogram(onset.sel(TIME=year).dark.where(mask_dark > 0).where(onset.dark < 240).values,
		range=(152, 239), bins=239-152)

	hist = hist * 0.377
	plt.plot(bin_edges[:-1], np.cumsum(hist), '-', color='#08306B')
	# change this to only be plotted when there are 'sufficient' good quality obs.
	#plt.plot(bin_edges[:-1], np.cumsum(hist), 'o', mec='#08306B', mfc='none', markersize=4, alpha=0.4)
	plt.title(pd.to_datetime(year.values).strftime('%Y'))

	plt.ylim(0, 100000)
	plt.yticks([0, 20000, 40000, 60000, 80000, 100000], [0, 2, 4, 6, 8, 10])
	if n in (1, 10):
		plt.ylabel('x 10$^4$ km$^3$')
	plt.xticks([150, 170, 190, 210, 230], [150, 170, 190, 210, 230])

	n += 1