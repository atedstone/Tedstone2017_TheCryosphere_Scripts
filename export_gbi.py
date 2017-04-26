import pandas as pd

fname = '/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/data/GBI_monthly_and_seasonal_data_1851to2017jan_for_distribution_5feb2017EH.xlsx'
data = pd.read_excel(fname, sheetname='GBI_monthly_seasonal_data', index_col='Year', parse_cols=12)

stacked = data.stack()
new_ix = pd.date_range('1851-01-01', '2017-01-01', freq='MS')
stacked.index = new_ix

gbi_nao = stacked.where((stacked.index.month >= 6) & (stacked.index.month < 9)) \
	.resample('1AS').mean()

gbi_nao = gbi_nao['2000':'2016']	

gbi_nao.to_csv(store_path + 'GBI_JJA_mean.csv')

