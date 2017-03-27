"""

Currently: copy/paste into IPython terminal in which you have excecuted
%run ~/scripts/paper_darkice_repo/prep_env_vars.py
first.

"""

from prep_env_vars import *
import plotmap
import pyproj

rcParams['font.sans-serif'] = 'Arial'
rcParams['axes.unicode_minus'] = False
rcParams['legend.fontsize'] = 6
rcParams['xtick.labelsize'] = 6
rcParams['xtick.direction'] = 'in'
rcParams['xtick.major.pad'] = 3
rcParams['figure.titlesize'] = 6

# June=152
# Also in date_reduction_modis_1d.py - make sure identical in both places!
as_perc = (100. / ((243-152)-onset.bad_dur)) * onset.dark_dur
toplot = as_perc \
	.sel(TIME=slice('2000','2016')) \
	.where(onset.dark_dur > 5) \
	.where(mask_dark == 1)

years = np.arange(2000, 2017)
n = 0

fig_extent = (-52, -48, 65, 70)
lon_0 = -40
ocean_kws = dict(fc='#C6DBEF', ec='none', alpha=1, zorder=199)
land_kws = dict(fc='#F6E8C3', ec='none', alpha=1, zorder=200)
ice_kws = dict(fc='white', ec='none', alpha=1, zorder=201)

# Load in land and ice dataframes, just once
shps_loader = plotmap.Map(extent=fig_extent, lon_0=lon_0)
df_ocean = shps_loader.load_polygons(shp_file='/scratch/L0data/NaturalEarth/ne_50m_ocean/ne_50m_ocean', 
	label='ocean')
df_land = shps_loader.load_polygons(shp_file='/scratch/L0data/NaturalEarth/ne_50m_land/ne_50m_land', 
	label='land')
df_ice = shps_loader.load_polygons(shp_file='/scratch/L0data/NaturalEarth/ne_50m_glaciated_areas/ne_50m_glaciated_areas', 
	label='ice')

epsg3413 = mar_raster.proj('10km')
data_ll_geo = epsg3413(as_perc.X.min(), as_perc.Y.min(), inverse=True)
data_ur_geo = epsg3413(as_perc.X.max(), as_perc.Y.max(), inverse=True)
data_ll = shps_loader.map(data_ll_geo[0], data_ll_geo[1])
data_ur = shps_loader.map(data_ur_geo[0], data_ur_geo[1])
data_extent = (data_ll[0], data_ur[0], data_ll[1], data_ur[1])

shps_loader = None
plt.close()

def facet(fig, ax, data, title_label, label_grid, imshow_kws):

	facet_map = plotmap.Map(extent=fig_extent, lon_0=lon_0, fig=fig, ax=ax)

	# Draw basic underlays
	#facet_map.plot_polygons(df=df_ocean, plot_kws=ocean_kws)
	facet_map.plot_polygons(df=df_land, plot_kws=land_kws)
	facet_map.plot_polygons(df=df_ice, plot_kws=ice_kws)
	facet_map.map.drawmapboundary(fill_color='#C6DBEF', linewidth=0)

	# Data
	facet_map.im = facet_map.ax.imshow(data, extent=data_extent, zorder=300, **imshow_kws)

	# Facet title
	facet_map.ax.annotate(title_label,fontsize=6, fontweight='bold', xy=(0.5, 1.10), xycoords='axes fraction',
           horizontalalignment='center', verticalalignment='top',zorder=300)
	
	# Ticks/graticules
	if label_grid:
		facet_map.geo_ticks(3, 2, rotate_parallels=True, linewidth=0.5, 
			color='#737373', fontsize=6)
	else:
		facet_map.geo_ticks(3, 2, rotate_parallels=True, linewidth=0.5, 
			color='#737373',
			mlabels=[0,0,0,0], plabels=[0,0,0,0])
	
	for axis in ['top','bottom','left','right']:
		facet_map.ax.spines[axis].set_linewidth(0)

	return facet_map



# Construct facet plot, subplot-by-subplot
fig = plt.figure(figsize=(5.5, 3))
n = 1
imshow_kws = dict(cmap='Reds', vmin=0, vmax=100, interpolation='none')
for year in toplot:

	ax = plt.subplot(2, 9, n)

	if n in [1,]:
		label_grid = True
	else:
		label_grid = False

	f = facet(fig, ax, np.flipud(year.values), year['TIME.year'].values, 
		label_grid, imshow_kws)

	n += 1

# Draw common area mask
ax = plt.subplot(2, 9, n)
mask_kws = dict(cmap='Blues', vmin=0, vmax=1, interpolation='none')
mask_data = np.flipud(mask_dark.values)
mask_data = np.where(mask_data == 1, 1, np.nan)
f2 = facet(fig, ax, mask_data, 'Common area', False, mask_kws)

plt.subplots_adjust(wspace=0.05, hspace=0.05, bottom=0.15)

# Add colorbar for the duration plots
cb_ax = fig.add_axes((0.25, 0.1, 0.5, 0.04))
cbar = plt.colorbar(f.im, cax=cb_ax, orientation='horizontal', 
	ticks=(0, 20, 40, 60, 80, 100), drawedges=False)
cbar.set_label('Dark % of cloud-free JJA observations', fontsize=6)
cbar.outline.set_visible(False)



# Save etc

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/dark_ice_45_JJA_fix.pdf', dpi=300)


