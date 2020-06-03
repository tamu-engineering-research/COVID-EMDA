import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from rvar import *
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.stats.stattools import durbin_watson


def var_data_input(city, input_folder,
                   file_reduction, file_covid, file_social_distancing, file_pattern, file_population):
    df_redu_rate = pd.read_csv(input_folder + file_reduction, index_col='date', parse_dates=True)
    df_covid = pd.read_csv(input_folder + file_covid, index_col='date', parse_dates=True)
    df_distance = pd.read_json(input_folder + file_social_distancing, orient='table')
    df_pattern = pd.read_csv(input_folder + file_pattern, index_col=0, parse_dates=True)
    df_pattern = df_pattern.loc[df_pattern.index.year == 2020]
    df_population = pd.read_csv(input_folder + file_population, index_col='area')

    var_all_dict_log = {
        'load_reduction':   np.log(-df_redu_rate['q_0.50']),
        'covid_case':       np.log(df_covid['new_confirm']),
        'stay_at_home':     np.log(df_distance[df_distance.columns[0]] * df_population.loc[city].values),
        'work_on_site':     np.log((df_distance[df_distance.columns[2]] + df_distance[df_distance.columns[3]])
                               * df_population.loc[city].values),
        'retail':           np.log(df_pattern['Retail']),
    }
    return var_all_dict_log


def test_stationary(variable_all_dict, variable_select, date_range, diff):
    var_dict = {k: variable_all_dict[k] for k in ['redu_rate'] + variable_select}
    var_df = pd.DataFrame(var_dict).dropna()
    if date_range is not None:
        var_df = var_df.loc[var_df.index.isin(date_range)]
    var_df.plot()  # plotting
    plt.show()

    d1, d2 = diff
    var_df_L0 = pd.DataFrame({key: val.diff(d1).diff(d2) for key, val in var_dict.items()}).dropna() \
        if d2 > 0 else pd.DataFrame({key: val.diff(d1) for key, val in var_dict.items()}).dropna()
    if date_range is not None:
        var_df_L0 = var_df_L0.loc[var_df_L0.index.isin(date_range)]
    var_df_L0.plot()  # plotting
    plt.show()

    adf_list = []
    for v in var_df.columns:
        test = var_df_L0[v].diff(d1).dropna() if d2 == 0 else var_df_L0[v].diff(d1).diff(d2).dropna()
        pval = sm.tsa.stattools.adfuller(test)[1]
        adf_list.append(pval)
        print('Variable = %s, p-Value = %f' % (v, pval))
    assert np.all(np.array(adf_list) < 0.05), '\n\n*** ERROR: Time series arrays are not stationary!\n\n'


def var_simulate(variable_all_dict, variable_select, date_range, diff, lag, restriction):
    var_dict = {k: variable_all_dict[k] for k in ['load_reduction'] + variable_select}
    var_df = pd.DataFrame(var_dict).dropna()
    if date_range is not None:
        var_df = var_df.loc[var_df.index.isin(date_range)]
    mark = ''

    # # ---------- Cointegration ----------
    test = var_df.copy()
    coint = coint_johansen(test, det_order=-1, k_ar_diff=lag)
    if coint.lr1[0] <= coint.cvt[0, 1]:
        print('\n\n*** ERROR: Cointegration exists!\n\n')
        mark += 'Cointegration  '
    print(':: Finish testing cointegration!')

    # # ---------- Stability Test + Detrending ----------
    d1, d2 = diff
    var_df_L0 = pd.DataFrame({key: val.diff(d1).diff(d2) for key, val in var_dict.items()}).dropna() \
        if d2 > 0 else pd.DataFrame({key: val.diff(d1) for key, val in var_dict.items()}).dropna()
    if date_range is not None:
        var_df_L0 = var_df_L0.loc[var_df_L0.index.isin(date_range)]

    start_date, end_date = var_df_L0.index[0].date(), var_df_L0.index[-1].date()
    print(':: Selected data volume: %d days, from %s to %s' % ((end_date - start_date).days, start_date, end_date))

    # # ---------- Granger Causality Wald Test ----------
    gcmat = grangers_causation_matrix(
        data=var_df_L0,
        variables=var_df_L0.columns,
        maxlag=lag,
    )

    # # ---------- VAR Regression ----------
    flg_coef, drop_num = restrict_to_zero(gcmat, restriction)
    n_var = len(var_df_L0.columns)
    if (n_var ** 2 - drop_num) * lag + n_var > len(var_df_L0):
        print('\n\n*** ERROR: Potential overfitting risk!\n\n')
        mark += 'Potential_Overfitting  '

    model = VAR_created(var_df_L0, num_lag=lag, flg_coef=flg_coef)
    print(model.summary())

    # ---------- VAR Model Verification (Several Tests) ----------
    if not model.is_stable():
        print('\n\n*** ERROR: The forecast arrays are not stationary!\n\n')
        mark += 'Non_Stationary_VAR  '
    lb_test = np.array([sm.stats.acorr_ljungbox(model.resid[col], lags=[lag])[1] for col in var_df_L0.columns])
    if not np.all(lb_test > 0.05):
        print('\n\n*** ERROR: Residuals autorecorrelation is still strong!\n\n')
        mark += 'Residual_Autorecorrelation  '
    dw_test = durbin_watson(model.resid)
    if not np.all(np.abs(dw_test - 2) < 0.4):
        print('\n\n*** ERROR: Residuals are correlated to independent variables!\n\n')
        mark += 'Residual_Correlated  '
    if model.test_normality().pvalue <= 0.05:
        print('\n\n*** ERROR: Residuals are not normally-distributed process!\n\n')
        mark += 'Non_Normal_Residual'
    print(':: The model has been tested for all verfification tests!')

    # # ---------- Impulse Response Analysis ----------
    irf = model.irf(periods=20)
    irf_contrib = {var_df_L0.columns[i]: irf.lr_effects[0, i] / irf.lr_effects[i, i]
                   for i in range(1, len(var_df_L0.columns))}
    print(':: Impulse response steady state: %s' % irf_contrib)

    # # ---------- Forecast Error Variance Decomposition ----------
    fevd = model.fevd(20)
    redu_explain = 1 - fevd.decomp[0, -1, 0]
    print(':: Load reduction rate can be explained by %.4f' % redu_explain)

    # # ---------- Output ----------
    output = pd.DataFrame({
        'variables':    ', '.join(variable_select),
        'date_range':   date_range[0].strftime('%Y-%m-%d') + ' to ' + date_range[-1].strftime('%Y-%m-%d'),
        'lag':          lag,
        'restrict':     restriction,
        'aic':          model.aic,
        'bic':          model.bic,
        'fpe':          model.fpe,
        'hqic':         model.hqic,
        'explain_rate': redu_explain,
        'irf_contrib':  np.str(irf_contrib),
        'mark':         mark,
    }, index=[0])
    return output


def grangers_causation_matrix(data, variables, maxlag):
    df = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
    for c in df.columns:
        for r in df.index:
            test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
            p_values = [test_result[i + 1][0]['ssr_chi2test'][1] for i in range(maxlag)]
            min_p_value = np.min(p_values)
            df.loc[r, c] = min_p_value
    df.columns = [var + '_x' for var in variables]
    df.index = [var + '_y' for var in variables]
    pd.set_option('display.max_columns', None)
    print(df)
    return df


def restrict_to_zero(granger_matrix, restriction_rule):
    output = np.ones_like(granger_matrix)
    n1, n2 = np.shape(output)
    if restriction_rule == 'rule1':  # drop 1st column + keep 1st row
        output[1:, 0] = 0
    elif restriction_rule == 'rule2':  # drop 1st column + keep 1st row + drop significance > 0.1
        output[1:, 0] = 0
        for i in range(1, n1):
            for j in range(1, n2):
                if granger_matrix.iloc[i, j] > 0.1 and i != j:
                    output[i, j] = 0
    elif restriction_rule == 'rule3':  # drop 1st column + keep 1st row + drop significance > 0.05
        output[1:, 0] = 0
        for i in range(1, n1):
            for j in range(1, n2):
                if granger_matrix.iloc[i, j] > 0.05 and i != j:
                    output[i, j] = 0
    drop_num = np.sum(np.sum(np.ones_like(granger_matrix) - output))
    return output, drop_num




