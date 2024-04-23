# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 21:23:33 2024

@author: SuMLiGhT
"""

import os
import ast
import astunparse
import pandas as pd
from zss import Node, simple_distance
import numpy as np
import matplotlib.pyplot as plt

directory = "Code3-Data"
file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]

def load_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    return code

def ast_to_tree(node):
    """ Convert an ast node to a tree structure understandable by zss. """
    if isinstance(node, ast.AST):
        node_label = type(node).__name__
        children = [ast_to_tree(child) for child in ast.iter_child_nodes(node)]
        return Node(label=node_label, children=children)
    return None

def calculate_similarity(ast1, ast2):
    tree1 = ast_to_tree(ast1)
    tree2 = ast_to_tree(ast2)
    return simple_distance(tree1, tree2)

# Load and parse code into ASTs
asts = {}
for file_path in file_paths:
    code = load_code(file_path)
    asts[file_path] = ast.parse(code)

# Calculate similarity scores and store in a list
results = []
for i, (path1, ast1) in enumerate(asts.items()):
    for path2, ast2 in list(asts.items())[i+1:]:
        similarity_score = calculate_similarity(ast1, ast2)
        results.append([path1, path2, similarity_score])

# Convert results to DataFrame and save as CSV
df = pd.DataFrame(results, columns=['File1', 'File2', 'Similarity'])
df.to_csv('ast_code_similarity_scores.csv', index=False)

print("AST-based similarity scores saved to ast_code_similarity_scores.csv")


import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('ast_code_similarity_scores.csv')

# Extract similarity scores
similarity_scores = df['Similarity'].values

# Calculate weights for each score to convert counts to percentages
weights = (np.ones_like(similarity_scores) / len(similarity_scores)) * 100  # Convert to percentage

# Plotting the histogram of scores
plt.figure(figsize=(5, 5))
plt.hist(similarity_scores, bins=20, color='blue', alpha=0.7, weights=weights)

plt.xlabel('Score')
plt.ylabel('Percentage (%)')
plt.grid(True)
plt.show()

