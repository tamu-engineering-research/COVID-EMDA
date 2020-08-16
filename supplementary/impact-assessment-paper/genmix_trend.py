import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_monthly_average_genmix_data(web, date_range):
    df = pd.read_csv(web, index_col='date')
    df.index = pd.to_datetime(df.index)
    df = df[df.index.isin(date_range)]

    all_kinds = df['fuel'].unique()
    dict_kind = {k: df[df['fuel'] == k].drop(columns='fuel').resample('M').mean().sum(axis=1) for k in all_kinds}
    df_kind = pd.DataFrame(dict_kind)
    return df_kind


def plot_genmix_trend(df):
    all_kinds = df.columns
    plot_data = [df[k] / df.sum(axis=1) for k in all_kinds]

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_axes([0.12, 0.22, 0.85, 0.75])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Generation Proportion (%)')
    ax.set_xlabel('Month')
    color_mapping = {
        'coal':    '#a67a6d',
        'gas':     '#f69850',
        'oil':     '#b35711',
        'nuclear': '#3f9b98',
        'hydro':   '#a0d8f1',
        'wind':    '#73c698',
        'solar':   '#ffbd4a',
        'other':   '#b4b4b4',
        'import':  'white',
    }

    plt.stackplot(df.index, plot_data, labels=all_kinds, colors=[color_mapping[k] for k in all_kinds])
    plt.xticks(df.index[::3], df.index[::3].strftime('%Y-%b'), rotation=40, ha='right')
    yticks = np.array([20, 40, 60, 80, 100])
    plt.yticks(yticks / 100, yticks)
    plt.legend(framealpha=0)
    plt.show()


if __name__ == '__main__':
    market = 'spp'
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_genmix = web_root + 'data_release/' + market + '/' + market + '_rto_genmix.csv'

    df = create_monthly_average_genmix_data(
        web=web_genmix,
        date_range=pd.date_range(pd.datetime(2017, 1, 1), pd.datetime(2020, 7, 15)),
    )
    print(df.head())
    plot_genmix_trend(df)
