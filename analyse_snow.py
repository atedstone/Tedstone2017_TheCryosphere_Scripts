""" 

Examine snow characteristics - melt rate, timing of disappearance, presence
of liquid meltwater in snowpack.

"""

from prep_env_vars import *


## Load datasets

## I think loading needs to stay here for the moment. This isn't a big deal, the major datasets to resolve
# are the ones which are used in multiple analysis files. These aren't just yet

SHSN2_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.SHSN2.sel(X=x_slice, 
		Y=y_slice))


WA1_all = mar_raster.open_mfxr(mar_path,
	dim='TIME', transform_func=lambda ds: ds.WA1.sel(X=x_slice, 
		Y=y_slice))




## Plot amount of snow above ice each spring
snow_above_ice = SHSN2_all.sel(SECTOR1_1=1.0).where(mar_mask_dark.r > 0).where((SHSN2_all['TIME.month'] >= 4) & (SHSN2_all['TIME.month'] < 9)).mean(dim=('X', 'Y')).to_pandas()
from matplotlib import dates
plt.figure()
n = 1
for year, data in snow_above_ice.groupby(snow_above_ice.index.year):
	ax = plt.subplot(2, 9, n)
	plt.plot(data.index, data)
	plt.title(year)
	plt.ylim(0, 1.5)
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('%m'))   
	n += 1



## Plot liquid water presence and mean snow depth across common dark area (2-d facets and a line)
import cmocean
fig = plt.figure()
n = 1
for year in range(2000, 2017):

	print(year)

	liquid_water = WA1_all.sel(TIME=str(year)).where(mar_mask_dark.r > 0) \
		.mean(dim=('X', 'Y'))

	ax = plt.subplot(2, 9, n)

	liquid_water.plot(ax=ax, vmin=0, vmax=0.2, add_colorbar=False, cmap=cmocean.cm.dense)

	snow_thick = SHSN2_all.sel(TIME=str(year), SECTOR1_1=1.0).where(mar_mask_dark.r > 0).mean(dim=('X', 'Y'))
	snow_thick_max = SHSN2_all.sel(TIME=str(year), SECTOR1_1=1.0).where(mar_mask_dark.r > 0).max(dim=('X', 'Y'))

	ax.plot(snow_thick, snow_thick.TIME, color='#E41A1C')
	ax.plot(snow_thick_max, snow_thick_max.TIME, '--', color='#E41A1C', alpha=0.7)

	plt.ylim('%s-04-01' % year, '%s-09-01' % year)
	plt.xlim(-0.03, 1.5)
	plt.ylabel('')
	plt.xlabel('')
	plt.xticks([0, 0.3, 0.6, 0.9, 1.2, 1.5])

	ax.yaxis.set_major_locator(dates.MonthLocator())
	ax.yaxis.set_major_formatter(dates.DateFormatter('%m'))   

	plt.title(year)
	n += 1


## Rate of snowpack removal
plt.figure()
from matplotlib import dates
n = 1
for year, data in snow_above_ice.groupby(snow_above_ice.index.year):
	ax = plt.subplot(2, 9, n, sharey=ax)
	data2 = data.rolling(7, freq='D').mean()
	plt.plot(data2.index, data2.diff())
	plt.title(year)
	plt.ylim(-0.1, 0.1)
	plt.grid('off')
	if n in (1, 10):
		plt.ylabel('Daily snowpack change (m)')
	else:
		yticks, ylabels = plt.yticks()
		#plt.yticks(yticks, [])
	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('%m'))   
	n += 1





## Not currently working below here
## At each pixel, trying to find out if meltwater is present at the snow-ice interface

# Mask OUTLAY so that, at each pixel, the only OUTLAY value present corresponds to the snow depth
# Squeeze OUTLAY so that only the value from the snow depth remains. (NOT the max value!)

new_da = WA1_all.sel(TIME='2016').where(mar_mask_dark.r > 0)
masked = new_da.where(new_da.OUTLAY <= SHSN2_all.sel(TIME='2016', SECTOR1_1=1.0).where(mar_mask_dark.r > 0))
max_depths = masked.last(dim='OUTLAY')

figure()
max_depths.mean(dim=('X', 'Y')).plot()
SHSN2_all.sel(TIME='2016', SECTOR1_1=1.0).where(mar_mask_dark.r > 0).mean(dim=('X', 'Y')).plot(color='blue')




WA1_all.sel(TIME='2016-05-13').sel(OUTLAY=SHSN2_all.sel(TIME='2016-05-13', SECTOR1_1=1.0), method='nearest')

WA1_all.loc[dict(TIME='2016', OUTLAY=SHSN2_all.sel(TIME='2016', SECTOR1_1=1.0), method='nearest')]


# is it a reducer function?

Xpt = slice(-390000, -380001)
Ypt = slice(-360000, -350001)

doy_b01 = b01_yr.groupby(b01_yr['TIME.dayofyear']).apply(lambda x: x).dayofyear



WA1_2016 = WA1_all.sel(TIME='2016')

# create a lookup of snow layers
#WA1_2016_O = WA1_2016.groupby(WA1_2016['TIME.dayofyear']).apply(lambda x: x).OUTLAY
WA1_2016_O = WA1_2016
# Mask to only retain values with meltwater present
WA1_2016_O = WA1_2016.where(WA1_2016 > 0)
# Mask to only retain values within measured snow depth
#ident = WA1_2016_O.where(WA1_2016 <= (sd + 0.02))
# Find the deepest location that has liquid water content
#max_water_depth = ident.max(dim='OUTLAY')
max_water_depth = WA1_2016_O.max(dim='OUTLAY')



# Look up amount of water at this location
water_content = WA1_2016.sel(OUTLAY=max_water_depth).squeeze()


#outlays = np.array([0.,0.05,0.1,0.2,0.30000001,0.40000001,0.5,0.64999998,0.80000001,1.,1.5,2.,3.,5.,7.5,10.,15.,20.])


outlays = WA1_all.OUTLAY.values
dims = WA1_all.shape
arr = np.broadcast_to(outlays, (dims[2], dims[3], dims[1]))
arr_corr = np.moveaxis(arr, 2, 0)
arr_corr_time = np.broadcast_to(arr_corr, dims)
outlay_id = xr.DataArray(arr_corr_time, coords=WA1_all.coords, dims=WA1_all.dims)

# 0.01 == 10g of liquid melt per kg of ice
WA1_O = outlay_id.where(WA1_all > 0.01)
max_water_depth = WA1_O.max(dim='OUTLAY')

fig = plt.figure()
n = 1
for year in range(2000, 2017):

	print(year)

	max_depth = max_water_depth.sel(TIME=str(year)).where(mar_mask_dark.r > 0).where(max_water_depth > 0) \
		.mean(dim=('X', 'Y'))

	ax = plt.subplot(2, 9, n)

	snow_thick = SHSN2_all.sel(TIME=str(year), SECTOR1_1=1.0).where(mar_mask_dark.r > 0).where(SHSN2_all > 0).mean(dim=('X', 'Y')).squeeze()
	snow_thick_1sd = SHSN2_all.sel(TIME=str(year), SECTOR1_1=1.0).where(mar_mask_dark.r > 0).where(SHSN2_all > 0).std(dim=('X', 'Y')).squeeze()

	ax.fill_between([pd.to_datetime(t) for t in snow_thick.TIME.values], snow_thick-snow_thick_1sd, y2=snow_thick+snow_thick_1sd)
	#ax.fill_between(snow_thick.TIME, snow_thick-snow_thick_1sd, snow_thick+snow_thick_1sd)
	ax.plot(snow_thick.TIME, snow_thick, color='white')
	max_depth.plot(ax=ax)
	

	plt.xlim('%s-04-01' % year, '%s-09-01' % year)
	plt.ylim(0, 1.5)
	plt.ylabel('')
	plt.xlabel('')
	#plt.xticks([0, 0.3, 0.6, 0.9, 1.2, 1.5])

	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('%m'))   

	plt.title(year)
	n += 1



# percentage of snow in common mask area with liquid at ice interface

# first need to identify whether liquid is at the interface (to nearest 5 cm)
identity = (max_water_depth.where(mar_mask_dark.r > 0) >= (SHSN2_all.sel(SECTOR1_1=1.0).where(mar_mask_dark.r > 0) - 0.05))

npx = np.sum(np.where(mar_mask_dark.r > 0, 1, 0))
nwet = identity.where(identity).count(dim=('X', 'Y'))

nsnowcovered = SHSN2_all.where(mar_mask_dark.r > 0.01).where(SHSN2_all > 0).count(dim=('X', 'Y'))

plt.style.use('ggplot')
fig = plt.figure()
n = 1
for year in range(2000, 2017):

	print(year)

	ax = plt.subplot(5, 4, n)

	nwet.sel(TIME=str(year)).load().rolling(TIME=7).median().plot(ax=ax)
	nsnowcovered.sel(TIME=str(year)).load().rolling(TIME=7).median().plot(ax=ax)

	plt.xlim('%s-04-01' % year, '%s-09-01' % year)
	plt.ylim(0, 200)
	plt.ylabel('')
	plt.xlabel('')
	#plt.xticks([0, 0.3, 0.6, 0.9, 1.2, 1.5])

	ax.xaxis.set_major_locator(dates.MonthLocator())
	ax.xaxis.set_major_formatter(dates.DateFormatter('%m'))   

	plt.title(year)
	n += 1