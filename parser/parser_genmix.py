import numpy as np
import pandas as pd


def parse_caiso_genmix(file):
    print(':: Start handling %s ...' % file)
    df1 = pd.read_table(file, sep='\t+', skiprows=1, nrows=24, engine='python')
    df1 = df1.interpolate()
    df2 = pd.read_table(file, sep='\t+', skiprows=29, nrows=24, engine='python')
    df2 = df2.interpolate()

    df = pd.concat([df1, df2.drop(columns=['Hour', 'RENEWABLES'])], axis=1)
    df['date'] = pd.to_datetime(pd.read_table(file, nrows=0, usecols=[0]).columns[0])
    if df['Hour'].dtype.kind not in 'iuf':  # non-numeric
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['Hour'].apply(lambda x: x.replace('.', '').isnumeric())]
        df['Hour'] = df['Hour'].astype(int)
    df = df.set_index(['date', 'Hour'])
    df.columns.name = 'fuel'
    df = df.stack().rename('gen').reset_index()

    genmix_mapping = {
        'GEOTHERMAL': 'other',
        'BIOMASS': 'other',
        'BIOGAS': 'gas',
        'SMALL HYDRO': 'hydro',
        'WIND TOTAL': 'wind',
        'SOLAR PV': 'solar',
        'SOLAR THERMAL': 'solar',
        'NUCLEAR': 'nuclear',
        'THERMAL': 'gas',
        'IMPORTS': 'import',
        'HYDRO': 'hydro',
    }
    df['fuel'] = df['fuel'].replace(genmix_mapping.keys(), genmix_mapping.values())
    df = df.groupby(by=['date', 'Hour', 'fuel']).sum().reset_index()
    return pd.DataFrame({
        'date': df['date'].dt.date,
        'time': pd.to_datetime(df['Hour'] - 1, format='%H').dt.strftime('%H:%M'),
        'fuel': df['fuel'],
        'gen':  df['gen'],
    })


def parse_miso_genmix(file):
    print(':: Start handling %s ...' % file)
    if 'historical' in file:  # annual archive file
        return _parse_miso_genmix_archive(file)
    elif 'sr_gfm' in file:  # daily file
        return _parse_miso_genmix_daily_record(file)
    print('>> WARNING: Unexpected file name!')


def _parse_miso_genmix_archive(file):
    df = pd.read_excel(file, skiprows=[0, 1, 2], usecols='A:F')
    if df['HourEnding'].dtype.kind not in 'iuf':  # not number
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['HourEnding'].astype(str).apply(lambda x: x.replace('.', '').isnumeric())]
        df['HourEnding'] = df['HourEnding'].astype(int)
    area = ['Central', 'North', 'South']
    dfsel = df[df['Region'].isin(area)].groupby(by=['Market Date', 'HourEnding', 'Fuel Type']).sum().reset_index()

    genmix_mapping = {
        'Coal':     'coal',
        'Gas':      'gas',
        'Nuclear':  'nuclear',
        'Hydro':    'hydro',
        'Wind':     'wind',
        'Other':    'other',
    }
    dfsel['Fuel Type'] = dfsel['Fuel Type'].replace(genmix_mapping.keys(), genmix_mapping.values())
    return pd.DataFrame({
        'date': pd.to_datetime(dfsel['Market Date']),
        'time': pd.to_datetime(dfsel['HourEnding'] - 1, format='%H').dt.strftime('%H:%M'),
        'fuel': dfsel['Fuel Type'],
        'gen': dfsel['[RT Generation State Estimator'],
    })


def _parse_miso_genmix_daily_record(file):
    date = pd.read_excel(file, sheet_name='RT Generation Fuel Mix', skiprows=[0, 1], nrows=1, usecols='A')
    date = pd.to_datetime(date.columns[0][-10:])
    df = pd.read_excel(file,
        sheet_name='RT Generation Fuel Mix', skiprows=[0, 1, 2, 3], skipfooter=2, usecols='A, AA:AF')
    if df['Market Hour Ending'].dtype.kind not in 'iuf':  # not number
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['Market Hour Ending'].astype(str).apply(lambda x: x.replace('.', '').isnumeric())]
        df['Market Hour Ending'] = df['Market Hour Ending'].astype(int)
    df['date'] = date
    df.columns = df.columns.str.replace('.\d+', '')  # Coal.3 (pandas use this to avoid duplicate names) -> Coal
    df.columns.name = 'fuel'
    df = df.set_index(['date', 'Market Hour Ending']).stack()
    df.name = 'gen'
    df = df.reset_index()

    genmix_mapping = {
        'Coal':     'coal',
        'Gas':      'gas',
        'Nuclear':  'nuclear',
        'Hydro':    'hydro',
        'Wind':     'wind',
        'Other':    'other',
    }
    df['fuel'] = df['fuel'].replace(genmix_mapping.keys(), genmix_mapping.values())
    return pd.DataFrame({
        'date': df['date'],
        'time': pd.to_datetime(df['Market Hour Ending'] - 1, format='%H').dt.strftime('%H:%M'),
        'fuel': df['fuel'],
        'gen':  df['gen'],
    })


def parse_isone_genmix(file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, skiprows=[0, 1, 2, 3, 5], skipfooter=1, engine='python').drop(columns='H')
    df.index = pd.to_datetime(df['Date'] + 'T' + df['Time'])
    df.index.name = 'date_time'
    df = df.drop_duplicates(subset=['Date', 'Time', 'Fuel Category'])
    dfds = df[['Fuel Category', 'Gen Mw']].groupby(by='Fuel Category').resample(rule='H', closed='right').mean()
    dfds = dfds.reset_index(level=0)

    mapping = {
        'Coal': 'coal',
        'Hydro': 'hydro',
        'Natural Gas': 'gas',
        'Nuclear': 'nuclear',
        'Landfill Gas': 'other',
        'Refuse': 'other',
        'Wind': 'wind',
        'Solar': 'solar',
        'Wood': 'other',
        'Other': 'other',
        'Oil': 'oil',
    }
    dfds['Fuel Category'] = dfds['Fuel Category'].replace(mapping.keys(), mapping.values())
    dfds = dfds.groupby(by=[dfds.index, dfds['Fuel Category']]).sum().reset_index()
    return pd.DataFrame({
        'date': dfds['date_time'].dt.date,
        'time': dfds['date_time'].dt.strftime('%H:%M'),
        'fuel': dfds['Fuel Category'],
        'gen':  dfds['Gen Mw'],
    })


def parse_nyiso_genmix(file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='Time Stamp')
    df.index = pd.to_datetime(df.index)
    df.columns = df.columns.str.replace('Gen MWh', 'Gen MW')  # unify to be Gen MW
    dfds = df.groupby(by='Fuel Category').resample(rule='H', closed='right').mean()  # downsample
    dfds = dfds.reset_index()

    genmix_mapping = {
        'Dual Fuel':            'oil',  # splitted into gas & oil later
        'Natural Gas':          'gas',
        'Nuclear':              'nuclear',
        'Other Fossil Fuels':   'other',
        'Other Renewables':     'other',
        'Wind':                 'wind',
        'Hydro':                'hydro',
    }
    dfds['Fuel Category'] = dfds['Fuel Category'].replace(genmix_mapping.keys(), genmix_mapping.values())

    ratio = {
        2017: 1.99e-2,
        2018: 4.51e-2,
        2019: 4.39e-2,
        2020: 12.50e-2,  # an estimate
    }
    ratio_col = dfds['Time Stamp'].dt.year.map(ratio)
    idx_gas = dfds[dfds['Fuel Category'] == 'gas'].index
    idx_oil = dfds[dfds['Fuel Category'] == 'oil'].index
    val_gas = dfds.loc[idx_gas, 'Gen MW'].values
    val_oil = dfds.loc[idx_oil, 'Gen MW'].values
    dfds.loc[idx_gas, 'Gen MW'] = val_gas + (1 - ratio_col[idx_gas]) * val_oil
    dfds.loc[idx_oil, 'Gen MW'] = ratio_col[idx_oil] * val_oil

    dfds.reset_index()
    dfds = dfds.groupby(by=['Time Stamp', 'Fuel Category']).sum().reset_index()
    return pd.DataFrame({
        'date': dfds['Time Stamp'].dt.date,
        'time': dfds['Time Stamp'].dt.strftime('%H:%M'),
        'fuel': dfds['Fuel Category'],
        'gen': dfds['Gen MW'],
    })


def parse_pjm_genmix(file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file)
    df['datetime_beginning_ept'] = pd.to_datetime(df['datetime_beginning_ept'])
    df = df.drop_duplicates(subset=['datetime_beginning_ept', 'fuel_type'])

    genmix_mapping = {
        'Coal':             'coal',
        'Gas':              'gas',
        'Hydro':            'hydro',
        'Multiple Fuels':   'other',
        'Nuclear':          'nuclear',
        'Oil':              'oil',
        'Other':            'other',
        'Other Renewables': 'other',
        'Solar':            'solar',
        'Storage':          'other',
        'Wind':             'wind',
        'Flywheel':         'other',  # occur in July 2017
    }
    df['fuel_type'] = df['fuel_type'].replace(genmix_mapping.keys(), genmix_mapping.values())
    df = df.groupby(by=['datetime_beginning_ept', 'fuel_type']).sum().reset_index()
    return pd.DataFrame({
        'date': df['datetime_beginning_ept'].dt.date,
        'time': df['datetime_beginning_ept'].dt.strftime('%H:%M'),
        'fuel': df['fuel_type'],
        'gen':  df['mw'],
    })


def parse_spp_genmix(file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='GMT MKT Interval')
    df.index = pd.to_datetime(df.index).tz_localize('GMT').tz_convert('America/Chicago')

    genmix_mapping = {
        ' Coal Market':             'coal',
        ' Coal Self':               'coal',
        ' Diesel Fuel Oil':         'oil',
        ' Diesel Fuel Oil Market':  'oil',
        ' Diesel Fuel Oil Self':    'oil',
        ' Hydro':                   'hydro',
        ' Hydro Market':            'hydro',
        ' Hydro Self':              'hydro',
        ' Natural Gas':             'gas',
        ' Natural Gas Market':      'gas',
        ' Gas Self':                'gas',
        ' Natural Gas Self':        'gas',
        ' Nuclear':                 'nuclear',
        ' Nuclear Market':          'nuclear',
        ' Nuclear Self':            'nuclear',
        ' Solar':                   'solar',
        ' Solar Market':            'solar',
        ' Solar Self':              'solar',
        ' Wind':                    'wind',
        ' Wind Market':             'wind',
        ' Wind Self':               'wind',
        ' Waste Disposal Services':         'other',
        ' Waste Disposal Services Market':  'other',
        ' Waste Disposal Services Self':    'other',
        ' Waste Heat':              'other',
        ' Waste Heat Market':       'other',
        ' Waste Heat Self':         'other',
        ' Other':                   'other',
        ' Other Market':            'other',
        ' Other Self':              'other',
        ' Average Actual Load':     'load',
        ' Load':                    'load',
    }
    col_map = np.array([genmix_mapping[c] for c in df.columns if c in genmix_mapping.keys()])
    dfmap = pd.DataFrame({
        s: df[df.columns[col_map == s]].sum(axis=1)
        for s in ['coal', 'gas', 'oil', 'nuclear', 'hydro', 'wind', 'solar', 'other']
    })
    dfmap.columns.name = 'fuel'
    dfds = dfmap.resample(rule='H').mean().stack()  # downsample & stack
    return pd.DataFrame({
        'date': dfds.index.get_level_values(0).date,
        'time': dfds.index.get_level_values(0).strftime('%H:%M'),
        'fuel': dfds.index.get_level_values(1),
        'gen':  dfds.values,
    })


def parse_ercot_genmix(file):
    print(':: Start handling %s ...' % file)
    xls = pd.ExcelFile(file)
    sheet_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df = pd.concat([pd.read_excel(xls, sheet_name=sh) for sh in sheet_list], axis=0, sort=True)
    temp = ['%d:%02d' % (hr, min) for hr in range(24) for min in range(0, 60, 15)]
    df = df[['Date', 'Fuel'] + temp[1:] + temp[:1]]  # 00:00 is the last
    df.columns = ['Date', 'Fuel'] + temp  # shift forward 15 minutes for ease of processing
    df = df.set_index(['Date', 'Fuel'])
    df.columns.name = 'time'
    df = df.stack().rename('gen').reset_index(level=2)
    df['time'] = pd.to_datetime(df['time'], format='%H:%M')
    dfds = df.groupby(by=['Date', 'Fuel']).resample(rule='H', on='time').mean().reset_index()  # no closed on right

    genmix_mapping = {
        'Biomass':  'other',
        'Coal':     'coal',
        'Gas':      'gas',
        'Gas-CC':   'gas',
        'Hydro':    'hydro',
        'Nuclear':  'nuclear',
        'Other':    'other',
        'Solar':    'solar',
        'Wind':     'wind',
    }
    dfds['Fuel'] = dfds['Fuel'].replace(genmix_mapping.keys(), genmix_mapping.values())
    dfds = dfds.groupby(by=['Date', 'time', 'Fuel']).sum().reset_index()
    return pd.DataFrame({
        'date': dfds['Date'].dt.date,
        'time': dfds['time'].dt.strftime('%H:%M'),
        'fuel': dfds['Fuel'],
        'gen':  dfds['gen'],
    })
