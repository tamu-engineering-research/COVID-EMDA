# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 21:23:33 2024

@author: SuMLiGhT
"""

import os
import ast
import pandas as pd
from zss import Node, simple_distance
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

directory = "Problemsolving-DCPOwerFlow-Prompt"

def load_and_parse_ast(file_path):
    """Load and parse a Python file to an AST."""
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    return file_path, ast.parse(code)

def ast_to_tree(node, cache=None, max_depth=5, current_depth=0):
    """ Convert an ast node to a tree structure with limited depth, always returning a Node. """
    if cache is None:
        cache = {}
    if node in cache:
        return cache[node]

    if isinstance(node, ast.AST):
        node_label = type(node).__name__
        # Check if the current depth exceeds max depth and return a leaf node if so
        if current_depth >= max_depth:
            return Node(label=node_label)  # Return node with no children
        children = [ast_to_tree(child, cache, max_depth, current_depth + 1) for child in ast.iter_child_nodes(node)]
        tree_node = Node(label=node_label, children=children)
        cache[node] = tree_node
        return tree_node

    # Return a placeholder node if the input is not an AST node and no cache entry is found
    return Node(label='None')



def calculate_similarity(ast1, ast2):
    return simple_distance(ast_to_tree(ast1), ast_to_tree(ast2))

def parse_asts(directory):
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    asts = {}
    with ProcessPoolExecutor() as executor:
        # Wrap tqdm around map to show progress
        results = list(tqdm(executor.map(load_and_parse_ast, file_paths), total=len(file_paths)))
    for file_path, ast_node in results:
        asts[file_path] = ast_node
    return asts

def main(directory):
    asts = parse_asts(directory)
    results = []

    paths = list(asts.keys())
    # Add tqdm for progress tracking on comparison
    for i in tqdm(range(len(paths))):
        for j in range(i + 1, len(paths)):
            path1, path2 = paths[i], paths[j]
            similarity_score = calculate_similarity(asts[path1], asts[path2])
            results.append([path1, path2, similarity_score])

    df = pd.DataFrame(results, columns=['File1', 'File2', 'Similarity'])
    df.to_csv('ast_code_similarity_scores.csv', index=False)
    print("AST-based similarity scores saved to ast_code_similarity_scores.csv")

    plot_histogram(df['Similarity'].values)

def plot_histogram(similarity_scores):
    weights = np.ones_like(similarity_scores) / len(similarity_scores) * 100  # Convert to percentage
    plt.figure(figsize=(5, 5))
    plt.hist(similarity_scores, bins=20, color='blue', alpha=0.7, weights=weights)
    plt.xlabel('Score')
    plt.ylabel('Percentage (%)')
    # plt.title('Histogram of Similarity Scores')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main(directory)
