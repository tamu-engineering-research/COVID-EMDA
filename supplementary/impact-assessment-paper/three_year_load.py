import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import warnings
warnings.filterwarnings("ignore")


def create_3yr_load_with_week_alignment(web, date_range_for_2020):
    df = pd.read_csv(web, index_col='date')
    df.index = pd.to_datetime(df.index)
    df['week_align'] = df.index.strftime('W%W-%a')

    align = df[df.index.isin(date_range_for_2020)].loc[:, 'week_align']
    df_sel = df[df['week_align'].isin(align)]
    return df_sel


def plot_3yr_load(df):
    df_2018 = df[df.index.year == 2018].set_index('week_align').stack()
    df_2019 = df[df.index.year == 2019].set_index('week_align').stack()
    df_2020 = df[df.index.year == 2020].set_index('week_align').stack()

    reduction_rate = np.array(1 - df_2020 / df_2019)
    print('Max Reduction Rate = %.3f, Mean Reduction Rate = %.3f'
          % (np.max(reduction_rate), np.mean(reduction_rate)))

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(10, 4))
    ax = fig.add_axes([0.05, 0.2, 1.1, 0.75])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Electricity Consumption (x$10^4$MW)')
    df_2018 = df_2018 / 1e4
    df_2019 = df_2019 / 1e4
    df_2020 = df_2020 / 1e4
    color_mapping = {2018: 'grey', 2019: 'peru', 2020: 'C0'}

    index = df_2018.index.map('{0[0]}-{0[1]}'.format)
    ax.plot(index, df_2018, c=color_mapping[2018], ls=':', label='2018')
    ax.plot(index, df_2019, c=color_mapping[2019], ls='--', label='2019')
    ax.plot(index, df_2020, c=color_mapping[2020], lw=2.5, label='2020')
    plt.xticks(index[::96], index[::96].str.replace('-00:00', ''), rotation=40, ha='right')
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    plt.legend(framealpha=0)
    plt.show()


def plot_average_daily_load_profile(df, year, month, ylim=None):
    df_sel = df[(df.index.year == year) & (df.index.month == month)]
    df_q = df_sel.quantile([0.05, 0.25, 0.5, 0.75, 0.95])

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(3, 3.5))
    ax = fig.add_axes([0.18, 0.15, 0.85, 0.85])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Electricity Consumption (x$10^4$MW)')
    df_q = df_q / 1e4
    color_mapping = {2018: 'grey', 2019: 'peru', 2020: 'C0'}

    ax.plot(df_q.loc[0.5], c=color_mapping[year], lw=2, label=np.str(year) + '-' + np.str(month).zfill(2))
    ax.fill_between(df_q.columns, df_q.loc[0.05], df_q.loc[0.95], color=color_mapping[year], alpha=0.1)
    ax.fill_between(df_q.columns, df_q.loc[0.25], df_q.loc[0.75], color=color_mapping[year], alpha=0.25)
    if ylim is not None:
        plt.ylim(ylim)
    axis_index = list(df_q.columns[::3]) + list(df_q.columns[[-1]])
    plt.xticks(axis_index, axis_index, rotation=40, ha='right')
    plt.legend(framealpha=0)
    plt.show()

    cv = np.std(df_q.loc[0.5]) / np.mean(df_q.loc[0.5])
    print('CV (%d-%02d) = %.3f' % (year, month, cv))


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_target = 'data_release/nyiso/nyiso_rto_load.csv'

    # ----- 01. Plot Three Year Electricity Consumption Trend -----
    df1 = create_3yr_load_with_week_alignment(
        web=web_root + web_target,
        date_range_for_2020=pd.date_range('2020-02-01', '2020-04-30'),
    )
    df2 = create_3yr_load_with_week_alignment(
        web=web_root + web_target,
        date_range_for_2020=pd.date_range('2020-05-01', '2020-07-15'),
    )
    plot_3yr_load(df1)
    plot_3yr_load(df2)

    # ----- 02. Plot Three Year Daily Load Profile -----
    df = pd.read_csv(web_root + web_target, index_col='date')
    df.index = pd.to_datetime(df.index)
    for year in [2018, 2019, 2020]:
        for month in [2, 4, 6]:
            plot_average_daily_load_profile(df, year, month, ylim=[1.1, 2.8])  # 11000 - 28000
