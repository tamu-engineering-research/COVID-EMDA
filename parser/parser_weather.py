import numpy as np
import pandas as pd


station_mapping = {
    ('caiso', 'rto'):       ['SFO', 'BUR', 'FAT'],
    ('caiso', 'la'):        ['CQT'],
    ('miso', 'rto'):        ['MSP', 'OZW', 'SPI', 'DSM', 'LIT', 'BTR'],
    ('miso', 'north'):      ['MSP', 'OZW'],
    ('miso', 'central'):    ['SPI', 'DSM'],
    ('miso', 'south'):      ['LIT', 'BTR'],
    ('isone', 'rto'):       ['BOS', 'HIE'],
    ('isone', 'boston'):    ['BOS'],
    ('nyiso', 'rto'):       ['LGA', 'SYR'],
    ('nyiso', 'nyc'):       ['LGA'],
    ('pjm', 'rto'):         ['PHL', 'CMH', 'RIC'],
    ('pjm', 'phila'):       ['PHL'],
    ('pjm', 'chicago'):     ['MDW'],
    ('spp', 'rto'):         ['OMA', 'ATY', 'OJC', 'OKC'],
    ('spp', 'kck'):         ['OJC'],
    ('spp', 'north'):       ['OMA', 'ATY'],
    ('spp', 'south'):       ['OJC', 'OKC'],
    ('ercot', 'rto'):       ['HOU', 'CVB', 'DAL'],
    ('ercot', 'houston'):   ['HOU'],
}


def parse_asos_weather(market, area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file)
    df['valid'] = pd.to_datetime(df['valid'])
    station_list = station_mapping[(market, area)]
    df = df[df['station'].isin(station_list)].set_index(['valid', 'station'])
    down_sample_list = []
    for col in df.columns:
        obs = df[col]
        obs = obs.loc[~obs.index.duplicated()]
        obs = obs[obs.astype(str) != 'M'].astype(np.float)
        obs_ds = obs.resample(rule='H', level=0).mean()
        obs_new = obs_ds.interpolate(method='linear', limit_direction='both')
        down_sample_list.append(obs_new)
    df_new = pd.concat(down_sample_list, axis=1).dropna()
    df_new.columns = df.columns
    df_new.columns.name = 'kind'
    df_new = df_new.stack().rename('value').reset_index()
    return pd.DataFrame({
        'date':     df_new['valid'].dt.date,
        'time':     df_new['valid'].dt.strftime('%H:%M'),
        'kind':     df_new['kind'],
        'value':    df_new['value'],
    })

