import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def create_forecast_accuracy_data(web_forecast, web_real, date_range):
    df_forecast = pd.read_csv(web_forecast, index_col='date')
    df_forecast.index = pd.to_datetime(df_forecast.index)
    df_real = pd.read_csv(web_real, index_col='date')
    df_real.index = pd.to_datetime(df_real.index)
    df_accuracy = (df_forecast / df_real - 1).dropna()
    df_accuracy = df_accuracy[df_accuracy.index.isin(date_range)]
    df_month_accuracy = df_accuracy.abs().resample('M').mean().mean(axis=1)
    return df_month_accuracy


def get_month_percentage(df, year, month):
    data = df[(df.index.year == year) & (df.index.month == month)]
    output = np.round(100 * data, decimals=1).astype(str).values[0]
    return output


def create_forecast_accuracy_table(webs, date_range):
    dict = {}
    for market, (web_forecast, web_real) in webs.items():
        df = create_forecast_accuracy_data(web_forecast, web_real, date_range)
        dict[market] = pd.Series(data=[
            get_month_percentage(df, 2020, 3) + ' (' + get_month_percentage(df, 2019, 3) + ')',
            get_month_percentage(df, 2020, 4) + ' (' + get_month_percentage(df, 2019, 4) + ')',
            get_month_percentage(df, 2020, 5) + ' (' + get_month_percentage(df, 2019, 5) + ')',
            get_month_percentage(df, 2020, 6) + ' (' + get_month_percentage(df, 2019, 6) + ')',
            get_month_percentage(df, 2020, 7) + ' (' + get_month_percentage(df, 2019, 7) + ')',
        ], index=['March', 'April', 'May', 'June', 'July'])
    output = pd.DataFrame(dict).T
    return output


if __name__ == '__main__':
    web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
    webs = {
        market: (
            web_root + 'supplementary/impact-assessment-paper/support/' + market + '_rto_load_forecast.csv',
            web_root + 'data_release/' + market + '/' + market + '_rto_load.csv'
        )
        for market in ['caiso', 'miso', 'isone', 'nyiso', 'pjm', 'spp', 'ercot']
    }
    df = create_forecast_accuracy_table(webs, pd.date_range('2019-03-01', '2020-07-15'))
    print(df)
