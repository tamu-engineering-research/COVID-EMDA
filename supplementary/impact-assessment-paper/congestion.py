import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_congestion_data(web_congestion, web_total_lmp, months):
    df_congestion = pd.read_csv(web_congestion, index_col='date')
    df_congestion.index = pd.to_datetime(df_congestion.index)
    df_lmp = pd.read_csv(web_total_lmp, index_col='date')
    df_lmp.index = pd.to_datetime(df_lmp.index)

    df_monthly_congestion = df_congestion.abs().resample('M').sum().sum(axis=1)
    df_monthly_congestion = df_monthly_congestion[df_monthly_congestion.index.month.isin(months)]
    df_monthly_lmp = df_lmp.abs().resample('M').sum().sum(axis=1)
    df_monthly_lmp = df_monthly_lmp[df_monthly_lmp.index.month.isin(months)]
    df_rate = df_monthly_congestion.divide(df_monthly_lmp)
    return df_monthly_congestion, df_rate


def slice_data(df):
    df = df[(df.index.year == 2019) | (df.index.year == 2020)]
    df = df[df.index.month.isin([3, 4, 5, 6])]
    return df


def insert_blank_between_year(df):
    years = df.index.year.unique().sort_values()
    months = df.index.month.unique().sort_values()
    if months[-1] < 12:
        gap_month = months[-1] + 1
        gap_index = [pd.datetime(yr, gap_month, 1) for yr in years[:-1]]
        new_index = df.index.append(pd.Index(gap_index))
        df = df.reindex(new_index).sort_index()
    return df


def plot_monthly_congestion(df_congestion, df_rate):
    df_congestion = insert_blank_between_year(slice_data(df_congestion))
    df_rate = insert_blank_between_year(slice_data(100 * df_rate))

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_axes([0.11, 0.2, 0.79, 0.75])
    ax2 = ax.twinx()
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.set_ylabel('Monthly Congestion Cost ($/MWh)')
    ax2.set_ylabel('Proportion of Total Cost (%)')

    axis_index = df_congestion.index.strftime('%Y-%b')
    ax.bar(x=axis_index, height=df_congestion.values, width=0.5,
           label='Monthly Congestion Cost', zorder=10, color='C0', alpha=0.75)
    ax2.plot(axis_index, df_rate, label='Proportion of Total Cost', zorder=20,
             c='C5', marker='o')

    ax.xaxis.set_tick_params(rotation=45)
    plt.xticks(axis_index.drop('2019-Jul'), axis_index.drop('2019-Jul'))  # ignore blank ticks
    ax.tick_params(axis='x', length=0)  # hide ticks marks
    ax.legend(framealpha=0, loc=1)
    ax2.legend(framealpha=0, loc=2)
    plt.show()


if __name__ == '__main__':
    market = 'isone'
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_congestion = web_root + 'supplementary/impact-assessment-paper/support/' + market + '_rto_congestion_lmp.csv'
    web_total_lmp = web_root + 'data_release/' + market + '/' + market + '_rto_lmp.csv'

    df_congestion, df_rate = create_congestion_data(
        web_congestion=web_congestion,
        web_total_lmp=web_total_lmp,
        months=[3, 4, 5, 6, 7],
    )
    plot_monthly_congestion(df_congestion, df_rate)

