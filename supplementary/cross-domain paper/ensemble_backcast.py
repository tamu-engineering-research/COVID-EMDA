import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas.tseries.holiday import USFederalHolidayCalendar
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import os, pickle


def generate_reduction_result_file(scan_prediction_file, outputs_in_covid_file):
    scan_pred = pd.read_csv(scan_prediction_file, index_col='date', parse_dates=True)
    del scan_pred['model']
    scan_pred_quantile = scan_pred.groupby(level=0).quantile(q=[0.9, 0.75, 0.5, 0.25, 0.1]).reset_index(level=1)
    scan_pred_quantile.columns = ['q', 'backcast_load']
    real_load = pd.read_csv(outputs_in_covid_file, index_col='date', parse_dates=True)

    output = pd.DataFrame({
        'date':         scan_pred_quantile.index,
        'q':            scan_pred_quantile['q'],
        'redu_rate':    1 - real_load['load'] / scan_pred_quantile['backcast_load'],
    }).set_index(['date', 'q'])
    output = output['redu_rate'].unstack(level=1).reset_index()
    output.columns = ['date', 'q_0.10', 'q_0.25', 'q_0.50', 'q_0.75', 'q_0.90']
    output.to_csv('reduction_result.csv')


    
def print_reduction_summary(reduction_result_file):
    redu = pd.read_csv(reduction_result_file, index_col='date', parse_dates=True)
    
    for month in [2, 3, 4, 5]:
        redu_sel = redu[redu.index.month == month]
        print('month = %d' % month)
        print(redu_sel.mean(axis='index').values)



class BackCastLoadForecast(object):
    def __init__(self, predict_inputs, predict_outputs):
        if predict_inputs is None or predict_outputs is None:
            self.predict_inputs, self.predict_outputs = 0, 0
            self.train_x, self.test_x, self.train_y, self.test_y = 0, 0, 0, 0
        else:
            self.predict_inputs = pd.DataFrame(predict_inputs)
            self.predict_outputs = pd.DataFrame(predict_outputs)

            self.train_x = predict_inputs.sample(frac=0.8)
            self.test_x = predict_inputs.drop(index=self.train_x.index).append(
                self.predict_inputs[pd.to_datetime(self.predict_inputs.index).year == 2020]  # NEW HERE!
            )
            self.train_y = predict_outputs.loc[self.train_x.index]
            self.test_y = predict_outputs.loc[self.test_x.index]
        self.scalar_x, self.scalar_y = 0, 0
        self.model = 0

    def train(self, n_hidden, save_path):
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
            batch_size=512, max_iter=3000,
            alpha=0.001,  # L2 regulation
            early_stopping=True,
        )
        self.model.fit(train_x, train_y)

        output_file = save_path + 'backcast_' + np.str(np.random.rand())[2: 6] + '.pickle'
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


def generate_daily_train_test_data(mode, weather_file, load_file, date_range):
    df_load = pd.read_csv(load_file, index_col='date', parse_dates=True)
    df_load = df_load.loc[df_load.index.isin(date_range)]
    df_load = df_load.mean(axis='columns')

    df_weather = pd.read_csv(weather_file, index_col='date', parse_dates=True)
    df_weather = df_weather.loc[df_weather.index.isin(date_range)]
    df_temp = df_weather[df_weather['kind'] == 'tmpc'].drop(columns='kind')  # series
    df_humid = df_weather[df_weather['kind'] == 'relh'].drop(columns='kind')
    df_wind = df_weather[df_weather['kind'] == 'sped'].drop(columns='kind')

    holidays = USFederalHolidayCalendar().holidays()
    predict_inputs = pd.DataFrame({
        'month_day': df_temp.index.month.astype(float) + df_temp.index.day.astype(float) / 31,
        'weekday':   df_temp.index.weekday,
        'holiday':   (df_temp.index.isin(holidays)).astype(int),
        'max_temp':  df_temp.max(axis='columns'),
        'max_temp2': df_temp.max(axis='columns').pow(2),
        'ave_temp':  df_temp.mean(axis='columns'),
        'ave_tamp2': df_temp.mean(axis='columns').pow(2),
        'q75_temp':  df_temp.quantile(q=0.75, axis='columns'),
        'q25_temp':  df_temp.quantile(q=0.25, axis='columns'),
        'max_humid': df_humid.max(axis='columns'),
        'ave_humid': df_humid.mean(axis='columns'),
        'ave_wind':  df_wind.mean(axis='columns'),
    }).dropna()

    predict_outputs = df_load.loc[df_load.index.intersection(predict_inputs.index)].rename('load').to_frame()
    if mode == 1:  
        in_path = weather_file.replace('input','input_train_test_all').replace('weather','inputs')
        out_path = in_path.replace('inputs','outputs')
    elif mode == 2:
        in_path = weather_file.replace('input','input_train_test_all').replace('weather','inputs_ver')
        out_path = in_path.replace('inputs','outputs')
    elif mode == 3:
        in_path = weather_file.replace('input','input_train_test_all').replace('weather','inputs_cov')
        out_path = in_path.replace('inputs','outputs')

    
    predict_inputs.to_csv(in_path)
    predict_outputs.to_csv(out_path)
    print(':: Output files: inputs.csv, outputs.csv')
    return predict_inputs, predict_outputs



