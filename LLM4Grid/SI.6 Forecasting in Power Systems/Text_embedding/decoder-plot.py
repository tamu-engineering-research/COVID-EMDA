# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:26:11 2024

@author: SuMLiGhT
"""

import numpy as np
import matplotlib.pyplot as plt

def letter_to_digit(letter):
    mapping = {chr(65 + i): i for i in range(26)}
    return mapping[letter]

def decode_string(input_string):
    # Extract the part after the colon
    # encoded_part = input_string.split(": ")[1]

    # Split the encoded part into encoded elements
    encoded_elements = input_string.split()

    decoded_numbers = []
    current_number = 0
    is_negative = False

    for element in encoded_elements:
        if element == 'N':  # If 'N' is found, set the next number as negative
            is_negative = True
        else:
            for char in element:
                current_number = current_number * 10 + letter_to_digit(char)

            if is_negative:
                current_number = -current_number  # Make the number negative
                is_negative = False  # Reset the flag for next numbers

            decoded_numbers.append(current_number)
            current_number = 0  # Reset for the next number

    return np.array(decoded_numbers)

input_strings = [
    "Person 3: FA EH EF EE ED ED EF EG EJ FC FG GB GE GH GI HA HC HC HA GH GF GD GA FH",
    "Person 3: CF CC CG CE CB CF CG CF CH CE CE CE CG CE CG CE CH CH CG CH CH CE CC CH",
    "Person 3: EJ EA EE EE EC EA DJ DH DJ DH CJ CI CI CI CH CH CJ DA DA DG DE DJ DC DH",
    "Person 3: EF EG FE FF FG FC FA EG EI EH DJ DB DD DB CH CH DB DA DC DB CH CG CJ DJ DA",
    "Person 3: FG FJ FI GF GC FE EF EE HF GC GB HD BFD CAA CAA FE BC DH FA EG DJ DH DG DI",
    "Person 3: EE EA EF EC EH EF EI EH EH EA DB CE CF CC CF CC CJ DC DE DG DD DD DE EA",
    "Person 3: DJ ED EF EH EI EJ EA EA DJ DC DH DH DE DC CI CH CJ DA DB DB DB DB DF",
    "Person 3: DB DE CAA CAA BCA BCF BBG DB FD FA FC EI DC DH EI DI EG DA CC CJ DH EA",
    # Add more strings as needed
]


# Convert each string to an array and store in a list
arrays = [decode_string(input_str) for input_str in input_strings]

# Converting the list to a numpy array
sample_array = np.array(arrays)

# Saving the numpy array as a txt file
output_file_path = '../load_text_temp.txt'
np.savetxt(output_file_path, sample_array, fmt='%d')

# Plotting
plt.figure(figsize=(10, 6))
for i, arr in enumerate(arrays):
    if i == 0:
        plt.plot(arr, label='Truth')
    elif i == 1:
        plt.plot(arr, label='Less data')
    elif i == 2:
        plt.plot(arr, label='More data')
    else:
        plt.plot(arr, label=f'More data {i-2}+')

plt.xlabel('Index')
plt.ylabel('Value')
plt.ylim([0,75])
plt.title('Price Forecast')
plt.legend()
plt.show()
