import pandas as pd
import numpy as np
import pickle
import math
import datetime
from scipy.io import loadmat
import texas_powerflow


bus_county = pickle.load(open('bus_county.pkl','rb'))
county_list = bus_county.drop_duplicates().to_list()
county_num =len(county_list)

total = pickle.load(open('total_cus.pkl','rb'))
out = pickle.load(open('out_cus.pkl','rb'))

# find max of total customers

date_start = datetime.datetime(year=2021, month=2, day=12, hour=0, minute=0, second=0)
ts_num = 8*24
date_list = [date_start + datetime.timedelta(hours=x) for x in range(ts_num)]
date_end = date_list[-1]
print(county_list)
# hour_num x county_num
# percentage of lost customer for each county
cty_out_avg = np.zeros([1, county_num])
cty_out_ttl = np.zeros([1, county_num])
# distribution of load shed among cty at each hour (absolute num of customer)

line_range = range(92,104)

for i in range(county_num):
    all_ttl = total[line_range,i]
    real_ttl = max(all_ttl)
    real_out = []
    for j in line_range:
        if all_ttl[j-92] == real_ttl:
            real_out.append(out[j, i])
    cty_out_avg[0, i] = np.mean(real_out)
    cty_out_ttl[0, i] = real_ttl
    
pd.DataFrame(cty_out_avg).to_csv("cty_out_avg.csv", header=None, index=None)
pd.DataFrame(cty_out_ttl).to_csv("cty_ttl_avg.csv", header=None, index=None)
