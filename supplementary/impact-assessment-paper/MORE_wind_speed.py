import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def cal_monthly_wind_speed(file):
    df = pd.read_csv(file, index_col=0)
    df.index = pd.to_datetime(df.index)
    df = df[df['kind'] == 'sped'].drop(columns='kind')
    output = []
    for year in [2018, 2019, 2020]:
        for month in [2, 3, 4, 5, 6]:
            tmp = df[(df.index.year == year) & (df.index.month == month)].abs().mean().mean()
            output.append(tmp)
    print(np.array(output).reshape([3, -1]))


if __name__ == '__main__':
    file = 'E:/Research/COVEM/3-Program/github/COVID-EMDA/data_release/miso/miso_rto_weather.csv'
    # file = 'E:/Research/COVEM/3-Program/github/COVID-EMDA/data_release/miso/miso_north_weather.csv'
    # file = 'E:/Research/COVEM/3-Program/github/COVID-EMDA/data_release/miso/miso_central_weather.csv'
    # file = 'E:/Research/COVEM/3-Program/github/COVID-EMDA/data_release/miso/miso_south_weather.csv'
    # file = 'E:/Research/COVEM/3-Program/github/COVID-EMDA/data_release/pjm/pjm_rto_weather.csv'
    cal_monthly_wind_speed(file)
