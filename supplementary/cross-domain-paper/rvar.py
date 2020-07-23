import os, time
from rvar_tools import *


class CrossDomainData(object):
    def __init__(self, city, date_range):
        self.city, self.date_range = city, date_range
        self.dict, self.dict1, self.dict2 = {}, {}, {}
        self.download_data()
        self.preprocess()

    def download_data(self):
        city_mapping = {
            'nyc':      'nyiso/nyiso_nyc',
            'phila':    'pjm/pjm_phila',
            'boston':   'isone/isone_boston',
            'chicago':  'pjm/pjm_chicago',
            'la':       'caiso/caiso_la',
            'houston':  'ercot/ercot_houston',
            'kck':      'spp/spp_kck',
        }
        web_root = 'https://raw.githubusercontent.com/tamu-engineering-research/COVID-EMDA/master/'
        webs = [
            web_root + 'supplementary/cross-domain-paper/support/' \
                     + city_mapping[self.city].split('/')[1] + '_load_backcast.csv',
            web_root + 'data_release/' + city_mapping[self.city] + '_covid.csv',
            web_root + 'data_release/' + city_mapping[self.city] + '_social_distancing.csv',
            web_root + 'data_release/' + city_mapping[self.city] + '_patterns.csv',
            web_root + 'supplementary/cross-domain-paper/support/population.csv',
        ]

        # 01.load reduction data
        df_load_reduction = pd.read_csv(webs[0], index_col='date')
        df_load_reduction.index = pd.to_datetime(df_load_reduction.index)
        df_load_reduction = df_load_reduction.loc[df_load_reduction.index.isin(self.date_range)]

        # 02.covid confirmed case data
        df_covid = pd.read_csv(webs[1], index_col='date')
        df_covid.index = pd.to_datetime(df_covid.index)
        df_covid = df_covid.loc[df_covid.index.isin(self.date_range)]

        # 03.social distancing data
        df_social_distancing = pd.read_csv(webs[2], index_col=0)
        df_social_distancing.index = pd.to_datetime(df_social_distancing.index)
        df_social_distancing = df_social_distancing.loc[df_social_distancing.index.isin(self.date_range)]

        # 04.pattern data
        df_pattern = pd.read_csv(webs[3], index_col=0)
        df_pattern.index = pd.to_datetime(df_pattern.index)
        df_pattern = df_pattern.loc[df_pattern.index.isin(self.date_range)]

        # 05.population data
        df_population = pd.read_csv(webs[4], index_col='area')

        self.dict = {
            'load_reduction': -df_load_reduction['q_0.50'],
            'covid_case':     df_covid['new_confirm'],
            'stay_at_home':   df_social_distancing.iloc[:, 0] * df_population.loc[self.city].values,
            'work_on_site':   df_social_distancing.iloc[:, [2, 3]].sum(axis=1) * df_population.loc[self.city].values,
            'retail':         df_pattern['Retail'],
        }

    def preprocess(self):
        self.dict1 = {
            'load_reduction': np.log(self.dict['load_reduction']),
            'covid_case':     np.log(handle_outlier(self.dict['covid_case']) + 1),
            'stay_at_home':   np.log(self.dict['stay_at_home']),
            'work_on_site':   np.log(self.dict['work_on_site']),
            'retail':         handle_spike(np.log(self.dict['retail'])),
        }
        self.dict2 = {
            'load_reduction': self.dict1['load_reduction'].diff(1),
            'covid_case':     self.dict1['covid_case'].diff(1),
            'stay_at_home':   self.dict1['stay_at_home'].diff(1),
            'work_on_site':   self.dict1['work_on_site'].diff(1),
            'retail':         self.dict1['retail'].diff(1),
        }

    def test_stability(self):
        for name, test in self.dict2.items():
            test = test.dropna().values
            adf = sm.tsa.stattools.adfuller(test)
            print(':: [ADF Test] %15s: Statistics = %5.3f, P-Value = %.4f' % (name, adf[0], adf[1]))

    def test_cointegration(self, lag):
        test = pd.DataFrame(self.dict1).dropna()
        coint = coint_johansen(test, det_order=-1, k_ar_diff=lag)
        trace = coint.lr1[0]
        cvt = coint.cvt[0, 0]  # for 0.90
        print(':: [Cointegreation] Statistics = %7.3f, CV(90) = %6.3f, No Cointegration is Found = %s'
              % (trace, cvt, trace > cvt))


class RestrictedVectorAutoRegression(object):
    def __init__(self, variable, lag, restriction):
        self.variable, self.lag, self.restriction = variable, lag, restriction
        self.df = pd.DataFrame(self.variable).dropna()
        self.model = None

    def run_regression(self):
        gcmat = cal_grangers_causation_matrix(df_data=self.df, maxlag=self.lag)
        flg_coef, drop_num = restrict_to_zero(gcmat, self.restriction)
        redundancy = np.round(len(self.df) / (len(self.df.columns) * self.lag + len(self.df.columns)), decimals=3)
        print(':: Data Amount / Parameter Amount = %.3f' % redundancy)

        # Model Calibration
        self.model = create_rvar_model(self.df, self.lag, flg_coef)
        print(self.model.summary())

        # Model Verification (Several Tests)
        print('[Stability] Stable = %s' % self.model.is_stable())
        lb_test = [sm.stats.acorr_ljungbox(self.model.resid[col], lags=[self.lag])[1][0] for col in self.df.columns]
        print('[LB Test] P-Value = %s' % lb_test)
        dw_test = durbin_watson(self.model.resid)
        print('[DW Test] Statistics = %s' % dw_test)

    def variance_decomposition(self):
        # Note: The first figure is of interest. We focus on the proportions other than the load change itself.
        self.model.fevd(periods=30).plot()
        plt.show()

    def impulse_response(self):
        # Note: The default impulse response figure is a bit different from the manuscript. In the default figure,
        # (1) load decrease -> load reduction increase; (2) all impulses are 1% increase impulse
        self.model.irf(periods=30).plot_cum_effects(impulse=1, response=0)  # covid case -> load reduction
        plt.show()
        self.model.irf(periods=30).plot_cum_effects(impulse=4, response=0)  # retail -> load reduction
        plt.show()


if __name__ == '__main__':
    cdd = CrossDomainData(city='nyc', date_range=pd.date_range('2020-03-24', '2020-06-28'))
    cdd.test_stability()
    cdd.test_cointegration(lag=5)  # optimal lag - 1

    rvar = RestrictedVectorAutoRegression(
        variable=cdd.dict2,
        lag=6,
        restriction='rule2',
    )
    rvar.run_regression()
    rvar.variance_decomposition()
    rvar.impulse_response()
