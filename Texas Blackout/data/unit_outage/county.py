import pandas as pd
import pickle
from scipy.io import loadmat
import texas_powerflow
import requests, json

# https://geo.fcc.gov/api/census/
case_mat_filepath = '../../bte2k/case_Mar3_5pm.mat'
case = loadmat(case_mat_filepath, squeeze_me=True, struct_as_record=False)
branch, bus, plant = texas_powerflow.get_dataframes_from_mpc(case["mpc"])

gen_buses = bus.loc[plant['bus_id']]
gen_num = gen_buses.shape[0]
gen_lat = gen_buses['lat'].tolist()
gen_lon = gen_buses['lon'].tolist()
gen_county = []

for i in range(gen_num):
    lat = str(gen_lat[i])
    lon = str(gen_lon[i])
    url_i = "https://geo.fcc.gov/api/census/block/find?latitude="+lat+"&longitude="+lon+"&format=json"

    response = requests.get(url_i)
    county = response.json()
    county = county['County']['name']
    gen_county.append(county)


gen_county = pd.Series(gen_county)
pickle.dump(gen_county, open('gen_county.pkl',"wb"))
gen_county.to_csv('gen_county.csv')
