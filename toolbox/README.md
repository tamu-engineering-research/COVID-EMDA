# CoVEMDA

This is the home page of an open-access toolbox: **CoVEMDA** (CoronaVirus - Electricity Market Data Analyzer). The root path contains this introductory document, a copy of the user manul, and a zip file containing all the toolbox source codes.
 

## Features
 
Based on COVID-EMDA+ data hub, CoVEMDA is designed for functionalities including:

- Baseline Estimation
- Regression Analysis
- Scientific Visualization

As well as other useful supplementary functions.


## Navigation

CoVEMDA root directory contains four folders and two `.m` files (apart from `README.md`). The two MATLAB scripts are `install.m` and `uninstall.m`, for installation and uninstallation of the toolbox. To install or uninstall CoVEMDA, just run these two scripts in your MATLAB console.

Folder `lib/` contains the essential scripts for CoVEMDA, including feature-oriented high-level functions (`lib/high_level/`) and function-oriented auxiliary low-level and basic functions (`lib/low_level` and `lib/basic_operations`). It is recommended to call the **high-level functions**, as they are integrated and simple to use.

Folder `docs/` contains the **User Manual** for CoVEMDA. The manual includes simple guidance for first-time users, as well as detailed explanation of all the features and functions, along with illustrative examples. It is recommended to read the entire manual to use the toolbox properly. However, merely reading **Section 2 (Getting Started)** is enough for a beginner to try it out.

Folder `examples/` contains the examples and sample code mentioned in the User Manual. All the example scripts are executable, with explanatory comments for each step.

Folder `data/` contains the temporary files of CoVEMDA, including data files downloaded from COVID-EMDA+ data hub (`data/COVID-EMDA+/`) and saved backcast models of different markets (`data/backcast`).


## User Manual

A detailed **User Manual** is attached to the toolbox, which can be found at `docs/`. In this manual, you will find a basic guidance for beginners as well as comprehensive details of the toolbox implementation. We highly recommend you to read this part (Section 1 and 2) before using CoVEMDA. The rest of the manual introduces all the features and functions from principle to practice in detail. You can refer to Section 5, 6, and 7 for advanced usage and customization. The sections of the manual are listed below:

1. Introduction
2. **Getting Started**
3. Data Hub
4. Baseline Estimation
5. Regression Analysis
6. Scientific Visualization
7. Acknowledgments
