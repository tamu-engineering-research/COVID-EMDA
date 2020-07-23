import numpy as np
import pandas as pd


def parse_caiso_lmp(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, index_col='INTERVALSTARTTIME_GMT')
    df.index = pd.to_datetime(df.index).tz_localize('GMT').tz_convert('America/Los_Angeles')
    df = df.sort_index()
    df = df[df['LMP_TYPE'] == 'LMP'].loc[:, ['NODE', 'MW']]
    area_mapping = {
        'rto': ['TH_SP15_GEN-APND', 'TH_NP15_GEN-APND', 'TH_ZP26_GEN-APND'],
        'sf': 'BAYSHOR2_1_N001',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    if area == 'rto':
        dfsel = df[df['NODE'].isin(area_mapping[area])]
        dfsel = dfsel.drop(columns='NODE').groupby(level=0).mean()
    else:
        dfsel = df[df['NODE'] == area_mapping[area]]
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp':  dfsel['MW'],
    })


def parse_miso_lmp(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_excel(file, skiprows=list(range(14)), nrows=24)
    df['time'] = df.iloc[:, 0].str.replace('Hour ', '').astype(int) - 1
    df['date'] = pd.to_datetime(pd.read_excel(file, nrows=1, usecols='A').values[0, 0][-10:])

    area_mapping = {
        'rto':      'MISO System',
        'chicago':  'Illinois Hub',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    return pd.DataFrame({
        'date': df['date'].dt.date,
        'time': df['time'].astype(str).str.zfill(2) + ':00',
        'lmp':  df[area_mapping[area]].values,
    })


def parse_isone_lmp(area, file):
    print(':: Start handling %s ...' % file)
    if 'WW_DALMP' in file:
        return _parse_isone_lmp_official(area, file)
    elif 'ISO-NE Day-Ahead Energy Price' in file:
        return _parse_isone_lmp_energyonline(area, file)
    print('>> WARNING: Unrecognized file name!')


def _parse_isone_lmp_official(area, file):
    df = pd.read_csv(file, skiprows=[0, 1, 2, 3, 5], skipfooter=1, engine='python',
        usecols=['Date', 'Hour Ending', 'Location Name', 'Locational Marginal Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    if df['Hour Ending'].dtype.kind not in 'iuf':  # not number
        print(':::: Find non-numeric hour records in %s' % file)
        df = df[df['Hour Ending'].astype(str).apply(lambda x: x.replace('.', '').isnumeric())]  # remove records 02X
    df['time'] = df['Hour Ending'].astype(int) - 1
    df = df.drop_duplicates(subset=['Date', 'time', 'Location Name'])

    area_mapping = {
        'rto':      ['.Z.MAINE', '.Z.NEWHAMPSHIRE', '.Z.VERMONT', '.Z.CONNECTICUT',
                     '.Z.RHODEISLAND', '.Z.SEMASS', '.Z.WCMASS', '.Z.NEMASSBOST'],
        'boston':   ['.Z.NEMASSBOST'],
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['Location Name'].isin(area_mapping[area])]
    dfsel = dfsel[['Date', 'time', 'Locational Marginal Price']].groupby(by=['Date', 'time']).mean().reset_index()
    return pd.DataFrame({
        'date': dfsel['Date'].dt.date,
        'time': dfsel['time'].astype(str).str.zfill(2) + ':00',
        'lmp':  dfsel['Locational Marginal Price'],
    })


def _parse_isone_lmp_energyonline(area, file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop_duplicates(subset=['Date', 'Node']).set_index('Date')

    area_mapping = {
        'rto':      ['.Z.MAINE', '.Z.NEWHAMPSHIRE', '.Z.VERMONT', '.Z.CONNECTICUT',
                     '.Z.RHODEISLAND', '.Z.SEMASS', '.Z.WCMASS', '.Z.NEMASSBOST'],
        'boston':   ['.Z.NEMASSBOST'],
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['Node'].isin(area_mapping[area])]
    dfsel = dfsel['LMP'].groupby(level=0).mean()
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp':  dfsel.values,
    })


def parse_nyiso_lmp(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file).drop_duplicates(subset=['Time Stamp', 'Name'])
    df['Time Stamp'] = pd.to_datetime(df['Time Stamp'])
    df = df.set_index('Time Stamp')

    area_mapping = {
        'rto':  ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL',
                 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST'],
        'nyc':  'N.Y.C.',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    if area == 'rto':
        dfsel = df[df['Name'].isin(area_mapping[area])]
        dfsel = dfsel.loc[:, 'LBMP ($/MWHr)'].groupby(level=0).mean()
    else:
        dfsel = df[df['Name'] == area_mapping[area]].loc[:, 'LBMP ($/MWHr)']
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp':  dfsel.values,
    })


def parse_pjm_lmp(area, file):
    print(':: Start handling %s ...' % file)
    df = pd.read_csv(file, usecols=['datetime_beginning_ept', 'pnode_name', 'total_lmp_da'])
    df['datetime_beginning_ept'] = pd.to_datetime(df['datetime_beginning_ept'])
    df = df.drop_duplicates(subset=['datetime_beginning_ept', 'pnode_name']).set_index('datetime_beginning_ept')

    area_mapping = {
        'rto':      'PJM-RTO',
        'phila':    'PECO',
        'chicago':  'COMED',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['pnode_name'] == area_mapping[area]]
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp':  dfsel['total_lmp_da'],
    })


def parse_spp_lmp(area, file):
    print(':: Start handling %s ...' % file)
    if 'DA-LMP-MONTHLY' in file:
        return _parse_spp_lmp_archive(area, file)
    elif 'DA-LMP-SL' in file:
        return _parse_spp_lmp_daily_record(area, file)
    print('>> WARNING: Unrecognized file name!')


def _parse_spp_lmp_daily_record(area, file):
    df = pd.read_csv(file, index_col='Interval', usecols=['Interval', 'Settlement Location', 'LMP'])
    df.index = pd.to_datetime(df.index) - pd.Timedelta(hours=1)

    area_mapping = {
        'rto': ['SPPNORTH_HUB', 'SPPSOUTH_HUB'],
        'kck': ['AECI'],
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['Settlement Location'].isin(area_mapping[area])]
    dfsel = dfsel.loc[:, 'LMP'].groupby(level=0).mean()
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp':  dfsel.values,
    })


def _parse_spp_lmp_archive(area, file):
    df = pd.read_csv(file)
    df = df[df[' Price Type'] == 'LMP'].drop(columns=[' Price Type', ' PNODE Name'])
    df = df.drop_duplicates(subset=['Date', ' Settlement Location Name']).set_index(
        ['Date', ' Settlement Location Name'])
    df.columns.name = 'time'
    df = df.stack(dropna=True).rename('lmp').reset_index()
    df['time'] = df['time'].str.replace(pat=r'HE\d\d', repl=lambda m: np.str(int(m.group(0)[2:]) - 1))  # avoid 24:00
    df.index = pd.to_datetime(df['Date'] + 'T' + df['time'] + ':00')
    df.index = df.index.tz_localize('GMT').tz_convert('America/Chicago')

    area_mapping = {
        'rto':  ['SPPNORTH_HUB', 'SPPSOUTH_HUB'],
        'kck':  ['AECI'],
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df[' Settlement Location Name'].isin(area_mapping[area])]
    dfsel = dfsel.loc[:, 'lmp'].groupby(level=0).mean()
    return pd.DataFrame({
        'date': dfsel.index.date,
        'time': dfsel.index.strftime('%H:%M'),
        'lmp': dfsel.values,
    })


def parse_ercot_lmp(area, file):
    print(':: Start handling %s ...' % file)
    xls = pd.ExcelFile(file)
    df = pd.concat([pd.read_excel(xls, sheet_name=sh) for sh in [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']], axis=0)
    df['Hour Ending'] = df['Hour Ending'].str.replace(
        pat=r'\d\d:', repl=lambda m: np.str(int(m.group(0)[0:2]) - 1).zfill(2) + ':')  # avoid 24:00

    area_mapping = {
        'rto':      'HB_HUBAVG',
        'houston':  'HB_HOUSTON',
    }
    assert area in area_mapping.keys(), '>> WARNING: Unexpected area keyword!'
    dfsel = df[df['Settlement Point'] == area_mapping[area]]
    return pd.DataFrame({
        'date': pd.to_datetime(dfsel['Delivery Date']).dt.date,
        'time': dfsel['Hour Ending'],
        'lmp':  dfsel['Settlement Point Price'],
    })

