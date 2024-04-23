# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 22:22:18 2024

@author: SuMLiGhT
"""

import pandas as pd
import os
from dateutil import parser
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.tsa.stattools import adfuller

    
def plot_variance_over_time(data, column_name, window_size_days, region, year):
    data = data[['time', column_name]].dropna()
    data['time'] = pd.to_datetime(data['time'])
    data.set_index('time', inplace=True)
    
    # Calculate rolling variance and mean
    rolling_variance = data[column_name].rolling(f'{window_size_days}D').var()
    rolling_mean = data[column_name].rolling(f'{window_size_days}D').mean()

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(rolling_variance, label='Rolling Variance')
    plt.plot(rolling_mean, label='Rolling Mean')
    plt.title(f'Rolling Variance and Mean for {column_name} in {region}, {year}')
    plt.legend()
    plt.show()

    # Heteroskedasticity Test
    y = data[column_name]
    X = sm.add_constant(data.index.to_julian_date().values.reshape(-1, 1))
    white_test = het_breuschpagan(y, X)
    Desx = "Heteroskedastic" if white_test[1] < 0.05 else "Homoskedastic"
    print(f"White's Test: {Desx}, p-value: {white_test[1]}")
    
def find_nan(dataframe):
    nan_locations = dataframe.isna().stack()
    nan_locations = nan_locations[nan_locations]
    if not nan_locations.empty:
        print(f"NaN values found at: \n{nan_locations}")
        
def test_station(data, column, time_col, year, i, region):
    """
    Removes outliers, applies log transformation, and performs a stationarity test.
    :param data: DataFrame containing the dataset.
    :param column: The column name containing the data to test.
    :param time_col: The time column for independent variable.
    :return: String indicating if data is heteroskedastic or homoskedastic.
    """
    # Perform the Augmented Dickey-Fuller test
    adf_test = adfuller(data[column], autolag='AIC')
    
    print("ADF Statistic: %f" % adf_test[0])
    print("p-value: %f" % adf_test[1])
    print("Critical Values:")
    for key, value in adf_test[4].items():
        print(f"\t{key}: {value}")
    
    p_value = adf_test[1]
    return "Stat" if p_value < 0.05 else "Non-Stat"
    
def parse_dates(date):
    try:
        return pd.to_datetime(date)
    except ValueError:
        return parser.parse(date)
    
# Normalization function
def normalize_column(column):
    min_val = column.min()
    max_val = column.max()
    normalized = (column - min_val) / (max_val - min_val)
    return normalized


def load_region_data(region, directory_path):
    # Define file paths
    ercot_load_file = os.path.join(directory_path, 'ERCOT_Load.csv')
    weather_file = os.path.join(directory_path, 'merged_weather_data.csv')
    rtm_lz_file = os.path.join(directory_path, 'RTM_LZ.csv')

    # Load data
    # solar_df = pd.read_csv(solar_data_file)
    ercot_df = pd.read_csv(ercot_load_file)
    temp_df = pd.read_csv(weather_file, usecols=['time', 'TEMPF_KTXCOPPE3'])
    rtm_df = pd.read_csv(rtm_lz_file, usecols=['time', 'rtm_lz_south'])
    
    # Convert 'time' to datetime format for all dataframes
    dataframes = [rtm_df, ercot_df, temp_df]
    for df in dataframes:
        df['time'] = df['time'].apply(parse_dates)

    # Merge all dataframes except normalized_df
    merged_df = pd.merge(ercot_df, temp_df, on='time', how='outer')
    merged_df = pd.merge(merged_df, rtm_df, on='time', how='outer')

    # Convert column names to lowercase
    merged_df.columns = merged_df.columns.str.lower()
    
    merged_df = merged_df.dropna()

    return merged_df

# Function to replace values in specified columns with their first two digits
def replace_with_data(df, columns, region):
    for col in columns:
        # Ensuring the column exists in the dataframe
        if col in ['ercot']:
            # Applying the transformation to each element in the column
            df.loc[:, col] = df[col].apply(lambda x: int(x/1000))
        # Ensuring the column exists in the dataframe
        elif col in ['tempf_ktxcoppe3']:
            # Applying the transformation to each element in the column
            df.loc[:, col] = df[col].apply(lambda x: int(float(str(x))))
            # df.loc[:, col] = df[col].apply(lambda x: int(str(x)[:2]))
        # Ensuring the column exists in the dataframe
        elif col in ['rtm_lz_south\n']:
            # Applying the transformation to each element in the column
            df.loc[:, col] = df[col].apply(lambda x: int(transform_value(x)))
    return df

# Define a function that applies the desired transformation, including handling for zero values
def transform_value(x):
    if abs(x) <= 5:
        if x >= 0:
            return int(1000/5)
        else:
            return -int(1000/5)
    else:
        return int(1000/x) if x != 0 else int(1000/5)

def digit_to_letter(value):
    mapping = {i: chr(65 + i) for i in range(26)}
    is_negative = value < 0
    value = abs(int(value))  # Convert to integer to discard decimal part, then to positive
    letter_representation = ''.join(mapping[int(digit)] for digit in str(value) if digit.isdigit())

    if is_negative:
        letter_representation = 'N' + letter_representation

    return letter_representation

# Function to extract and format data for each day
def format_data_for_days(df,day_from,day_to):
    formatted_data = ""
    for day in range(day_from,day_to):  # Considering first 3 days
        day_data = df[df['date'] == day]
        
        # Convert and extract data
        temp_data = [digit_to_letter(item) for item in day_data['tempf_ktxcoppe3']]
        ercot_data = [digit_to_letter(item) for item in day_data['ercot']]
        price_data = [digit_to_letter(item) for item in day_data['rtm_lz_south\n']]
        
        # Formatting the data without brackets and quotes
        formatted_temp = ' '.join(temp_data)
        formatted_ercot = ' '.join(ercot_data)
        formatted_price = ' '.join(price_data)

        formatted_data += f"Person 1: {formatted_temp}"
        formatted_data += f"Person 2: {formatted_ercot}"
        formatted_data += f"Person 3: {formatted_price}"

    return formatted_data


################################################################################
# Load the CSV data into a DataFrame
# Define the folder containing the CSV files
folder_path_source = 'data'  # Replace with the actual path to your folder
folder_path_analysis = 'Analysis Data'  # Replace with the actual path to your folder

regions = {'north', 'south', 'west'}  # Replace with 'south' or 'west' as needed

region = 'south'
# for region in regions:
df = pd.read_csv('../Embedding_input_peak.csv')
# df_transformed = transform_data(df, region)
df_transformed = df.copy()
df_transformed['time'] = pd.to_datetime(df_transformed['time'])
start_date = pd.Timestamp('2021-01-01')
df_transformed['date'] = (df_transformed['time'] - start_date).dt.days + 1

day_from = 27
day_to = 46
df_first_few_days = df_transformed[(df_transformed['date'] >= day_from) & (df_transformed['date'] <= day_to)]
df_first_few_days = replace_with_data(df_first_few_days, ['ercot', 'tempf_ktxcoppe3', 'rtm_lz_south\n'], region)

formatted_text = format_data_for_days(df_first_few_days,day_from, day_to)

# Writing the formatted text to a file
file_path = '../load_query_peak_day1.txt'
with open(file_path, 'w') as file:
    file.write(formatted_text)


# Display the first few rows of the dataframe with new columns
print(df_first_few_days.head())
