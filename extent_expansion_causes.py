df = pd.read_csv(store_path + 'timeseries_df.csv', index_col=0, parse_dates=True)

# Add TTMIN column
ttmin = pd.read_csv(store_path + 'TTMIN_daily.csv', index_col=0, skiprows=1, header=None, parse_dates=True).squeeze()
df = df.assign(ttmin=ttmin)
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


# Add e.g. 'big' indicator column to be able to use seaborn facet options
