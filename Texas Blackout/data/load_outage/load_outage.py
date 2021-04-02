import pandas as pd
import numpy as np
import pickle
import math
import datetime
from scipy.io import loadmat
import texas_powerflow

bus_county = pickle.load(open('bus_county.pkl','rb'))

case_mat_filepath = '../../bte2k/case_Mar3_5pm.mat'
case = loadmat(case_mat_filepath, squeeze_me=True, struct_as_record=False)
branch, bus, plant = texas_powerflow.get_dataframes_from_mpc(case["mpc"])
gen_buses = bus.loc[plant['bus_id']]


outage_tbl_path = 'txraw.csv'
outage_raw = pd.read_csv(outage_tbl_path)
#county_list = bus_county.drop_duplicates().to_list()
#county_num = len(county_list)

county_list = outage_raw['CountyName'].to_list()
county_list = list(set(county_list))
county_num = len(county_list)



date_start = datetime.datetime(year=2021, month=2, day=12, hour=0, minute=0, second=0)
ts_num = 8*24
date_list = [date_start + datetime.timedelta(hours=x) for x in range(ts_num)]
date_end = date_list[-1]

# hour_num x county_num
# percentage of lost customer for each county
cty_out_pct = np.zeros([ts_num, county_num])
# distribution of load shed among cty at each hour (absolute num of customer)
cty_out_dist = np.zeros([ts_num, county_num])

# temp containers
cty_total_cus = np.zeros([ts_num, county_num])
cty_out_cus = np.zeros([ts_num, county_num])
# iterate county
for i in range(county_num):
    cty = county_list[i]
    cty_data = outage_raw.loc[outage_raw['CountyName'] == cty]
    cty_data = cty_data.set_index(pd.DatetimeIndex(cty_data['RecordedDateTime']))
    cty_data = cty_data.drop('RecordedDateTime',axis=1)

    for j in range(48, ts_num):
        dt = date_list[j]
        # combine data from different cities in the same county
        city_names = cty_data['CityName'].unique()
        total_customer = 0
        out_customer = 0
        for c in city_names:
            city = cty_data.loc[cty_data['CityName'] == c]
            city = city.sort_index()
            city = city[~city.index.duplicated(keep='first')]
            dat = city.iloc[city.index.get_loc(dt, method = 'nearest')]
            total_customer += dat['CustomersTracked']
            out_customer += dat['CustomersOut']

        cty_total_cus[j, i] = total_customer
        cty_out_cus[j, i] = out_customer
        
cty_total_df = pd.DataFrame(cty_total_cus)
cty_total_df.columns = county_list
cty_total_df['UTC'] = date_list
cty_total_df = cty_total_df.set_index('UTC')
cty_total_df.to_csv('cty_total_all.csv')

cty_out_df = pd.DataFrame(cty_out_cus)
cty_out_df.columns = county_list
cty_out_df['UTC'] = date_list
cty_out_df = cty_out_df.set_index('UTC')
cty_out_df.to_csv('cty_outage_all.csv')


pickle.dump(cty_total_cus, open('total_cus_all.pkl',"wb"))
pickle.dump(cty_out_cus, open('out_cus_all.pkl',"wb"))
