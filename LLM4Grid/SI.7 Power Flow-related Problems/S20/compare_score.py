# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 10:54:17 2024

@author: SuMLiGhT
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import itertools
from comet import download_model, load_from_checkpoint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def main(directory):
    model_path = download_model("wmt21-cometinho-da")
    model = load_from_checkpoint(model_path)
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    combinations = list(itertools.combinations(files, 2))
    scores = []
    file_pairs = []

    for file1, file2 in combinations:
        src_text = read_text_file(file1)
        mt_text = read_text_file(file2)
        ref_text = mt_text  # Using the second file as a reference to the first
        data = [{'src': src_text, 'mt': mt_text, 'ref': ref_text}]
        output = model.predict(data)
        
        if 'scores' in output:
            score = output['scores'][0]
            print(f"Score for {file1} vs {file2}: {score}")  # Debug output
            scores.append(score)
            file_pairs.append((file1, file2))
        else:
            print("Expected 'scores' key not found in output:", output)

    score_data = pd.DataFrame({
        'file_pair': file_pairs,
        'score': scores
    })

    # Clipping scores to be between 0 and 1
    score_data['score_clipped'] = score_data['score'].clip(0, 1)

    # Save to CSV
    csv_path = os.path.join(directory, 'scores_clipped.csv')
    score_data.to_csv(csv_path, index=False)
    print(f"Clipped scores saved to {csv_path}")


# Function call
directory = 'Prompt-generated-text'  # Update this path to your data directory
main(directory)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_scores(csv_path):
    # Set global font size
    plt.rcParams.update({'font.size': 14})
    
    # Read scores from CSV
    data = pd.read_csv(csv_path)
    scores_np = data['score_clipped'].values
    
    # Calculate weights for each score to convert counts to percentages
    weights = (np.ones_like(scores_np) / len(scores_np)) * 100  # Convert to percentage

    # Plotting the histogram of scores
    plt.figure(figsize=(5, 5))
    plt.hist(scores_np, bins=20, color='blue', alpha=0.7, weights=weights)
    plt.xlabel('Score')
    plt.ylabel('Percentage (%)')
    plt.grid(True)
    plt.show()

# Function call
directory = 'Prompt-generated-text'  # Update this path to your data directory

# Plotting outside of the main function
csv_path = os.path.join(directory, 'scores_clipped.csv')
plot_scores(csv_path)
