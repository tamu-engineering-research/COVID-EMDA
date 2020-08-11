import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import warnings
warnings.filterwarnings("ignore")


def create_outage_data(web_outage, months):
    df_outage = pd.read_csv(web_outage, index_col='date')
    df_outage.index = pd.to_datetime(df_outage.index)
    df_outage = df_outage[df_outage.index.isin(pd.date_range('2000-01-01', '2020-07-15'))]
    df_outage = df_outage.abs().resample('M').sum().sum(axis=1)
    df_outage = df_outage[df_outage.index.month.isin(months)]
    return df_outage


def plot_monthly_outage(df):
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['font.family'] = 'Arial'
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_axes([0.15, 0.1, 0.8, 0.85])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    magnitude = int(np.log10(df.max()))
    ax.set_ylabel('Monthly Forced Outage (x$10^' + np.str(magnitude) + '$MW)')
    df = df / (10 ** magnitude)

    xpos = np.array([2, 3, 4, 5, 6])
    xticks = ['Feb', 'Mar', 'Apr', 'May', 'Jun']
    bar_width = 0.2
    pos_delta_mapping = {2018: -bar_width - 0.05, 2019: 0, 2020: bar_width + 0.05}
    color_mapping = {2018: 'grey', 2019: 'peru', 2020: 'C0'}
    for yr in [2018, 2019, 2020]:
        df_sel = df[df.index.year == yr]
        ax.bar(x=xpos + pos_delta_mapping[yr], height=df_sel.values, width=bar_width,
               label=np.str(yr), color=color_mapping[yr], alpha=0.75)

    plt.xticks(xpos, xticks)
    ax.tick_params(axis='x', length=0)  # hide ticks marks
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.legend(framealpha=0)
    plt.show()


if __name__ == '__main__':
    market = 'pjm'
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    web_outage = web_root + 'supplementary/impact-assessment-paper/support/' + market + '_rto_outage.csv'
    df = create_outage_data(web_outage, months=[2, 3, 4, 5, 6])
    plot_monthly_outage(df)
