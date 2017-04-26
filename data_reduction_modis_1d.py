# Dark ice metrics

from prep_env_vars import *

mod10 = xr.open_mfdataset('/scratch/MOD10A1.006.SW/*.nc', chunks={'TIME':366})

b01 = ds_refl.sur_refl_b01_1.where(mask_dark > 0)
b02 = ds_refl.sur_refl_b02_1.where(mask_dark > 0)
al = mod10.Snow_Albedo_Daily_Tile.where(mask_dark > 0)

tot_px = mask_dark.where(mask_dark > 0).count(dim=('X', 'Y'))
cloudy = al.where(al == 150).where(mask_dark > 0).count(dim=('X', 'Y'))
daily_perc_cloudy = (100 / tot_px) * cloudy
daily_perc_cloudy.to_pandas().to_csv(store_path + 'cloudy_commonarea_perc_daily.csv')

ice = b02.where(b02 < 0.6).where(mask_dark > 0).count(dim=('X', 'Y'))

b01_avg = b01.where(al <= 100).where(mask_dark > 0).mean(dim=('X', 'Y'))
b01_avg.to_pandas().to_csv(store_path + 'B01_avg_incl_clouds_daily.csv')
b01_avg = b01_avg.where(daily_perc_cloudy <= 50)
b01_avg.to_pandas().to_csv(store_path + 'B01_avg_clouds50_daily.csv')



# Dark ice percentage is...
# Copied from plot_annual_duration_basemap.py - make sure they stay the same!
as_perc = (100. / ((243-152)-onset.bad_dur)) * onset.dark_dur
toplot = as_perc \
	.sel(TIME=slice('2000','2016')) \
	.where(onset.dark_dur > 5) \
	.where(mask_dark == 1)


B01_avg_bare = b01_avg.where(modis_periods_bare2end) \
	.resample('1AS', dim='TIME', how='mean').to_pandas()
B01_avg_bare.to_csv(store_path + 'B01_avg_bareice_JJA.csv')

dark_perc = toplot.median(dim=('X', 'Y')).to_pandas()
dark_perc.to_csv(store_path + 'B01_JJA_darkperc.csv')

B01_avg = b01_avg.where(b01_avg['TIME.season'] == 'JJA').resample('1AS', dim='TIME', how='mean').to_pandas()
B01_avg.to_csv(store_path + 'B01_avg_JJA.csv')

dark_norm = dark_perc / (B01_avg * 100)
dark_norm.to_csv(store_path + 'dark_norm_JJA.csv')

dark_norm_bare = dark_perc / (B01_avg_bare * 100)
dark_norm_bare.to_csv(store_path + 'dark_norm_bare_JJA.csv')