# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 19:38:36 2024

@author: SuMLiGhT
"""

import numpy as np
import pandas as pd
import pypower.api as pypower
from pypower.idx_bus import PD, VM, VA
from pypower.idx_gen import PG, GEN_BUS, PMAX, PMIN
from pypower.idx_brch import PF, PT, F_BUS, T_BUS, RATE_A
import matplotlib.pyplot as plt


# Function to load and process each CSV file
def process_file(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Standardize headers
    df.columns = df.columns.str.lower()
    
    # Convert time to datetime format
    df['time'] = pd.to_datetime(df['time'])
    
    # Set time as index
    df.set_index('time', inplace=True)
    
    # Resample to 15-minute intervals and interpolate
    df = df.resample('15T').interpolate()
    
    return df

# Load and process each file
wind_data = process_file('wind_data.csv')
solar_data = process_file('solar_data.csv')
ercot_load = process_file('ERCOT_Load.csv')

# Combine all data into a single DataFrame
combined_df = wind_data.join(solar_data, how='outer').join(ercot_load, how='outer')

# Normalize each column by its maximum value
for column in combined_df.columns:
    combined_df[column] = combined_df[column] / combined_df[column].max()

# Reset index to have time as a column
combined_df.reset_index(inplace=True)

# Assuming combined_df is already defined
combined_df_copy = combined_df.head(10).copy()

# Load PyPower case
mpc = pypower.case24_ieee_rts()

# Node 1 is typically indexed as 0 in Python (assuming bus numbering starts from 1)
node = 1  # adjust if your numbering is different

# Wind and solar generator bus IDs
wind_gen_buses = [18, 21, 22]
solar_gen_buses = [2, 3]
diesel_gen_buses = [1]

# Define the branch pairs for which you want to find the indices
branch_pairs = [(24, 3), (11, 9), (11, 10), (12, 9), (12, 10)]

# Find the indices of these branches in the mpc['branch'] array
branch_indices = {}
for from_bus, to_bus in branch_pairs:
    for idx, branch in enumerate(mpc['branch']):
        if (branch[F_BUS] == from_bus and branch[T_BUS] == to_bus) or \
           (branch[F_BUS] == to_bus and branch[T_BUS] == from_bus):
            branch_indices[f'{from_bus}-{to_bus}'] = idx
            break


# Initialize the number of buses, generators, and branches
num_buses = mpc['bus'].shape[0]
num_gens = mpc['gen'].shape[0]
num_branches = mpc['branch'].shape[0]

# Prepare empty arrays to store the new data
bus_vm_data = np.zeros((len(combined_df_copy), num_buses))
bus_va_data = np.zeros((len(combined_df_copy), num_buses))
bus_pd_data = np.zeros((len(combined_df_copy), num_buses))
gen_pg_data = np.zeros((len(combined_df_copy), num_gens))
branch_pf_data = np.zeros((len(combined_df_copy), num_branches))
branch_pt_data = np.zeros((len(combined_df_copy), num_branches))


# Initialize a list to store the convergence status
convergence_status = []

# Loop over each time point in combined_df_copy
for index, row in combined_df_copy.iterrows():
    # Reload PyPower case for each iteration
    mpc = pypower.case24_ieee_rts()

    # Get multipliers
    ercot_multiplier = row['ercot']
    wind_multiplier = row['wind']
    solar_multiplier = row['solar']

    # Modify load at each bus
    for i in range(num_buses):
        mpc['bus'][i, PD] *= ercot_multiplier
        
    # Loop over all branches in the case
    for idx, branch in enumerate(mpc['branch']):
        if branch[F_BUS] == node or branch[T_BUS] == node:
            # Branch is connected to node 1
            # Increase RATE_A (maximum power flow limit) by 2 times
            mpc['branch'][idx, RATE_A] *= 2

    # Loop over each generator in the case
    for gen_idx in range(num_gens):
        gen_bus = mpc['gen'][gen_idx, GEN_BUS]
    
        if gen_bus in wind_gen_buses:
            # Adjust the maximum generation limit for wind generators
            mpc['gen'][gen_idx, PMAX] = mpc['gen'][gen_idx, PMAX] * wind_multiplier
            mpc['gen'][gen_idx, PMIN] = mpc['gen'][gen_idx, PMIN] * 0
            # # Update actual generation if necessary
            mpc['gen'][gen_idx, PG] = min(mpc['gen'][gen_idx, PG], mpc['gen'][gen_idx, PMAX])
    
        elif gen_bus in solar_gen_buses:
            # Adjust the maximum generation limit for solar generators
            mpc['gen'][gen_idx, PMAX] = mpc['gen'][gen_idx, PMAX] * solar_multiplier
            mpc['gen'][gen_idx, PMIN] = mpc['gen'][gen_idx, PMIN] * 0
            # # Update actual generation if necessary
            mpc['gen'][gen_idx, PG] = min(mpc['gen'][gen_idx, PG], mpc['gen'][gen_idx, PMAX])
            
        elif gen_bus in diesel_gen_buses:
            # Adjust the maximum generation limit for solar generators
            mpc['gen'][gen_idx, PMAX] = mpc['gen'][gen_idx, PMAX] * 5
            # # Update actual generation if necessary
            # mpc['gen'][gen_idx, PG] = min(mpc['gen'][gen_idx, PG], mpc['gen'][gen_idx, PMAX])


    # Identify the indices of wind and solar generators in the mpc['gen'] array
    wind_gen_indices = [i for i, gen in enumerate(mpc['gen']) if gen[GEN_BUS] in wind_gen_buses]
    solar_gen_indices = [i for i, gen in enumerate(mpc['gen']) if gen[GEN_BUS] in solar_gen_buses]
    diesel_gen_indices = [i for i, gen in enumerate(mpc['gen']) if gen[GEN_BUS] in diesel_gen_buses]
    
    # Set the cost components of wind and solar generators to zero
    for idx in wind_gen_indices + solar_gen_indices:
        # Assuming a polynomial cost function, set all cost coefficients to zero
        mpc['gencost'][idx, 4:] = 0  # Adjust the index 4 according to your cost function structure
        
    # Set the cost components of diesel generators to heighest
    for idx in diesel_gen_indices:
        # Assuming a polynomial cost function, set all cost coefficients to custom value
        mpc['gencost'][idx, 4] = 0.5  # Adjust the index 4 according to your cost function structure
        mpc['gencost'][idx, 5] = 130  # Adjust the index 4 according to your cost function structure
        mpc['gencost'][idx, 6] = 400  # Adjust the index 4 according to your cost function structure

    # Run optimal power flow
    results = pypower.runopf(mpc)
    
    # Extract the convergence status (True if OPF converged, False otherwise)
    converged = results['success']
    convergence_status.append(converged)

    # Extract required data
    bus_vm_data[index, :] = results['bus'][:, VM]
    bus_va_data[index, :] = results['bus'][:, VA]
    bus_pd_data[index, :] = mpc['bus'][:, PD]
    gen_pg_data[index, :] = results['gen'][:, PG]
    branch_pf_data[index, :] = results['branch'][:, PF]
    branch_pt_data[index, :] = results['branch'][:, PT]

# Create new DataFrames from the collected data
bus_vm_df = pd.DataFrame(bus_vm_data, columns=[f'bus_{i+1}_VM' for i in range(num_buses)])
bus_va_df = pd.DataFrame(bus_va_data, columns=[f'bus_{i+1}_VA' for i in range(num_buses)])
bus_pd_df = pd.DataFrame(bus_pd_data, columns=[f'bus_{i+1}_PD' for i in range(num_buses)])
gen_pg_df = pd.DataFrame(gen_pg_data, columns=[f'gen_{i+1}_PG' for i in range(num_gens)])
branch_pf_df = pd.DataFrame(branch_pf_data, columns=[f'branch_{i+1}_PF' for i in range(num_branches)])
branch_pt_df = pd.DataFrame(branch_pt_data, columns=[f'branch_{i+1}_PT' for i in range(num_branches)])

# Concatenate the new data with the original DataFrame
combined_df_copy = pd.concat([combined_df_copy, bus_vm_df, bus_va_df, bus_pd_df, gen_pg_df, branch_pf_df, branch_pt_df], axis=1)

# # Save to a file (CSV format)
# combined_df_copy.to_csv('power_system_data.csv', index=False)

# # Make a copy of the DataFrame
# formatted_df = combined_df_copy.copy()

# # Format the columns
# for column in formatted_df.columns:
#     if column.startswith('bus_'):
#         # For voltage (VM) and bus angle (VA) columns, limit to two decimal points
#         if column.endswith('_VM') or column.endswith('_VA'):
#             formatted_df[column] = formatted_df[column].round(2)
#         # For other bus columns, remove decimal points
#         else:
#             formatted_df[column] = formatted_df[column].round(0).astype(int)
#     elif column.startswith('gen_') or column.startswith('branch_'):
#         # For generator and branch columns, remove decimal points
#         formatted_df[column] = formatted_df[column].round(0).astype(int)

# # Save the formatted DataFrame to a CSV file
# formatted_df.to_csv('formatted_power_system_data.csv', index=False)

# Create a DataFrame for convergence status
convergence_df = pd.DataFrame({'convergence_status': convergence_status}, index=combined_df_copy.index)


#################################################################################
# Normalize the specified columns with respect to their maximum values
columns_to_plot = ['ercot', 'bus_1_PD', 'wind', 'gen_23_PG', 'solar', 'gen_1_PG', 'gen_12_PG']
for column in columns_to_plot:
    combined_df_copy[column] = combined_df_copy[column] / combined_df_copy[column].max()

# Plotting
plt.figure(figsize=(12, 5))
for column in columns_to_plot:
    plt.plot(combined_df_copy['time'], combined_df_copy[column], label=column)

plt.title('Normalized Plot of Various Power System Parameters')
plt.xlabel('Time Index')
plt.ylabel('Normalized Value')
plt.legend()
plt.show()

# # Filter columns that start with 'gen_'
# gen_columns = [col for col in combined_df_copy.columns if col.startswith('gen_')]

# # Normalize these columns
# for col in gen_columns:
#     combined_df_copy[col] = combined_df_copy[col] / combined_df_copy[col].max()

# # Plotting
# plt.figure(figsize=(15, 8))
# for col in gen_columns:
#     plt.plot(combined_df_copy['time'], combined_df_copy[col], label=col)

# plt.title('Normalized Output of Generators')
# plt.xlabel('Time Index')
# plt.ylabel('Normalized Generator Output')
# plt.legend()
# plt.show()

# Plotting inter-area line flows
plt.figure(figsize=(12, 6))
for branch, idx in branch_indices.items():
    plt.plot(combined_df_copy['time'], combined_df_copy[f'branch_{idx+1}_PF'], label=branch)

plt.title('Line Flows for Inter-Area Branches')
plt.xlabel('Time')
plt.ylabel('Active Power Flow (MW)')
plt.legend()
plt.show()


## Mapping dictionary
generator_mapping = {
    f'gen_{i+1}': {'PG': f'gen_{i+1}_PG', 'bus': int(gen[0])}
    for i, gen in enumerate(mpc['gen'])
}

branch_mapping = {
    f'branch_{i+1}': {
        'from_bus': int(branch[0]),
        'to_bus': int(branch[1]),
        'PF': f'branch_{i+1}_PF',
        'PT': f'branch_{i+1}_PT'
    }
    for i, branch in enumerate(mpc['branch'])
}

bus_mapping = {
    f'bus_{int(bus[0])}': {'VM': f'bus_{int(bus[0])}_VM', 'VA': f'bus_{int(bus[0])}_VA', 'PD': f'bus_{int(bus[0])}_PD', 'bus': int(bus[0])}
    for bus in mpc['bus']
}

# Extract bus, generator, and branch data
bus_data = mpc['bus']
gen_data = mpc['gen']
branch_data = mpc['branch']

buses = {
    int(bus[0]): {
        'type': int(bus[1]), 'Pd': round(float(bus[2]), 2), 'Qd': round(float(bus[3]), 2),
        'area': int(bus[6]), 'Vm': round(float(bus[7]), 2), 'Va': round(float(bus[8]), 2),  
        'zone': int(bus[10]), 'VA': f'bus_{int(bus[0])}_VA', 'PD': f'bus_{int(bus[0])}_PD'
    } 
    for bus in bus_data
}

generators = {
    idx: {
        'bus': int(gen[0]), 'Pg': round(float(gen[1]), 2), 'Qg': round(float(gen[2]), 2),
        'status': int(gen[7]), 'Pmax': round(float(gen[8]), 2), 'Pmin': round(float(gen[9]), 2), 'PG': f'gen_{idx}_PG'
    } 
    for idx, gen in enumerate(gen_data, start=1)
}

branches = {
    (int(branch[0]), int(branch[1])): {
        'x': round(float(branch[3]), 2), 'rateA': round(float(branch[5]), 2),
        'ratio': round(float(branch[8]), 2), 'angle': round(float(branch[9]), 2),
        'status': int(branch[10]), 'from_bus': int(branch[0]),
        'to_bus': int(branch[1]),
        'PF': f'branch_{idx+1}_PF',  # Ensure 'idx' is defined correctly in your loop
        'PT': f'branch_{idx+1}_PT'
    } 
    for idx, branch in enumerate(branch_data, start=1)  # Assuming 'idx' is defined in your loop context
}


import json

def store_dictionaries_json(bus_data, gen_data, branch_data):
    buses = {
        int(bus[0]): {
            'type': int(bus[1]), 'Pd': round(float(bus[2]), 2), 'Qd': round(float(bus[3]), 2),
            'area': int(bus[6]), 'Vm': round(float(bus[7]), 2), 'Va': round(float(bus[8]), 2),  
            'zone': int(bus[10]), 'VA': f'bus_{int(bus[0])}_VA', 'PD': f'bus_{int(bus[0])}_PD'
        } 
        for bus in bus_data
    }

    generators = {
        idx: {
            'bus': int(gen[0]), 'Pg': round(float(gen[1]), 2), 'Qg': round(float(gen[2]), 2),
            'status': int(gen[7]), 'Pmax': round(float(gen[8]), 2), 'Pmin': round(float(gen[9]), 2), 'PG': f'gen_{idx}_PG'
        } 
        for idx, gen in enumerate(gen_data, start=1)
    }

    branches = {
        idx: {  # Convert tuple keys to string format
            'x': round(float(branch[3]), 2), 'rateA': round(float(branch[5]), 2),
            'ratio': round(float(branch[8]), 2), 'angle': round(float(branch[9]), 2),
            'status': int(branch[10]), 'from_bus': int(branch[0]),
            'to_bus': int(branch[1]),
            'PF': f'branch_{idx+1}_PF', 'PT': f'branch_{idx+1}_PT'
        } 
        for idx, branch in enumerate(branch_data, start=1)
    }

    # Storing the dictionaries into JSON files with proper handling for JSON format
    with open('buses_dict.json', 'w') as f:
        json.dump(buses, f, indent=4)

    with open('generators_dict.json', 'w') as f:
        json.dump(generators, f, indent=4)

    with open('branches_dict.json', 'w') as f:
        json.dump(branches, f, indent=4)

    print("Dictionaries stored successfully in JSON format.")

store_dictionaries_json(bus_data, gen_data, branch_data)