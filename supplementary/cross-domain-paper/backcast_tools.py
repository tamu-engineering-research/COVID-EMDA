import numpy as np
import pandas as pd
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import os, pickle, random, math


class DailyDataCollector(object):
    def __init__(self, area):
        self.area = area
        self.area_mapping = {
            'caiso':        'caiso/caiso_rto',
            'miso_north':   'miso/miso_north',
            'miso_central': 'miso/miso_central',
            'miso_south':   'miso/miso_south',
            'isone':        'isone/isone_rto',
            'nyiso':        'nyiso/nyiso_rto',
            'pjm':          'pjm/pjm_rto',
            'spp_north':    'spp/spp_north',
            'spp_south':    'spp/spp_south',
            'ercot':        'ercot/ercot_rto',
            #
            'nyc':     'nyiso/nyiso_nyc',
            'phila':   'pjm/pjm_phila',
            'boston':  'isone/isone_boston',
            'chicago': 'pjm/pjm_chicago',
            'la':      'caiso/caiso_la',
            'houston': 'ercot/ercot_houston',
            'kck':     'spp/spp_kck',
        }
        self.webs = self._initialize_webs()
        self.inputs, self.outputs = None, None

    def _initialize_webs(self):
        web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
        webs = [
            web_root + 'data_release/' + self.area_mapping[self.area] + '_load.csv',
            web_root + 'data_release/' + self.area_mapping[self.area] + '_weather.csv',
            web_root + 'supplementary/cross-domain-paper/support/gdp.csv',
        ]
        return webs

    def generate_train_test_data(self, date_range, save_path=''):
        self.inputs, self.outputs = generate_daily_input_output_data(
            weather_file=self.webs[1],
            load_file=self.webs[0],
            gdp_path=self.webs[2],
            gdp_area=self.area.split(sep='_')[0],
            date_range=date_range,
        )
        area_kw = self.area_mapping[self.area].split(sep='/')[1]
        date_range_kw = date_range[0].strftime('%Y%m%d') + '-' + date_range[-1].strftime('%Y%m%d')
        file_names = {
            'input_train':  save_path + area_kw + '_input_train_' + date_range_kw + '.csv',
            'output_train': save_path + area_kw + '_output_train_' + date_range_kw + '.csv',
            'input_test':   save_path + area_kw + '_input_test_' + date_range_kw + '.csv',
            'output_test':  save_path + area_kw + '_output_test_' + date_range_kw + '.csv',
        }
        split_train_test_set(
            df_inputs=self.inputs,
            df_outputs=self.outputs,
            file_names=file_names,
        )
        print(':: Generate train and test files: \n - %s' % '\n - '.join(file_names.values()))
        return file_names


class BackcastModel(object):
    def __init__(self, predict_inputs, predict_outputs):
        if predict_inputs is None or predict_outputs is None:
            self.predict_inputs, self.predict_outputs = 0, 0
            self.train_x, self.test_x, self.train_y, self.test_y = 0, 0, 0, 0
        else:
            self.predict_inputs = pd.DataFrame(predict_inputs)
            self.predict_outputs = pd.DataFrame(predict_outputs)

            self.train_x = predict_inputs.sample(frac=0.8)
            self.test_x = predict_inputs.drop(index=self.train_x.index).append(
                self.predict_inputs[pd.to_datetime(self.predict_inputs.index).year == 2020]
            )
            self.train_y = predict_outputs.loc[self.train_x.index]
            self.test_y = predict_outputs.loc[self.test_x.index]
        self.scalar_x, self.scalar_y = 0, 0
        self.model = 0

    def train(self, model_index, n_hidden, save_path):
        if not os.path.exists(save_path):
            os.makedirs(save_path)  # create folder

        self.scalar_x = MinMaxScaler().fit(self.train_x.astype(np.float))
        train_x = self.scalar_x.transform(self.train_x)
        self.scalar_y = MinMaxScaler().fit(self.train_y.astype(np.float))
        train_y = self.scalar_y.transform(self.train_y)
        if np.shape(train_y)[1] == 1:
            train_y = train_y.flatten()  # avoid warning
        self.model = MLPRegressor(
            hidden_layer_sizes=n_hidden,
            activation='relu',
            batch_size=256, max_iter=3000,
            alpha=0.001,  # L2 regulation
            early_stopping=True,
        )
        self.model.fit(train_x, train_y)

        output_file = save_path + 'backcast_' + str(model_index) + '.pickle'
        with open(output_file, 'wb') as fn:
            pickle.dump([self.model, self.scalar_x, self.scalar_y], fn)
        print(':::: Model ' + output_file + ' is successfully saved!')
        return output_file

    def load(self, pickle_file):
        with open(pickle_file, 'rb') as fn:
            self.model, self.scalar_x, self.scalar_y = pickle.load(fn)

    def validate(self):
        test_x = self.scalar_x.transform(self.test_x)
        pred = self.model.predict(test_x)
        if len(pred.shape) == 1:
            pred = pred[:, np.newaxis]
        y_pred = self.scalar_y.inverse_transform(pred)
        acc = np.abs(y_pred / self.test_y - 1).mean().mean()
        print(':::: Accuracy = %.5f' % acc)
        return acc

    def predict(self, inputs):
        test_x = self.scalar_x.transform(inputs)
        pred = self.model.predict(test_x)
        if len(pred.shape) == 1:
            pred = pred[:, np.newaxis]
        y_pred = self.scalar_y.inverse_transform(pred)
        return y_pred


def generate_daily_input_output_data(weather_file, load_file, gdp_path, gdp_area, date_range):
    df_load = pd.read_csv(load_file, index_col='date', parse_dates=True)
    df_load = df_load.loc[df_load.index.isin(date_range)]
    df_load = df_load.mean(axis='columns')

    df_weather = pd.read_csv(weather_file, index_col='date', parse_dates=True)
    df_weather = df_weather.loc[df_weather.index.isin(date_range)]
    df_temp = df_weather[df_weather['kind'] == 'tmpc'].drop(columns='kind')  # series
    df_humid = df_weather[df_weather['kind'] == 'relh'].drop(columns='kind')
    df_wind = df_weather[df_weather['kind'] == 'sped'].drop(columns='kind')
    gdp = pd.read_csv(gdp_path, index_col='date', parse_dates=True)
    gdp = gdp.loc[gdp.index.isin(date_range)]
    holidays = USFederalHolidayCalendar().holidays()
    predict_inputs = pd.DataFrame({
        'month_day': df_temp.index.month.astype(float) + df_temp.index.day.astype(float) / 31,
        'weekday': df_temp.index.weekday,
        'gdp': gdp[gdp_area],
        'holiday': (df_temp.index.isin(holidays)).astype(int),
        'max_temp': df_temp.max(axis='columns'),
        'max_temp2': df_temp.max(axis='columns').pow(2),
        'ave_temp': df_temp.mean(axis='columns'),
        'ave_tamp2': df_temp.mean(axis='columns').pow(2),
        'q75_temp': df_temp.quantile(q=0.75, axis='columns'),
        'q25_temp': df_temp.quantile(q=0.25, axis='columns'),
        'max_humid': df_humid.max(axis='columns'),
        'ave_humid': df_humid.mean(axis='columns'),
        'ave_wind': df_wind.mean(axis='columns'),
    }).dropna()

    predict_outputs = df_load.loc[df_load.index.intersection(predict_inputs.index)].rename('load').to_frame()
    return predict_inputs, predict_outputs


def split_train_test_set(df_inputs, df_outputs, file_names):
    df_inputs = df_inputs.loc[df_inputs.index.intersection(df_outputs.index)]
    fd, ld = df_inputs.index[0], df_inputs.index[-1]  # first and last day
    test_ind = []
    while not (fd.year == ld.year and fd.month > ld.month):
        num_of_mon = monthrange(fd.year, fd.month)[1]
        days = random.sample(range(1, num_of_mon+1), 4)
        test_ind.append(date(fd.year, fd.month, days[0]))
        test_ind.append(date(fd.year, fd.month, days[1]))
        test_ind.append(date(fd.year, fd.month, days[2]))
        test_ind.append(date(fd.year, fd.month, days[3]))
        fd = fd + relativedelta(months=1)

    # split i/o
    in_test = df_inputs.loc[test_ind]
    out_test = df_outputs.loc[test_ind]
    in_train = df_inputs[~df_inputs.index.isin(test_ind)]
    out_train = df_outputs[~df_outputs.index.isin(test_ind)]
    # save to csv
    in_train.to_csv(file_names['input_train'], index=1)
    out_train.to_csv(file_names['output_train'], index=1)
    in_test.to_csv(file_names['input_test'], index=1)
    out_test.to_csv(file_names['output_test'], index=1)


def scan_training(inputs, outputs, n_batch, base_hidden, save_path):
    col_hidden, col_accuracy, col_save_file = [], [], []
    for m in range(n_batch):
        print(':: Train model #%d...' % (m + 1))
        n_hidden = (np.random.uniform(low=0.8, high=1.2, size=len(base_hidden)) * base_hidden).astype(int)
        model = BackcastModel(inputs, outputs)
        save_file = model.train(m,n_hidden=n_hidden, save_path=save_path)
        acc = model.validate()
        col_hidden.append('-'.join(n_hidden.astype(str)))
        col_accuracy.append(acc)
        col_save_file.append(save_file)
    print(':: Searching is finished!')
    output = pd.DataFrame({
        'n_hidden': col_hidden,
        'accuracy': col_accuracy,
        'save_file': col_save_file,
    })
    output.to_csv(save_path + 'model_summary.csv', index=False)
    print(':: Summary is recorded in ' + save_path + 'model_summary.csv!')


def scan_prediction(inputs, model_path, scan_path):
    file_list = [fn for fn in os.listdir(model_path) if fn.endswith('.pickle')]
    pred_list = {}
    for idx in range(len(file_list)):
        print(':: Running model #%s...' % (idx + 1))
        model = BackcastModel(None, None)
        model.load(model_path + file_list[idx])
        pred = model.predict(inputs)
        pred_list[file_list[idx]] = pred.flatten()
    print(':: Loop is finished!')
    outp = pd.DataFrame(pred_list, index=inputs.index)
    outp.columns.name = 'model'
    outp = outp.stack().rename('pred').reset_index(1)

    outp['date'] = outp.index.date
    outp['time'] = outp.index.strftime('%H:%M')
    outp = outp.set_index(['date', 'model', 'time'])
    outp = outp['pred'].unstack(level=2).reset_index().dropna()

    outp.to_csv(scan_path, index=0)
    return


def verify_model(mdl_path, in_file, out_file, mdl_num):
    file_list = [fn for fn in os.listdir(mdl_path) if fn.endswith('.pickle')]
    in_df = pd.read_csv(in_file, index_col='date', parse_dates=True)
    out_df = pd.read_csv(out_file, index_col='date', parse_dates=True)
    model_acc = pd.DataFrame({
        'model': file_list,
        'err': np.zeros(len(file_list)),
    })
    for i in model_acc.index:
        print(':: Running model #%s...' % (i + 1))
        model = BackcastModel(None, None)
        model.load(mdl_path + model_acc['model'][i])
        pred = model.predict(in_df)
        model_acc.at[i, 'err'] = _cal_mape_distance(np.array(out_df['load']), pred.flatten())

    mdl_sorted = model_acc.sort_values('err')
    return mdl_sorted[0: mdl_num]


def _cal_mape_distance(v1, v2):
    v11 = np.zeros(12)
    for i in range(math.floor(len(v1) / 2)):
        v11[math.floor(i / 4)] += (v1[i] - v2[i]) / v2[i]  # mean average percentage error (MAPE)
        v11[math.floor(i / 4)] += (v1[i + int(len(v1) / 2)] - v2[i + int(len(v1) / 2)]) / v2[i + int(len(v1) / 2)]
    v11 /= 8
    return np.linalg.norm(v11)


def generate_reduction_result(scan_prediction_file, outputs_in_covid_file, res_path):
    scan_pred = pd.read_csv(scan_prediction_file, index_col='date', parse_dates=True)
    del scan_pred['model']
    scan_pred_quantile = scan_pred.groupby(level=0).quantile(q=[0.9, 0.75, 0.5, 0.25, 0.1]).reset_index(level=1)
    scan_pred_quantile.columns = ['q', 'backcast_load']
    real_load = pd.read_csv(outputs_in_covid_file, index_col='date', parse_dates=True)

    output = pd.DataFrame({
        'date':         scan_pred_quantile.index,
        'q':            scan_pred_quantile['q'],
        'redu_num':    real_load['load'] - scan_pred_quantile['backcast_load'],
        'redu_rate':    1 - real_load['load'] / scan_pred_quantile['backcast_load'],
    }).set_index(['date', 'q'])
    output1 = output['redu_num'].unstack(level=1).reset_index()
    output1.columns = ['date', 'q_0.10', 'q_0.25', 'q_0.50', 'q_0.75', 'q_0.90']
    
    output1.to_csv(res_path, index = 0)

    output2 = output['redu_rate'].unstack(level=1).reset_index()
    output2.columns = ['date', 'q_0.10', 'q_0.25', 'q_0.50', 'q_0.75', 'q_0.90']
    
    output2.to_csv(res_path.replace('.csv','_pct.csv'), index = 0)


def print_reduction_summary(reduction_result_file):
    redu = pd.read_csv(reduction_result_file, index_col='date', parse_dates=True)
    with open(reduction_result_file.replace('pct.csv','sum.txt'),'w') as f:
        for month in [2, 3, 4, 5,6]:
            redu_sel = redu[redu.index.month == month]
            print('month = %d' % month, file=f)
            print(redu_sel.mean(axis='index').values, file=f)


def create_path(path_dict):
    for path in path_dict.values():
        if not os.path.exists(path):
            os.makedirs(path)
