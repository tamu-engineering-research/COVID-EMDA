import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.var_model import VARProcess
from statsmodels.tsa.vector_ar.var_model import VARResults, VARResultsWrapper
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.stats.stattools import durbin_watson
from numpy.linalg import inv


def VAR_created(y, num_lag, flg_coef):
    if isinstance(flg_coef, np.ndarray):
        flg_coef = flg_coef.tolist()
    # step 1 OLS
    num_var = y.shape[1]
    models = []
    results = []
    params = []
    for i in range(num_var):
        x_lagged = create_x_from_y(y=y, maxlag=num_lag, flg_coef=flg_coef[i])
        model_tmp = sm.OLS(y.iloc[num_lag:, i].values, sm.add_constant(x_lagged))
        result_tmp = model_tmp.fit()
        params_tmp = extend_params(params=result_tmp.params, maxlag=num_lag, flg_coef=flg_coef[i])
        
        models.append(model_tmp)
        results.append(result_tmp)
        params.append(params_tmp)

    # step 2 create VAR
    model_empty = VAR(y)
    y_lagged = create_y_lagged(y=y, maxlag=num_lag)
    params_created = np.concatenate(tuple(params),axis=0).T
    sigma_u_created = cal_sigma_u(y.iloc[num_lag:].values, params_created, y_lagged)

    varr = VARResults(
        endog=y.values,
        endog_lagged=y_lagged, 
        params=params_created, 
        sigma_u=sigma_u_created, 
        lag_order=num_lag, 
        model = model_empty,
        names = y.columns,
        dates = np.array(range(y_lagged.shape[0])))
    model_created = VARResultsWrapper(varr)
    return model_created

def extend_params(params, maxlag, flg_coef):
    params = params.tolist()
    params_extend = [params[0]]
    flg_coef_ext = flg_coef*maxlag

    head = 0
    for i in range(len(flg_coef_ext)):
        if flg_coef_ext[i]==0:
            params_extend = params_extend+[0]
        else:
            head += 1
            params_extend = params_extend+[params[head]]
    params_extend = np.array(params_extend).reshape((1,-1))
    return params_extend


def cal_sigma_u(y,params,x):
    err = y-x.dot(params)
    return np.cov(err.T)


def create_y_lagged(y, maxlag):
    y_array = y.values
    num_sample = y_array.shape[0]
    y_lagged = np.ones((num_sample-maxlag,1))
    for i in range(maxlag):
        y_tmp = y_array[maxlag-i-1:-i-1,:]
        y_lagged = np.concatenate((y_lagged, y_tmp), axis=1)
    return y_lagged


def create_x_from_y(y, maxlag, flg_coef):
    y_array = y.values
    # get full x
    x = []
    for i in range(maxlag):
        y_tmp = y_array[maxlag-i-1:-i-1,:]
        if len(x)==0:
            x = y_tmp.copy()
        else:
            x = np.concatenate((x, y_tmp), axis=1)
    # extend flg_coef
    flg_coef_ext = flg_coef*maxlag
    x_flg_coef = []
    for i in range(len(flg_coef_ext)):
        if not flg_coef_ext[i]==0:
            if len(x_flg_coef)==0:
                x_flg_coef = x[:,i].reshape((-1,1)).copy()
            else:
                x_flg_coef = np.concatenate((x_flg_coef, x[:,i].reshape((-1,1))), axis=1)
    return x_flg_coef
