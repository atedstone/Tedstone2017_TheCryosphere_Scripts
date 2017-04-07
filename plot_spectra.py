from matplotlib import rcParams
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

store_path = '/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/data/'

plt.style.use('default')
rcParams['font.size'] = 6
rcParams['font.sans-serif'] = 'Arial'
rcParams['axes.labelsize'] = 6 # sets colorbar label size
rcParams['legend.fontsize'] = 6
rcParams['xtick.labelsize'] = 6
rcParams['ytick.labelsize'] = 6
rcParams['xtick.major.pad'] = 3
rcParams['figure.titlesize'] = 6
rcParams['axes.unicode_minus'] = False

data = pd.read_excel(store_path + 'Spectra for AT.xlsx', index_col='wl')

plt.figure(figsize=(3.5, 3))
ax = plt.subplot(1, 1, 1)

plt.fill_between(data.index, data['clean_min'], data['clean_max'], 
	facecolor='#6BAED6', edgecolor='none', zorder=2, alpha=0.4)
plt.plot(data.index, data['clean_mean'], color='#08519C')
plt.annotate('White ice', fontsize=6, xy=(400,0.7), xycoords='data',
           horizontalalignment='left', verticalalignment='top', zorder=10, color='#08519C')

plt.fill_between(data.index, data['medium_min'], data['medium_max'], 
	facecolor='#FEE391', edgecolor='none', zorder=2, alpha=0.4)
plt.plot(data.index, data['medium_mean'], color='#CC4C02')
plt.annotate('Light algae', fontsize=6, xy=(400,0.41), xycoords='data',
           horizontalalignment='left', verticalalignment='top', zorder=10, color='#CC4C02')

plt.fill_between(data.index, data['heavy_min'], data['heavy_max'], 
	facecolor='#FCBBA1', edgecolor='none', zorder=2, alpha=0.4)
plt.plot(data.index, data['heavy_mean'], color='#CB181D')
plt.annotate('Heavy algae', fontsize=6, xy=(400,0.11), xycoords='data',
           horizontalalignment='left', verticalalignment='top', zorder=10, color='#CB181D')


plt.axvspan(841, 876, facecolor='#cccccc', edgecolor='#cccccc', zorder=1)
plt.plot([841, 876], [0.6, 0.6], color='white', zorder=5)

plt.axvspan(620, 670, facecolor='#FBB4AE', edgecolor='#FBB4AE', zorder=1)
plt.plot([620, 670], [0.45, 0.45], color='white', zorder=5) ##CB181D


plt.xlim(350, 1000)

plt.xlabel('Wavelength (nm)')
plt.ylabel('Reflectance')
plt.ylim(0, 1)

ax.tick_params(axis='y', direction='out', right='off')
ax.tick_params(axis='x', direction='out', top='off')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_darkice/submission1/figures/suppl_spectra.pdf', dpi=300)

