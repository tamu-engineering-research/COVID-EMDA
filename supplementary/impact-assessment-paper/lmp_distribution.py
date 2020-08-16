import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_lmp_distribution_date(web, date_range, months):
    df = pd.read_csv(web, index_col='date')
    df.index = pd.to_datetime(df.index)
    df = df[df.index.isin(date_range)]
    df = df[df.index.month.isin(months)]
    return df


def plot_lmp_distribution(df, year, xlim=None, ylim=None):
    array_sel = df[df.index.year == year].values.flatten()
    xlim = xlim if xlim is not None else [array_sel.min(), array_sel.max()]

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_axes([0.12, 0.22, 0.85, 0.75])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Occurence Frequency')
    ax.set_xlabel('Day-Ahead Locational Marginal Price ($/MW)')
    color_mapping = {2017: '#f2d0a2', 2018: '#f8ad96', 2019: '#d9819a', 2020: '#ac6297'}

    freq, _, _ = ax.hist(
        array_sel, bins=np.linspace(xlim[0], xlim[1], 50), density=True, color=color_mapping[year], label=np.str(year))
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    plt.legend(framealpha=0)
    plt.show()

    print('In %d, Average LMP = %.2f, Highest Frequency = %.3f'
          % (year, array_sel.mean(), freq.max()))


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_target = web_root + 'data_release/isone/isone_rto_lmp.csv'

    df = create_lmp_distribution_date(
        web=web_target,
        date_range=pd.date_range('2017-01-01', '2020-07-15'),
        months=[3, 4, 5, 6, 7],
    )
    for year in [2017, 2018, 2019, 2020]:
        plot_lmp_distribution(df, year, xlim=[0, 70], ylim=[0, 0.14])
