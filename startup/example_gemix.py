import EMDA_Utilities as utils
import os
import numpy as np
import matplotlib.pyplot as plt

# switch to root directory
os.chdir("../")

# Path to the data to be imported
csv_path = "data_release/caiso/caiso_rto_genmix.csv"

# read RTO-wide LMP data for CAISO using provided utility script
[dates, types, data] = utils.read_genmix(csv_path)

# findout what are the type of fuels in this RTO
fuel_types = list(set(types))
print("The type of fuels are:")
print(fuel_types)
num_fuel_type = len(fuel_types)
# count the capacity of each type of fuel
gen_ct = [0] * num_fuel_type

# solar capacity of each day
solar_output = []

# iterate through each entry to aggregate data
for i in range(len(dates)):
    # fuel type of this entry
    gen_type = types[i]
    type_ind = fuel_types.index(gen_type)
    # mean of capacity of that day for that fuel type
    gen_capacity = np.sum(data[i,:])
    gen_ct[type_ind] += gen_capacity

    # check if fuel is solar, if yes then append to solar container
    if gen_type == 'solar':
        solar_output.append(gen_capacity)

# draw a bar plot of each type of fuel 
plt.bar(fuel_types,gen_ct)
plt.title('Annual Capacity of Each Fuel Type in CAISO')
plt.show()

# plot the trend of solar energy over this entire dataset
plt.plot(solar_output)
plt.title('Daily Output of Solar in CAISO')
plt.show()
