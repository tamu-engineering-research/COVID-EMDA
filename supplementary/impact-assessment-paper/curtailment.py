import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import warnings
warnings.filterwarnings("ignore")


def create_curtailment_data(web, date_range, selected_months):
    df = pd.read_csv(web, index_col='date')
    df.index = pd.to_datetime(df.index)
    df = df[df.index.isin(date_range)]

    df_new = df.resample('M').sum()
    df_new = df_new.sum(axis=1).to_frame(name='monthly_curtailment')
    df_new = df_new[df_new.index.month.isin(selected_months)]
    return df_new


def insert_blank_between_year(df):
    years = df.index.year.unique().sort_values()
    months = df.index.month.unique().sort_values()
    if months[-1] < 12:
        gap_month = months[-1] + 1
        gap_index = [pd.datetime(yr, gap_month, 1) for yr in years[:-1]]
        new_index = df.index.append(pd.Index(gap_index))
        df = df.reindex(new_index).sort_index()
    return df


def plot_monthly_curtailment(df):
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_axes([0.12, 0.15, 0.85, 0.8])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    magnitude = int(np.log10(df.max()))
    ax.set_ylabel('Monthly Curtailment (x$10^' + np.str(magnitude) + '$MW)')
    df = df / (10 ** magnitude)
    df = insert_blank_between_year(df)

    df_prev = df[df.index.year < 2020]
    df_2020 = df[df.index.year == 2020]
    ax.bar(x=df_prev.index.strftime('%Y-%b'), height=df_prev['monthly_curtailment'].values, width=0.65,
           color='grey', alpha=0.6)
    ax.bar(x=df_2020.index.strftime('%Y-%b'), height=df_2020['monthly_curtailment'].values, width=0.65,
           color='C0', alpha=0.75)

    axis_index = ['2017-Feb', '2017-Jun', '2018-Feb', '2018-Jun', '2019-Feb', '2019-Jun', '2020-Feb', '2020-Jun']
    plt.xticks(axis_index, axis_index, rotation=40, ha='right')
    ax.tick_params(axis='x', length=0)  # hide ticks marks
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.show()


if __name__ == '__main__':
    market = 'spp'
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_curtailment = web_root + 'supplementary/impact-assessment-paper/support/' + market + '_rto_curtailment.csv'
    df = create_curtailment_data(
        web=web_curtailment,
        date_range=pd.date_range('2017-01-01', '2020-06-30'),
        selected_months=[2, 3, 4, 5, 6],
    )
    plot_monthly_curtailment(df)
