import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.var_model import VARResults, VARResultsWrapper
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.stats.stattools import durbin_watson


def create_rvar_model(y, num_lag, flg_coef):
    if isinstance(flg_coef, np.ndarray):
        flg_coef = flg_coef.tolist()
    # 01. OLS
    num_var = y.shape[1]
    models = []
    results = []
    params = []
    for i in range(num_var):
        x_lagged = _create_x_from_y(y=y, maxlag=num_lag, flg_coef=flg_coef[i])
        model_tmp = sm.OLS(y.iloc[num_lag:, i].values, sm.add_constant(x_lagged))
        result_tmp = model_tmp.fit()
        params_tmp = _extend_params(params=result_tmp.params, maxlag=num_lag, flg_coef=flg_coef[i])

        models.append(model_tmp)
        results.append(result_tmp)
        params.append(params_tmp)

    # 02. Create VAR
    model_empty = VAR(y)
    y_lagged = _create_y_lagged(y=y, maxlag=num_lag)
    params_created = np.concatenate(tuple(params), axis=0).T
    sigma_u_created = _cal_sigma_u(y.iloc[num_lag:].values, params_created, y_lagged)

    varr = VARResults(
        endog=y.values,
        endog_lagged=y_lagged,
        params=params_created,
        sigma_u=sigma_u_created,
        lag_order=num_lag,
        model=model_empty,
        names=y.columns,
        dates=np.array(range(y_lagged.shape[0])))
    model_created = VARResultsWrapper(varr)
    return model_created


def _extend_params(params, maxlag, flg_coef):
    params = params.tolist()
    params_extend = [params[0]]
    flg_coef_ext = flg_coef * maxlag

    head = 0
    for i in range(len(flg_coef_ext)):
        if flg_coef_ext[i] == 0:
            params_extend = params_extend + [0]
        else:
            head += 1
            params_extend = params_extend + [params[head]]
    params_extend = np.array(params_extend).reshape((1, -1))
    return params_extend


def _cal_sigma_u(y, params, x):
    err = y - x.dot(params)
    return np.cov(err.T)


def _create_y_lagged(y, maxlag):
    y_array = y.values
    num_sample = y_array.shape[0]
    y_lagged = np.ones((num_sample - maxlag, 1))
    for i in range(maxlag):
        y_tmp = y_array[maxlag - i - 1:-i - 1, :]
        y_lagged = np.concatenate((y_lagged, y_tmp), axis=1)
    return y_lagged


def _create_x_from_y(y, maxlag, flg_coef):
    y_array = y.values
    # get full x
    x = []
    for i in range(maxlag):
        y_tmp = y_array[maxlag - i - 1:-i - 1, :]
        if len(x) == 0:
            x = y_tmp.copy()
        else:
            x = np.concatenate((x, y_tmp), axis=1)
    # extend flg_coef
    flg_coef_ext = flg_coef * maxlag
    x_flg_coef = []
    for i in range(len(flg_coef_ext)):
        if not flg_coef_ext[i] == 0:
            if len(x_flg_coef) == 0:
                x_flg_coef = x[:, i].reshape((-1, 1)).copy()
            else:
                x_flg_coef = np.concatenate((x_flg_coef, x[:, i].reshape((-1, 1))), axis=1)
    return x_flg_coef


def cal_grangers_causation_matrix(df_data, maxlag):
    variables = df_data.columns
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    for c in df.columns:
        for r in df.index:
            test_result = grangercausalitytests(df_data[[r, c]], maxlag=maxlag, verbose=False)
            p_values = [test_result[i + 1][0]['ssr_chi2test'][1] for i in range(maxlag)]
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    pd.set_option('display.max_columns', None)
    print(df)
    return df


def restrict_to_zero(granger_matrix, rule):
    output = np.ones_like(granger_matrix, dtype=np.int)
    n1, n2 = np.shape(output)
    if rule == 'rule1':  # drop 1st column + keep 1st row
        output[1:, 0] = 0
    elif rule == 'rule2':  # drop 1st column + keep 1st row + drop significance > 0.1
        output[1:, 0] = 0
        for i in range(1, n1):
            for j in range(1, n2):
                if granger_matrix.iloc[i, j] > 0.1 and i != j:
                    output[i, j] = 0
    elif rule == 'rule3':  # drop 1st column + keep 1st row + drop significance > 0.05
        output[1:, 0] = 0
        for i in range(1, n1):
            for j in range(1, n2):
                if granger_matrix.iloc[i, j] > 0.05 and i != j:
                    output[i, j] = 0
    drop_num = np.sum(np.sum(np.ones_like(granger_matrix) - output))
    return output, drop_num


def handle_outlier(sr_covid):
    threshold_ramp = 2
    threshold_level = 30 if sr_covid.max() > 500 else 10
    sr_covid.loc[sr_covid < 0] = 0
    df_log_diff = np.log(sr_covid + 1).diff(1)
    handle_date = []

    suspecious_neg_date = df_log_diff.index[df_log_diff < -threshold_ramp]
    for date in suspecious_neg_date:
        prev_date = date - pd.Timedelta(days=1)
        if sr_covid.loc[prev_date] > threshold_level:
            if date not in handle_date:
                handle_date.append(date)
    suspecious_pos_date = df_log_diff.index[df_log_diff > threshold_ramp]
    for date in suspecious_pos_date:
        prev_date = date - pd.Timedelta(days=1)
        if sr_covid.loc[date] > threshold_level:
            if prev_date not in handle_date:
                handle_date.append(prev_date)

    handle_date = np.sort(handle_date)
    for d in handle_date:
        print(':: Find outlier in COVID-19 cases on %s' % d.strftime('%Y-%m-%d'))
    sr_accum = np.cumsum(sr_covid)
    sr_accum.loc[handle_date] = np.nan
    sr_accum = sr_accum.interpolate()
    sr_covid_ = np.round(sr_accum.diff(1)).rename(sr_covid.name)
    sr_covid_.iloc[0] = sr_covid.iloc[0]
    return sr_covid_.astype(int)


def handle_spike(sr_retail):
    ub = sr_retail.nlargest(n=2)[-1]
    lb = sr_retail.nsmallest(n=2)[-1]
    return sr_retail.clip(lb, ub)
