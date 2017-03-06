"""

Identify precipitation events, then examine their impact upon b01.

"""

from prep_env_vars import *


## Rain
RF_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.RF.sel(X=x_slice, 
		Y=y_slice))		

# Rainfall event markers
RF = RF_all.where(mar_mask_dark.r > 0).mean(dim=('X', 'Y'))
RF_pd = RF.to_pandas().to_frame()
RF_pd.columns = ('RF',)

# Dates of last day of rainfall in any 1-day or multi-day rain event
RF_pd['rain'] = np.where(RF_pd.RF > 1, 1, 0)
rain_events = (RF_pd['rain'].shift(1) - RF_pd['rain']).shift(-1)
rain_events = rain_events.where(rain_events == 1, other=0)

# Duration of each rain event, corresponding with each marker as above
# see http://stackoverflow.com/questions/18196811/cumsum-reset-at-nan
v = pd.Series(np.where(RF_pd.RF > 1, 1, np.nan), index=RF_pd.index)
n = v.isnull()
a = ~n
c = a.cumsum()
index = c[n].index  # need the index for reconstruction after the np.diff
d = pd.Series(np.diff(np.hstack(([0.], c[n]))), index=index)
v[n] = -d
d_rain = v.cumsum()
d_rain = d_rain[rain_events == 1]



## Snow
SF_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.SF.sel(X=x_slice, 
		Y=y_slice))

# Snowfall event markers
sf = SF_all.where(mar_mask_dark.r > 0).mean(dim=('X', 'Y'))
SF_pd = sf.to_pandas().to_frame()
SF_pd.columns = ('SF',)

# Dates of last day of snowfall in any 1-day or multi-day snow event
SF_pd['snow'] = np.where(SF_pd.SF > 1, 1, 0)
snow_events = (SF_pd['snow'].shift(1) - SF_pd['snow']).shift(-1)
snow_events = snow_events.where(snow_events == 1, other=0)

# Duration of each snow event, corresponding with each marker as above
# see http://stackoveSFlow.com/questions/18196811/cumsum-reset-at-nan
v = pd.Series(np.where(SF_pd.SF > 1, 1, np.nan), index=SF_pd.index)
n = v.isnull()
a = ~n
c = a.cumsum()
index = c[n].index  # need the index for reconstruction after the np.diff
d = pd.Series(np.diff(np.hstack(([0.], c[n]))), index=index)
v[n] = -d
d_snow = v.cumsum()
d_snow = d_snow[snow_events == 1]


# Get b01 loaded if it isn't already...
# need to load b01 from plot_b01_heatmap.py at the moment


## Combine the indicators
precip = pd.DataFrame({'e_snow': snow_events.resample('1D').first(),
					   'e_rain': rain_events.resample('1D').first(),
					   'd_snow': d_snow.resample('1D').first(), 
					   'd_rain': d_rain.resample('1D').first(),
					   'b01': b01_ts})


## Analysis
# Look at JJA only
precip_jja = precip[(precip.index.month >= 6) & (precip.index.month <= 8)]
precip_jja = precip_jja.assign(b01_pad=precip_jja.b01.fillna(method='pad', limit=3))

precip_jja[(precip_jja.e_rain.shift(1) == 1) & (precip_jja.e_snow.shift(1) == 0) & (precip_jja.d_rain > 1) & (precip_jja.b01 <= 0.45)].diff(3).describe()
