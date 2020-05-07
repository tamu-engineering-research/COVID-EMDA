# Cleaned Database

This folder contains all the cleaned and processed data, the data source files can be found in folder `db1_source/`. All the file namess in this folder obey the rule of `MARKET_AREA_CATEGORY.csv`. Readers can find their interested files quickly by activating the Github's file finder (Press `T`).

Current data are updated to April 12, 2020. After final release, the supporting team will implement daily updates to catch the latest situations.


## Field Description
All files are organized in a wide csv table.
- Field `date`: list all the date from 2017 to present.
- Field `fuel`: only in generation mix dataset, represent the different fuel souce used by generators. Possible values: coal, gas, oil, nuclear, hydro, wind, solar, other, export. We harmonize all the different definitions in different electricity markets.
- Field `HH:MM`: represent the hourly time slot. For example, items in the column 08:00 represent the recorded data of period 8AM to 9AM.
