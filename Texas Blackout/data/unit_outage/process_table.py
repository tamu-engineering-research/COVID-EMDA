import pandas as pd
import numpy as np
import pickle
import math
import datetime
from scipy.io import loadmat
import texas_powerflow

gen_county = pickle.load(open('gen_county.pkl','rb'))

case_mat_filepath = '../../bte2k/case_Mar3_5pm.mat'
case = loadmat(case_mat_filepath, squeeze_me=True, struct_as_record=False)
branch, bus, plant = texas_powerflow.get_dataframes_from_mpc(case["mpc"])
gen_buses = bus.loc[plant['bus_id']]

outage_tbl_path = 'unit_outage.xlsx'

date_start = datetime.datetime(year=2021, month=2, day=12, hour=0, minute=0, second=0)
ts_num = 8*24
date_list = [date_start + datetime.timedelta(hours=x) for x in range(ts_num)]
date_end = date_list[-1]

outage_raw = pd.read_excel(outage_tbl_path)
outage_raw = outage_raw.drop('Unnamed: 4', axis=1).dropna()

county_list = gen_county.drop_duplicates().to_list()
county_num = len(county_list)

# 0:county_num -- out MW, county_num:2*county_num -- total MW
ng_out_list = np.zeros([ts_num, 2*county_num])
coal_out_list = np.zeros([ts_num, 2*county_num])
pv_out_list = np.zeros([ts_num, 2*county_num])

ng_derate_cap = np.zeros([ts_num, county_num])
ng_derate_ttl = np.zeros([ts_num, county_num])
# aggregate by county
for ind, row in outage_raw.iterrows():
    start_str = row['START']
    end_str = row['END']
    cty = row['COUNTY']

    # parse datetime
    start_ts =  datetime.datetime.strptime(start_str, '%m/%d/%y %I:%M %p')
    end_ts =  datetime.datetime.strptime(end_str, '%m/%d/%y %I:%M %p')

    # locate county
    for i in range(county_num):
        if county_list[i].lower() == cty.lower():
            cty_ind = i
            break
        if i == county_num - 1:
            print("Cannot locate county "+cty+"!");
            print(row['FUEL TYPE'])
    
    # locate start and end row num
    start_row = (start_ts - date_start).days * 24 + math.ceil((start_ts - date_start).seconds / 3600)
    end_row = (end_ts - date_start).days * 24 + (end_ts - date_start).seconds // 3600
    if end_row > ts_num:
        end_row = ts_num - 1

    # group by type
    on_mw = float(row['AVAILABLE MW AFTER OUTAGE/DERATE'])
    out_mw = float(row['MW REDUCTION FROM OUTAGE/DERATE'])
    ttl_mw = float(row['SEASONAL MAX MW (HSL)'])
    if row['FUEL TYPE'] == 'NG':
        ng_out_list[start_row:end_row+1, cty_ind] += out_mw
        ng_out_list[start_row:end_row+1, county_num + cty_ind] += ttl_mw
        # compute factor of derating
        if on_mw > 0:
            ng_derate_cap[start_row:end_row+1, cty_ind] += on_mw
            ng_derate_ttl[start_row:end_row+1, cty_ind] += ttl_mw
    elif row['FUEL TYPE'] == 'COAL':
        coal_out_list[start_row:end_row+1, cty_ind] += out_mw
        coal_out_list[start_row:end_row+1, county_num + cty_ind] += ttl_mw    
    elif row['FUEL TYPE'] == 'SOLAR':
        pv_out_list[start_row:end_row+1, cty_ind] += out_mw
        pv_out_list[start_row:end_row+1, county_num + cty_ind] += ttl_mw
    else:
        pass
np.seterr(divide='ignore', invalid='ignore')
ng_derate_fac = np.divide(ng_derate_cap, ng_derate_ttl)
ng_derate_fac[np.isnan(ng_derate_fac)] = 1
# save data
##ng_out_df = pd.DataFrame(ng_out_list)
##ng_out_df.columns = county_list * 2
##ng_out_df['UTC'] = date_list
##ng_out_df = ng_out_df.set_index('UTC')
##ng_out_df.to_csv('ng_outage.csv')
##
##coal_out_df = pd.DataFrame(coal_out_list)
##coal_out_df.columns = county_list * 2
##coal_out_df['UTC'] = date_list
##coal_out_df = coal_out_df.set_index('UTC')
##coal_out_df.to_csv('coal_outage.csv')
##
##pv_out_df = pd.DataFrame(pv_out_list)
##pv_out_df.columns = county_list * 2
##pv_out_df['UTC'] = date_list
##pv_out_df = pv_out_df.set_index('UTC')
##pv_out_df.to_csv('pv_outage.csv')
ng_derate_df = pd.DataFrame(ng_derate_fac)
ng_derate_df.columns = county_list
ng_derate_df['UTC'] = date_list
ng_derate_df = ng_derate_df.set_index('UTC')
ng_derate_df.to_csv('ng_derate_fac.csv')
