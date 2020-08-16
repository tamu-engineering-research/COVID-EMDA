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

    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(10, 4.5))
    ax = fig.add_axes([0.06, 0.22, 0.98, 0.75])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Reduction Rate of Electricity Consumption (%)')
    df_redu = df_redu * 100
    df_ma = df_ma * 100

    ax.plot(df_redu.index, df_redu, label='Daily Reduction Rate', c='grey', alpha=0.3)
    ax.plot(df_redu.index, df_ma, c='C0', lw=3, marker='o', ms=4, label='Weekly Reduction Rate Trend')
    if time_label is not None:
        for d in time_label:
            ax.axvline(x=d, color='#773456', linestyle='--', linewidth=2)

    plt.xticks(df_redu.index[::6], df_redu.index[::6].strftime('%b-%d'), rotation=40, ha='right')
    fig.legend(framealpha=0)
    plt.show()


if __name__ == '__main__':
    # 01. NYISO
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_caiso = web_root + 'supplementary/impact-assessment-paper/support/nyiso_rto_load_backcast_pct.csv'
    covid_label = [
        pd.datetime(2020, 3, 1),   # first case
        pd.datetime(2020, 3, 7),   # state of emergency
        pd.datetime(2020, 3, 27),  # US has most cases, confirmed cases exceed 50 million
        pd.datetime(2020, 4, 3),   # confirmed cases exceed 100 thousand
        pd.datetime(2020, 4, 13),  # confirmed cases exceed 200 thousand
        pd.datetime(2020, 4, 29),  # confirmed cases exceed 300 thousand
        pd.datetime(2020, 6, 8),   # New York City region partially reopened with Phase 1
    ]

    plot_load_reduction_timeline(
        web=web_caiso,
        date_range=pd.date_range('2020-02-01', '2020-06-30'),
        time_label=covid_label,
    )

    # 02. Results for All Markets
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    webs = {
        market: web_root + 'supplementary/impact-assessment-paper/support/' + market + '_rto_load_backcast_pct.csv'
        for market in ['caiso', 'miso', 'isone', 'nyiso', 'pjm', 'spp', 'ercot']
    }
    for market, web in webs.items():
        print(market)
        plot_load_reduction_timeline(
            web=web,
            date_range=pd.date_range('2020-02-01', '2020-06-30'),
            time_label=[],
        )

