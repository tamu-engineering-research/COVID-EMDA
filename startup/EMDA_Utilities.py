import pandas as pd
import numpy as np
import os, csv
import matplotlib.pyplot as plt

# returns:
# dates -- vector of length N = number of rows in dataset
# data -- numpy array of size (N, 24) containin the hourly data for each date
def read_load_lmp(path):
    with open(path, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        # skip firstline
        first = 1
        # number of date
        rowNum = sum(1 for row in reader) - 1
        csvfile.seek(0, 0)
        # allocate
        dates = [None] * rowNum 
        data = np.zeros((rowNum, 24))
        ind = 0
        for row in reader:
            if first:
                first = 0
                continue
            data[ind,:] = row[1:]
            dates[ind] = row[0]
            ind = ind + 1

    return dates, data
     
# returns:
# dates -- vector of length N = number of rows in dataset
# data -- a dictionary obeject containing 5 vectors for each type of data
# The keys are:
#   'accum_confirm' -- Accumulated confirmed cases at each day
#   'new_confirm' -- New confirmed cases of each day
#   'infect_rate'-- Infection rate calculated at each date
#   'accum_death' -- Accumulated confirmed deaths at each day
#   'new_death' -- New confirmed deaths of each day
#   'fatal_rate'-- Fatal rate calculated at each date
def read_covid(path):
    with open(path, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        # skip firstline
        first = 1
        # number of date
        rowNum = sum(1 for row in reader) - 1
        csvfile.seek(0, 0)
        # allocate
        dates = [None] * rowNum 
        accum_confirm = np.zeros(rowNum)
        new_confirm = np.zeros(rowNum)
        infect_rate = np.zeros(rowNum)
        accum_death = np.zeros(rowNum)
        new_death = np.zeros(rowNum)
        fatal_rate = np.zeros(rowNum)
        ind = 0
        for row in reader:
            if first:
                first = 0
                continue
            dates[ind] = row[0]
            accum_confirm[ind] = row[1]
            new_confirm[ind] = row[2]
            infect_rate[ind] = row[3]
            accum_death[ind] = row[4]
            new_death[ind] = row[5]
            fatal_rate[ind] = row[6]
            ind = ind + 1

        data = {'accum_confirm':accum_confirm,
            'new_confirm': new_confirm,
            'infect_rate': infect_rate,
            'accum_death': accum_death,
            'new_death': new_death,
            'fatal_rate': fatal_rate}
    
    return dates, data



# returns:
# dates -- vector of length N = number of rows in dataset containing dates
# types -- vector of length N = number of rows in dataset containing fuel types
# data -- numpy array of size (N, 24) containin the hourly data for each date
def read_genmix(path):
    with open(path, newline = '') as csvfile:
        handle = csv.reader(csvfile, delimiter = ',')
        # skip firstline
        first = 1
        # number of date
        rowNum = sum(1 for row in handle) - 1
        csvfile.seek(0, 0)
        # allocate data containers
        dates = [None] * rowNum 
        types = [None] * rowNum 
        data = np.zeros((rowNum, 24))
        ind = 0
        for row in handle:
            if first:
                first = 0
                continue
            dates[ind] = row[0]
            types[ind] = row[1]
            data[ind,:] = row[2:]
            ind = ind + 1
            
    return dates, types, data



# returns:
# dates -- vector of length N = number of rows in dataset containing dates
# types -- vector of length N = number of rows in dataset containing type of measurement
# data -- numpy array of size (N, 24) containin the hourly data for each date
def read_weather(path):
    with open(path, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        # skip firstline
        first = 1
        # number of date
        rowNum = sum(1 for row in reader) - 1
        csvfile.seek(0, 0)
        # allocate
        dates = [None] * rowNum
        types = [None] * rowNum 
        data = np.zeros((rowNum, 24))
        ind = 0
        for row in reader:
            if first:
                first = 0
                continue
            dates[ind] = row[0]
            types[ind] = row[1]
            data[ind,:] = row[2:]
            ind = ind + 1
            

    return dates, types, data
