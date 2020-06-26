import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_duck_curve_data(web_genmix, web_load, months):
    df_genmix = pd.read_csv(web_genmix, index_col='date')
    df_genmix.index = pd.to_datetime(df_genmix.index)
    df_solar = df_genmix[df_genmix['fuel'] == 'solar'].drop(columns='fuel')
    df_load = pd.read_csv(web_load, index_col='date')
    df_load.index = pd.to_datetime(df_load.index)
    df_duck_curve = df_load - df_solar
    df_duck_curve = df_duck_curve[df_duck_curve.index.month.isin(months)]
    return df_duck_curve


def plot_duck_curve(df, year, ylim=None):
    df_sel = df[df.index.year == year]
    df_q = df_sel.quantile([0.1, 0.25, 0.5, 0.75, 0.9])

    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(3, 3.5))
    ax = fig.add_axes([0.18, 0.22, 0.85, 0.75])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Residual Electricity Consumption (MW)')
    ax.set_xlabel('Time')

    ax.plot(df_q.loc[0.5], label='Average ', c='C0', lw=2)
    ax.fill_between(df_q.columns, df_q.loc[0.1], df_q.loc[0.9], label='Quantile1', color='C0', alpha=0.1)
    ax.fill_between(df_q.columns, df_q.loc[0.25], df_q.loc[0.75], label='Quantile2', color='C0', alpha=0.2)

    if ylim is not None:
        ax.set_ylim(ylim)
    xticks = df_q.columns[[0, 3, 6, 9, 12, 15, 18, 21, 23]]
    plt.xticks(xticks, xticks, rotation=40)
    fig.legend(framealpha=0)
    plt.show()


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_target_genmix = 'data_release/caiso/caiso_rto_genmix.csv'
    web_target_load = 'data_release/caiso/caiso_rto_load.csv'

    df = create_duck_curve_data(
        web_genmix=web_root + web_target_genmix,
        web_load=web_root + web_target_load,
        months=[3, 4, 5],
    )
    for year in [2018, 2019, 2020]:
        plot_duck_curve(df, year, ylim=[9000, 27500])

