import numpy as np
import pandas as pd
import json


def parse_caiso_load(area, file):
    print(':: Start handling %s ...' % file)
    assert area in ['rto', 'la'], '>> WARNING: Unexpected area keyword!'
    if area == 'rto' and 'ENE_SLRS_DAM' in file:
        return _parse_caiso_load_rto(file)
    if area == 'la' and 'Demand_for_Los_Angeles' in file:
        return _parse_ca_load_la(file)
    print('>> WARNING: Dismatch area keyword & file name! Please double check!')


def _parse_caiso_load_rto(file):
    df = pd.read_csv(file, index_col='INTERVALSTARTTIME_GMT')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.index = df.index.tz_localize('GMT').tz_convert('America/Los_Angeles')
    dfsel = df[df['TAC_ZONE_NAME'] == 'Caiso_Totals']
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'load': dfsel['MW'],
    })


def _parse_ca_load_la(file, after_date=pd.datetime(2017, 1, 1)):
    with open(file) as fn:
        dict = json.load(fn)
    df = pd.DataFrame(dict['series'][0]['data'])
    df.columns = ['date_time', 'load']
    df.index = pd.to_datetime(df['date_time'])
    df.index = df.index.tz_localize('GMT').tz_convert('America/Los_Angeles')
    if after_date is not None:
        df = df.loc[df.index.date >= after_date.date()]
    return pd.DataFrame({
        'date': df.index.date,
        'time': df.index.strftime('%H:%M'),
        'load': df['load'],
    })


def parse_miso_load(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_excel(file, skiprows=[0, 1, 2, 3, 5], skipfooter=27)
    area_mapping = {
        'rto':      'MISO ActualLoad (MWh)',
        'chicago':  'LRZ4 ActualLoad (MWh)',
        'north':    ['LRZ1 ActualLoad (MWh)', 'LRZ2_7 ActualLoad (MWh)'],
        'central':  ['LRZ3_5 ActualLoad (MWh)', 'LRZ4 ActualLoad (MWh)', 'LRZ6 ActualLoad (MWh)'],
        'south':    'LRZ8_9_10 ActualLoad (MWh)',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[area_mapping[area]]
    if len(dfsel.shape) > 1:
        dfsel = dfsel.sum(axis=1)
    return pd.DataFrame({
        'date': pd.to_datetime(df['Market Day']).dt.date,
        'time': (df['HourEnding'] - 1).astype(str).str.zfill(2) + ':00',
        'load': dfsel.values,
    })


def parse_isone_load(area, file):
    print(':: Start handling %s ...' % file)
    assert area in ['rto', 'boston'], '>> WARNING: Unexpected area keyword!'
    if area == 'rto' and 'rt_hourlysysload' in file:
        return _parse_isone_load_rto(file)
    if area == 'boston' and 'OI_darthrmwh_iso' in file:
        return _parse_isone_load_boston(file)
    print('>> WARNING: Dismatch area keyword & file name! Please double check!')


def _parse_isone_load_rto(file):
    df = pd.read_csv(file, skiprows=[0, 1, 2, 3, 5], skipfooter=1, engine='python').drop(columns='H')
    if df['Hour Ending'].dtype.kind not in 'iuf':  # not number
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['Hour Ending'].astype(str).apply(lambda x: x.replace('.', '').isnumeric())]  # remove records 02X
        df['Hour Ending'] = df['Hour Ending'].astype(int)
    return pd.DataFrame({
        'date': pd.to_datetime(df['Date']).dt.date,
        'time': (df['Hour Ending'] - 1).astype(str).str.zfill(2) + ':00',
        'load': df['Total Load'],
    })


def _parse_isone_load_boston(file):
    df = pd.read_csv(file, skiprows=[0, 1, 2, 3, 4, 6], skipfooter=1, engine='python')
    df.columns = ['H', 'Date', 'Hour Ending', 'Day Ahead', 'Real Time']
    df = df.drop(columns=['H', 'Day Ahead'])
    if df['Hour Ending'].dtype.kind not in 'iuf':  # not number
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['Hour Ending'].astype(str).apply(lambda x: x.replace('.', '').isnumeric())]  # remove records 02X
        df['Hour Ending'] = df['Hour Ending'].astype(int)
    return pd.DataFrame({
        'date': pd.to_datetime(df['Date']).dt.date,
        'time': (df['Hour Ending'] - 1).astype(str).str.zfill(2) + ':00',
        'load': df['Real Time'],
    }).dropna()


def parse_nyiso_load(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='Time Stamp')
    df.index = pd.to_datetime(df.index)
    assert area in ['rto', 'nyc'], '>> WARNING: Unexpected area keyword!'
    if area == 'rto':
        df.index = [df.index, df['Name']]
        df = df.loc[~df.index.duplicated()]
        dfsel = df['Integrated Load'].unstack().sum(axis=1)
    elif area == 'nyc':
        dfsel = df[df['Name'] == 'N.Y.C.'].loc[:, 'Integrated Load']
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'load': dfsel.values,
    })


def parse_pjm_load(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='datetime_beginning_ept')
    df.index = pd.to_datetime(df.index)
    area_mapping = {
        'rto':      'RTO',
        'phila':    'PE',
        'chicago':  'CE',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['load_area'] == area_mapping[area]].loc[:, 'mw']
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'load': dfsel.values,
    })


def parse_spp_load(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='MarketHour')
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize('GMT').tz_convert('America/Chicago') - pd.Timedelta(hours=1)
    area_mapping = {
        'rto':      df.columns,
        'kck':      ' KCPL',
        'north':    [' WAUE', ' NPPD', ' OPPD', ' LES', ' INDN'],
        'south':    [c for c in df.columns if c not in [' WAUE', ' NPPD', ' OPPD', ' LES', ' INDN']],
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[area_mapping[area]]
    if len(dfsel.shape) > 1:
        dfsel = dfsel.sum(axis=1)
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'load': dfsel.values,
    })


def parse_ercot_load(area, file):
    print(':: Start handling %s ...' % file)
    if 'cdr.00013101' in file:
        return _parse_ercot_load_daily_record(area, file)
    elif 'Native_Load' in file:
        return _parse_ercot_load_archive(area, file)
    print('>> WARNING: Unexpected file name!')


def _parse_ercot_load_daily_record(area, file):
    df = pd.read_csv(file, index_col='OperDay')
    df.index = pd.to_datetime(df.index)
    df['HourEnding'] = df['HourEnding'].str.replace(
        pat=r'\d\d:', repl=lambda m: np.str(int(m.group(0)[0:2]) - 1).zfill(2) + ':')  # avoid 24:00
    area_mapping = {
        'rto':      'TOTAL',
        'houston':  'COAST',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    return pd.DataFrame({
            'date': df.index.date,
            'time': df['HourEnding'],
            'load': df[area_mapping[area]].values,
        })


def _parse_ercot_load_archive(area, file):
    df = pd.read_excel(file, index_col=0)  # 'Hour Ending' or 'HourEnding'
    df.index = df.index.astype(str).str.replace(
        pat=r'\d\d:', repl=lambda m: np.str(int(m.group(0)[0:2]) - 1).zfill(2) + ':')  # avoid 24:00
    df.index = df.index.astype(str).str.replace('DST', '')
    df.index = pd.to_datetime(df.index)
    area_mapping = {
        'rto':      'ERCOT',
        'houston':  'COAST',
    }
    return pd.DataFrame({
        'date': df.index.date,
        'time': df.index.strftime('%H:%M'),
        'load': df[area_mapping[area]].values,
    })


