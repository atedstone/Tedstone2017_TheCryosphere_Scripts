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
		'snow_sum_bare': read_data(store_path + 'SF_bare_sum.csv', 'sf_bare_sum')
	})

print(df_jja.corr(method='spearman').round(2))

df_jja.to_excel('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/statistics_df_jja.xls')
## Implement tests for normality...but do they actually tell us anything? (see belog post...)




### Regression for JJA annual values -----------------------------------------

X_vars = ('SHF_anom', 'melt_rate_JJA_anomaly', 'melt_rate_bare', 'snow_clear_doy', 'ttmin_count', 'LWD_SHF_vs_SWD', 'RF_sum', 'snow_sum_JJA', 'snow_sum_bare', 'SWD_anom', 'LWD_anom')
Y_vars = ('B01_avg', 'B01_avg_bare', 'dark_perc', 'dark_norm', 'dark_norm_bare', 'SHF_anom')

r2 = []
p = []
xx = []
for Y_var in Y_vars:
	for X_var in X_vars:
		X = df_jja[X_var]
		y = df_jja[Y_var]
		X = sm.add_constant(X)
		model = sm.OLS(y, X) # or QuantReg
		results = model.fit() # if QuantReg, can pass p=percentile here
		print(results.summary())
		r2.append(results.rsquared)
		p.append(results.pvalues[1])
		xx.append(results.params[1])



### Scatters of most important variables only --------------------------------

plt.figure(figsize=(15,9))
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

		plt.title('R2 %.2f, p %.2f' %(r2[n-1], p[n-1]))
		n += 1

plt.tight_layout()		
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/jja_scatter_3.pdf')
plt.close()


### Scatters for paper
X_vars = ('SHF_anom', 'melt_rate_JJA_anomaly', 'snow_clear_doy', 'ttmin_count', 'LWD_SHF_vs_SWD', 'snow_sum_bare')
Y_vars = ('B01_avg', 'dark_norm')
plt.figure(figsize=(10, 5))
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

		#plt.title('R2 %.2f, p %.2f' %(r2[n-1], p[n-1]))
		n += 1

plt.tight_layout()		
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/scatter_paper.pdf')


