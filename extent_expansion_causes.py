from prep_env_vars import *
import pandas as pd

df = pd.read_csv(store_path + 'timeseries_df.csv', index_col=0, parse_dates=True)


### Add data columns 

# Add TTMIN column
ttmin = pd.read_csv(store_path + 'TTMIN_daily.csv', index_col=0, skiprows=1, header=None, parse_dates=True).squeeze()
df = df.assign(ttmin=ttmin)

# Remove non-JJA data
df = df[(df.index.month >= 6) & (df.index.month < 9)]

# Compute n.days of continuous TTMIN > 0
results = []
for year, data in df.ttmin.groupby(df.index.year):
	only = data[(data.index.month >= 6) & (data.index.month < 9)]
	only = only.where(only > 0, np.nan)
	only[only.notnull()] = 1
	v = only
	n = v.isnull()
	a = ~n
	c = a.astype(float).cumsum()
	index = c[n].index  # need the index for reconstruction after the np.diff
	d = pd.Series(np.diff(np.hstack(([0.], c[n]))), index=index)
	v[n] = -d
	result = v.cumsum()
	results.append(result)
r = pd.concat(results)
# Add count to dataframe
df = df.assign(ttmin_cont=r)

# Compute n.days of 'continuous' cloudiness
results = []
for year, data in df.cloud_perc.groupby(df.index.year):
	only = data[(data.index.month >= 6) & (data.index.month < 9)]
	only = only.where(only > 50, np.nan)
	only[only.notnull()] = 1
	v = only
	n = v.isnull()
	a = ~n
	c = a.astype(float).cumsum()
	index = c[n].index  # need the index for reconstruction after the np.diff
	d = pd.Series(np.diff(np.hstack(([0.], c[n]))), index=index)
	v[n] = -d
	result = v.cumsum()
	results.append(result)
r = pd.concat(results)
# Add count to dataframe
df = df.assign(clouds_cont=r)

# Compute daily dark ice extent increase and add to df
df = df.assign(darkice_increase=df.darkice_cumsum.diff())

# Remove days when no dark ice has appeared yet
df = df[df.darkice_cumsum > 0]

## Categorise dark ice increase days
# common area size in km
ca = 10409
df = df.assign(big=np.where(((100 / ca) * df.darkice_increase >= 5) & (df.darkice_cumsum < ca-1040), 1, 0))
df = df.assign(massive=np.where(((100 / ca) * df.darkice_increase >= 10) & (df.darkice_cumsum < ca-1040), 1, 0))

df = df.assign(cloud_7d_mean=df.cloud_perc.rolling(7).mean())
df = df.assign(cloud_7d_std=df.cloud_perc.rolling(7).std())

### Analysis, Part A - check that big expansion events aren't an artefact of 
### several days preceding cloud cover


print('N.obs .... big: %s, rest: %s' % (df[df.big == 1].count(), df[df.big == 0].count()))
print('N.days preceding cloud cover > 50 perc .... big: %s, rest: %s' % (df[df.big == 1].clouds_cont.mean(), df[df.big == 0].clouds_cont.mean()))
print('TTMIN_count .... big: %s, rest: %s' % (df[df.big == 1].ttmin_cont.median(), df[df.big == 0].ttmin_cont.median()))
print('SHF .... big: %s, rest: %s' % (df[df.big == 1].SHF.mean(), df[df.big == 0].SHF.mean()))
print('SHFstd .... big: %s, rest: %s' % (df[df.big == 1].SHF.std(), df[df.big == 0].SHF.std()))

print('cloud_7d_mean .... big: %s, rest: %s' % (df[df.big == 1].cloud_7d_mean.mean(), df[df.big == 0].cloud_7d_mean.mean()))
print('cloud_7d_std .... big: %s, rest: %s' % (df[df.big == 1].cloud_7d_std.mean(), df[df.big == 0].cloud_7d_std.mean()))


# Percentage increase in absolute SHF on dark expanison days
(100 / 29) * 57




### Stuff below this line not currently in use ----------------------------


# Compute SWnet
df = df.assign(sw_net=df.SW * (1 - (df.al / 100)))

# Energy flux anomalies
df = df.assign(shf_anomaly=df.SHF - df.SHF.mean())
df = df.assign(sw_anomaly=df.SW - df.SW.mean())
df = df.assign(lw_anomaly=df.LW - df.LW.mean())

# Cumulative energy fluxes
df = df.assign(shf_cum=df.SHF.rolling(7).sum())
df = df.assign(sw_net_cum=df.sw_net.rolling(7).sum())
df = df.assign(lw_cum=df.LW.rolling(7).sum())

df = df.assign(shf_perc=(100 / df.shf_cum) * df.SHF)

df = df.assign(shf_2d=df.SHF.rolling(2).sum())


## Create df of weekly conditions, with appropriate aggregation
# Rolling??
# Could specify window type if desired
df_weekly = df.rolling(window=7).agg({'darkice_increase':np.sum, 
	'al':np.mean, 
	'SHF':np.sum, 
	'ttmin_cont':np.argmax, 
	'ttmin':np.mean, 
	'SW':np.sum, 
	'LW':np.sum,
	'cloud_perc':np.max})
df_weekly = df_weekly.assign(daily_contrib=(100 / df_weekly.darkice_increase) * df.darkice_increase)
df_weekly = df_weekly.assign(darkice_today=df.darkice_increase)


from scipy import stats
stat, pval = stats.ks_2samp(df_big.ttmin_cont, df_other.ttmin_cont)

stats.mannwhitneyu(df_big.ttmin_cont, df_other.ttmin_cont)
stats.ranksums(df_big.ttmin_cont, df_other.ttmin_cont)