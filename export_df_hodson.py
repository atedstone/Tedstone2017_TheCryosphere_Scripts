from prep_env_vars import *

b01_avg = read_data(store_path + 'B01_avg_clouds50_daily.csv', 'B01_avg')
shf_abs = read_data(store_path + 'SHF_abs.csv', 'SHF')
sw_abs = read_data(store_path + 'SW_abs.csv', 'SW')
lw_abs = read_data(store_path + 'LW_abs.csv', 'LW')

df = pd.concat((b01_avg, shf_abs, sw_abs, lw_abs), axis=1)
df.to_csv(store_path + 'b01_shf_lw_sw.csv')
