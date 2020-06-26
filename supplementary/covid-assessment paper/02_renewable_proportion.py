import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_renewable_proportion_table(webs, months):
    col_renewable = ['wind', 'solar']
    dict = {}
    for mkt, web in webs.items():
        df = pd.read_csv(web, index_col='date')
        df.index = pd.to_datetime(df.index)
        df = df[df.index.month.isin(months)]

        df_renewable = df[df['fuel'].isin(col_renewable)].groupby(level=0).sum().resample('Y').mean().sum(axis=1)
        df_gensum = df.groupby(level=0).sum().resample('Y').mean().sum(axis=1)
        percent = df_renewable / df_gensum
        percent.index = percent.index.strftime('%Y')
        dict[mkt] = percent
    output = pd.DataFrame(dict).T
    return output


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    webs = {
        mkt: web_root + 'data_release/' + mkt + '/' + mkt + '_rto_genmix.csv'
        for mkt in ['caiso', 'miso', 'isone', 'nyiso', 'pjm', 'spp', 'ercot']
    }
    df = create_renewable_proportion_table(webs=webs, months=[3, 4, 5])
    print(df)
