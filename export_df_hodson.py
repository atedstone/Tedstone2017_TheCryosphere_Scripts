from prep_env_vars import *

mod10 = xr.open_mfdataset('/scratch/MOD10A1.006.SW/*.nc', chunks={'TIME':366})

tot_px = mask_dark.where(mask_dark > 0).count(dim=('X', 'Y'))
cloudy = mod10.Snow_Albedo_Daily_Tile \
	.where(mod10.Snow_Albedo_Daily_Tile == 150) \
	.where(mask_dark > 0) \
	.count(dim=('X', 'Y'))
daily_perc_cloudy = (100 / tot_px) * cloudy

al = mod10.Snow_Albedo_Daily_Tile \
	.where(mask_dark > 0) \
	.where(mod10.Snow_Albedo_Daily_Tile <= 100) \
	.where(daily_perc_cloudy <= 50) \
	.mean(dim=('X', 'Y')) \
	.to_pandas()

b01_avg = read_data(store_path + 'B01_avg_clouds50_daily.csv', 'B01_avg')
shf_abs = read_data(store_path + 'SHF_abs.csv', 'SHF')
sw_abs = read_data(store_path + 'SW_abs.csv', 'SW')
lw_abs = read_data(store_path + 'LW_abs.csv', 'LW')

df = pd.concat((b01_avg, shf_abs, sw_abs, lw_abs, al), axis=1)
df.to_csv(store_path + 'b01_shf_lw_sw.csv')
