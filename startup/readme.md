# Start-up Examples and Utility Functions
This folder contains a script of Python APIs to parse .csv files in `data_release` folders into Python and Numpy arrays. Two examples are provided to demonstrate the usage of the .csv files and utility functions


## EMDA_Utilities.py
- This script contains 4 APIS to handle .csv files that have different contents:
	`read_load_lmp`: Parses load and LMP data into Numpy data arrays and Python string lists\
	`read_covid_lmp`: Parses aggregated COVID-19 data into Numpy data arrays and Python string lists\
	`read_genmix`: Parses generation data into Numpy data arrays and Python string lists\
	`read_weather`: Parses weather and climate data into Numpy data arrays and Python string lists\
	
	
## example_covid.py
- This script demonstrates the usage of the .csv datasets and utility functions by plotting the daily new confirmed cases and deaths in the entire CAISO RTO region.

## example_gemix.py
- This script demonstrates the usage of the .csv datasets and utility functions by aggregating and plotting the:
	1) year-long generation from each type of energy sources in the entire CAISO RTO region
	2) daily output of solar generation in the entire CAISO RTO region

## Dependencies
- NumPy and Matplotlib are required to run the example demonstration scripts.
- Installation commands:\
`pip install numpy` and `pip install matplotlib`
