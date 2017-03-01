""" 

Examine snow characteristics - melt rate, timing of disappearance, presence
of liquid meltwater in snowpack.

"""

from prep_env_vars import *


## Load datasets

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




WA1_all.sel(TIME='2016').sel(OUTLAY=SHSN2_all.sel(TIME='2016', SECTOR1_1=1.0), method='nearest')


# is it a reducer function?

Xpt = slice(-390000, -380001)
Ypt = slice(-360000, -350001)