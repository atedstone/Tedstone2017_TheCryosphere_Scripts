nao = pd.read_csv('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/data/norm.nao.monthly.b5001.current.ascii',
	parse_dates={'date':[0, 1]}, index_col='date', header=None, delim_whitespace=True)
nao = nao.squeeze()

nao_JJA_all = nao.where((nao.index.month >= 6) & (nao.index.month < 9)) \
	.resample('1AS').mean()
nao_JJA = nao_JJA_all['2000':'2016']

nao_JJA.to_csv(store_path + 'NAO_JJA_mean.csv')