from prep_env_vars import *


# Snowline clearing markers
bare_doy_med_masked_common = onset.bare.where(mask_dark > 0).median(dim=['X','Y'])
# Remove the window duration from the date to get the true snowline retreat date
bare_doy_med_masked_common -= 4 
# compare to mar?
# kinda a fiddle at the moment
# and the point is to understand what MODIS is seeing, so its version of snow clearing might be more helpful


# Snowfall event markers
sf_pd = read_data(store_path + 'SF_daily_common_mean.csv', 'SF_mean')
sf_pd['Year'] = sf_pd.index.year
sf_pd['DOY'] = sf_pd.index.dayofyear
sf_piv = pd.pivot_table(sf_pd, index='DOY', columns='Year', values=0)
sf_piv[sf_piv >= 1] = 1
sf_piv[sf_piv < 1] = 0
sf_piv = sf_piv


# Rainfall event markers
RF_pd = read_data(store_path + 'RF_daily_common_mean.csv', 'RF_mean')
RF_pd['Year'] = RF_pd.index.year
RF_pd['DOY'] = RF_pd.index.dayofyear
RF_piv = pd.pivot_table(RF_pd, index='DOY', columns='Year', values=0)
RF_piv[RF_piv >= 1] = 1
RF_piv[RF_piv < 1] = 0
RF_piv = RF_piv

combined = RF_piv + sf_piv



import seaborn as sns

b01_pd = pd.read_csv(store_path + 'B01_avg_clouds50_daily.csv', names=['B01_avg'], index_col=0, parse_dates=True, skiprows=0)
b01_pd = b01_pd.assign(Year=b01_pd.index.year)
b01_pd = b01_pd.assign(DOY=b01_pd.index.dayofyear)
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
plt.xlabel('Day of Year', fontsize=6)
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
	if n == 17:
		plt.plot(clear + 0.5, n - 0.5, '>', mfc='black', mec='none', markersize=3, label='Day of winter snow clearing')
	else:
		plt.plot(clear + 0.5, n - 0.5, '>', mfc='black', mec='none', markersize=3)
	n -= 1

plt.legend(numpoints=1, loc=(0.69, 0.99), frameon=False, handletextpad=0.05)

plt.tight_layout()
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/B01.pdf')



