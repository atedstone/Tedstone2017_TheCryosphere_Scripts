from prep_env_vars import *

import statsmodels.api as sm
import matplotlib.pyplot as plt


### Construct data frames ----------------------------------------------------

lwd = read_data(store_path + 'LWD_JJA_absolute_mean.csv', 'LWD')
swd = read_data(store_path + 'SWD_JJA_absolute_mean.csv', 'SWD')
shf = read_data(store_path + 'SHF_JJA_absolute_mean.csv', 'SHF')
ratio = (lwd+shf) / swd

# ideally need some flickering metric as well.
df_jja = pd.DataFrame({
		'SWD_anom': read_data(store_path + 'SWD_JJA_anomalies.csv', 'SWD_anom'),
		'LWD_anom': read_data(store_path + 'LWD_JJA_anomalies.csv', 'LWD_anom'),
		'SHF_anom': read_data(store_path + 'SHF_JJA_anomalies.csv', 'SHF_anom'),
		'RF_sum': read_data(store_path + 'RF_JJA_sum.csv', 'RF_sum'),
		'dark_perc': read_data(store_path + 'B01_JJA_darkperc.csv', 'dark_perc'),
		'B01_avg': read_data(store_path + 'B01_avg_JJA.csv', 'B01_avg'),
		'B01_avg_bare': read_data(store_path + 'B01_avg_bareice_JJA.csv', 'B01_avg_bare'),
		'dark_norm': read_data(store_path + 'dark_norm_JJA.csv', 'dark_norm'),
		'dark_norm_bare': read_data(store_path + 'dark_norm_bare_JJA.csv', 'dark_norm_bare'),
		'melt_rate_JJA_anomaly': read_data(store_path + 'ME_JJA_meandailyrateanomaly.csv', 'melt_rate_anomaly'),
		'melt_rate_bare': read_data(store_path + 'ME_bare_meandailyrate.csv', 'melt_rate_bare'), ## not yet available
		'snow_clear_doy': onset.bare.where(mask_dark > 0).mean(dim=['X','Y']).to_pandas(),
		'ttmin_count': read_data(store_path + 'TTMIN_JJA_count.csv', 'ttmin_count'),
		'LWD_SHF_vs_SWD': ratio,
		'snow_sum_JJA': read_data(store_path + 'SF_JJA_sum.csv', 'sf_jja_sum'),
		'snow_sum_bare': read_data(store_path + 'SF_bare_sum.csv', 'sf_bare_sum'),
		'MOF': read_data(store_path + 'MOF_JJA_mean.csv', 'MOF_JJA_mean'),
		'TT': read_data(store_path + 'TT_JJA_mean.csv', 'TT_JJA_mean'),
		'NAO': read_data(store_path + 'NAO_JJA_mean.csv', 'NAO_JJA'),
		'GBI': read_data(store_path + 'GBI_JJA_mean.csv', 'GBI_JJA')
	})

print(df_jja.corr(method='spearman').round(2))

df_jja.to_excel('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/statistics_df_jja.xls')
## Implement tests for normality...but do they actually tell us anything? (see belog post...)




### Regression for JJA annual values -----------------------------------------

X_vars = ('SHF_anom', 'melt_rate_JJA_anomaly', 'melt_rate_bare', 'snow_clear_doy', 'ttmin_count', 'LWD_SHF_vs_SWD', 'RF_sum', 'snow_sum_JJA', 'snow_sum_bare', 'SWD_anom', 'LWD_anom', 'MOF', 'TT', 'NAO', 'GBI')
Y_vars = ('B01_avg', 'B01_avg_bare', 'dark_perc', 'dark_norm', 'dark_norm_bare', 'SHF_anom')

r2 = {}
p = {}
xx = {}
for Y_var in Y_vars:
	for X_var in X_vars:
		X = df_jja[X_var]
		y = df_jja[Y_var]
		X = sm.add_constant(X)
		model = sm.OLS(y, X) # or QuantReg
		results = model.fit() # if QuantReg, can pass p=percentile here
		print(results.summary())
		r2['%s_%s' %(X_var, Y_var)] = results.rsquared
		p['%s_%s' %(X_var, Y_var)] = results.pvalues[1]
		xx['%s_%s' %(X_var, Y_var)] = results.params[1]



### Scatters of most important variables only --------------------------------

plt.figure(figsize=(20,14))
n = 1
#Y_vars = ('dark_norm',)
for y_var in Y_vars:
	for x_var in X_vars:
		ax = plt.subplot(len(Y_vars), len(X_vars), n)
		plt.plot(df_jja[x_var], df_jja[y_var], 'o', mfc='#377EB8', mec='none', alpha=0.8)
		if y_var == Y_vars[-1]:
			plt.xlabel(x_var)
		
		if x_var == 'SHF_anom':
			plt.ylabel(y_var)
		else:
			yticks, ylabels = plt.yticks()
			plt.yticks(yticks, [])

		plt.title('R$^2$ %.2f, p %.2f' %(r2['%s_%s' %(x_var, y_var)], p['%s_%s' %(x_var, y_var)]))
		#plt.title('R2 %.2f, p %.2f' %(r2[n-1], p[n-1]))
		n += 1

plt.tight_layout()		
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/jja_scatter_3.pdf')
plt.close()


### Scatters for paper
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

X_vars = ('SHF_anom', 'snow_clear_doy', 'ttmin_count', 'TT')
Y_vars = ('B01_avg', 'dark_norm')

X_labels = ('SHF$\prime$ (W m$^{-2}$)', '$\\tilde{t_B}$', '$\sum{T > 0}$', 'T ($^o$C)')
Y_labels = ('$\\bar{D_I}$', '$D_N$')
letters = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
xlims = ((-10, 20), (150, 200), (0, 60), (-1, 1), (-10, 20), (150, 200), (0, 60), (-1, 1) )
ylims = ((0.4, 0.8), (0, 1.5))
anno_locs = ((0.1, 0.1), (0.7, 0.1), (0.1, 0.1), (0.1, 0.1), (0.1, 0.5), (0.6, 0.6), (0.1, 0.5), (0.1, 0.5))

plt.figure(figsize=(5.5, 3))
n = 1
#Y_vars = ('dark_norm',)
for y_var, y_label in zip(Y_vars, Y_labels):
	for x_var, x_label in zip(X_vars, X_labels):
		ax = plt.subplot(len(Y_vars), len(X_vars), n)
		plt.plot(df_jja[x_var], df_jja[y_var], 'o', mfc='gray', mec='none', 
			markersize=6, alpha=0.8)
		if y_var == Y_vars[-1]:
			plt.xlabel(x_label)

		ax.annotate('(%s)' % letters[n-1], fontsize=8, fontweight='bold', xy=(0.05,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

		ax.tick_params(axis='y', direction='out')
		ax.yaxis.tick_left()

		plt.tick_params(axis='x', direction='out')
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)

		if n <= 4:
			plt.ylim(ylims[0])
			xticks, xlabels = plt.xticks()
			plt.xticks(xticks, [])
		else:
			plt.ylim(ylims[1])
			plt.yticks((0, 0.5, 1), (0, 0.5, 1))

		if x_var == 'SHF_anom':
			plt.ylabel(y_label)
		else:
			yticks, ylabels = plt.yticks()
			plt.yticks(yticks, [])

		plt.xlim(xlims[n-1])

		if p['%s_%s' %(x_var, y_var)] < 0.01:
			p_here = 0.01
		elif p['%s_%s' %(x_var, y_var)] < 0.05:
			p_here = 0.05
		else:
			p_here = p['%s_%s' %(x_var, y_var)]

		ax.annotate('R$^2$ %.2f \np < %.2f' %(r2['%s_%s' %(x_var, y_var)], p_here), 
			fontsize=6, xy=anno_locs[n-1], xycoords='axes fraction',
			horizontalalignment='left')
		n += 1

plt.tight_layout()		
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/scatter_paper.pdf')


