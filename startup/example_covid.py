import EMDA_Utilities as utils
import os
import numpy as np
import matplotlib.pyplot as plt

# switch to root directory
os.chdir("../")

# Path to the data to be imported
csv_path = "data_release/caiso/caiso_rto_covid.csv"

# read RTO-wide LMP data for CAISO using provided utility script
[dates, data] = utils.read_covid(csv_path)

# plot the curve of daily new confirmed case and deaths in CAISO
new_cases = data['new_confirm']
new_deaths = data['new_death']
num_dates = len(dates)
# set ticks and labels in x axis
xticks = [0, int(num_dates/4), int(num_dates/2), int(num_dates*3/4), num_dates-1]
xlabels = [dates[i] for i in xticks]

# plot daily confirmed cases
plt.plot(range(num_dates),new_cases)
plt.xticks(xticks,xlabels)
plt.title('Daily New Confirmed Cases in CAISO')
plt.show()

# plot daily confirmed deaths
plt.plot(range(num_dates),new_deaths)
plt.xticks(xticks,xlabels)
plt.title('Daily New Confirmed Deaths in CAISO')
plt.show()
