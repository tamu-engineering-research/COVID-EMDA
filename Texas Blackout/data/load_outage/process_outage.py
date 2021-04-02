import pandas as pd
import numpy as np
import pickle
import math
import datetime
from scipy.io import loadmat
import texas_powerflow


bus_county = pickle.load(open('bus_county.pkl','rb'))
county_list = bus_county.drop_duplicates().to_list()
county_num = len(county_list)

total = pickle.load(open('total_cus.pkl','rb'))
out = pickle.load(open('out_cus.pkl','rb'))

# find max of total customers

date_start = datetime.datetime(year=2021, month=2, day=12, hour=0, minute=0, second=0)
ts_num = 8*24
date_list = [date_start + datetime.timedelta(hours=x) for x in range(ts_num)]
date_end = date_list[-1]
print(total)
# hour_num x county_num
# percentage of lost customer for each county
cty_out_pct = np.zeros([ts_num, county_num])
# distribution of load shed among cty at each hour (absolute num of customer)
cty_out_dist = np.zeros([ts_num, county_num])

for i in range(48,ts_num):
    total_ts = total[i,:]
    total_ts[total_ts==0] = 1;
    cty_out_pct[i,:] = np.divide(out[i,:], total_ts)
    cty_out_dist[i,:] = out[i,:] / sum(out[i,:])

out_pct_df = pd.DataFrame(cty_out_pct)
out_pct_df.columns = county_list
out_pct_df['UTC'] = date_list
out_pct_df = out_pct_df.set_index('UTC')
out_pct_df.to_csv('cty_out_pct.csv')

out_dist_df = pd.DataFrame(cty_out_dist)
out_dist_df.columns = county_list
out_dist_df['UTC'] = date_list
out_dist_df = out_dist_df.set_index('UTC')
out_dist_df.to_csv('cty_out_dist.csv')
