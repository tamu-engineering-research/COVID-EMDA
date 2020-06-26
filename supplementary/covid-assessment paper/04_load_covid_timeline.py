import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def plot_load_reduction_timeline(web, date_range, time_label=None):
    df = pd.read_csv(web, index_col='date')
    df.index = pd.to_datetime(df.index)
    df = df[df.index.isin(date_range)]
    df_redu = df['q_0.50']
    df_ma = df_redu.rolling(window=7).mean()

    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(10, 4.5))
    ax = fig.add_axes([0.08, 0.22, 0.9, 0.77])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Reduction Rate of Electricity Consumption')
    ax.set_xlabel('Date')

    ax.plot(df_redu.index, df_redu, label='Hourly Reduction Rate', c='grey', alpha=0.3)
    ax.plot(df_redu.index, df_ma, c='C0', lw=3, marker='o', ms=4, label='Weekly Reduction Rate Trend')
    if time_label is not None:
        for d in time_label:
            ax.axvline(x=d, color='#773456', linestyle='--', linewidth=2)

    plt.xticks(df_redu.index[::3], df_redu.index[::3].strftime('%b-%d'), rotation=40)
    fig.legend(framealpha=0)
    plt.show()


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_target = 'supplementary/covid-assessment%20paper/data_support/nyiso_rto_reduction_result.csv'
    covid_label = [
        pd.datetime(2020, 3, 1),   # first case
        pd.datetime(2020, 3, 7),   # state of emergency
        pd.datetime(2020, 3, 27),  # US has most cases, confirmed cases exceed 50 million
        pd.datetime(2020, 4, 3),   # confirmed cases exceed 100 million
        pd.datetime(2020, 4, 10),  # most confirmed cases in US
    ]

    plot_load_reduction_timeline(
        web=web_root + web_target,
        date_range=pd.date_range(pd.datetime(2020, 2, 1), pd.datetime(2020, 5, 12)),
        time_label=covid_label,
    )

