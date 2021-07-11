# Cleaned Datasets for Release

This folder contains all the cleaned and processed data, and the source files can be found in another folder `data_source/`. All the file namess in this folder follow the file naming convention of `MARKET_AREA_CATEGORY.csv`. Readers can find the files of interest quickly by activating the Github's file finder (Press `T`), or directly import the data from website link (Click [Here](https://github.com/tamu-engineering-research/COVID-EMDA/tree/master/supplementary/impact-assessment-paper) for some examples).

## Data Updates
The electricity market datasets in this folder are updated daily, and the additional celluar phone and satellite data are updated weekly. The latest available time for different datasets are listed below.
- **Electricity Market Data**: Most are avaiable for Jul 7, 2021 (except ercot_genmix.csv for May 31 due to the data source limitation).
- **Weather and COVID Cases Data**: Available for Jul 7, 2021 (align with the other sources).
- **Visit Pattern Data**: Available up to Nov 22, 2020.
- **Social Distancing Data**: Available up to Dec 31, 2020.
- **Night-Time Lighting Data**: Available for Aug 28, 2020.

## Electricity Data Field Description
All files are organized in a wide csv table.
- Field `date`: list all the date from 2017 to present. Format: `YYYY-mm-dd`
- Field `fuel`: only in generation mix dataset, represent the different fuel souce used by generators. Possible values: coal, gas, oil, nuclear, hydro, wind, solar, export, other. We harmonize all the different definitions in different electricity markets.
- Field `kind`: only in weather dataset, represent the type of measurement that is recorded in each corresponding row. Possible values:
dwpc (dew point temperature), relh (relative humidity), sped (wind speed), tmpc (temperature)
- Field `HH:MM`: represent the hourly time slot. For example, column "08:00" records the data of period 8AM to 9AM.

## COVID-19 Data Field Description
- Field `date`: list all the date from January 23, 2020 to present. Format: `YYYY-mm-dd`
- Field `accum_confirm`: Accumulated confirmed case number recorded at each date
- Field `new_confirm`: Newly confirmed case number of each date
- Field `infect_rate`: Infection ratio calculated at each date
- Field `accum_death`: Accumulated confirmed deth number recorded at each date
- Field `new_death`: Newly confirmed death number of each date
- Field `fatal_rate`: Fatal rate calculated at each date

## Visit Pattern to Point of Interests (POIs)
- Field `date`: list all the date from December 30, 2019 to present. Format: `YYYY-mm-dd`
- Field `Restaurant_Recreation`: Daily total number of visits to Restaurant and Recreation places
- Field `Grocery_Pharmacy`: Daily total number of visits to Grocery and Pharmacy places
- Field `Retail`: Daily total number of visits to Retail places

## Social Distancing
- Field `date`: list all the date from January 1, 2020 to present. Format: `YYYY-mm-dd`
- Field `completely_home_device_count_percentage`: percentage of devices that stay at home 24 hours out of all devices
- Field `median_home_dwell_time_percentage`: median proportion of home dwell time in one day
- Field `part_time_work_behavior_devices_percentage`: percentage of devices that go to workplaces for 3 to 6 hours out of all devices
- Field `full_time_work_behavior_devices_percentage`: percentage of devices that go to workplaces for more than 6 hours out of all devices
- Field `completely_home_device_count`: count of devices that stay at home 24 hours
- Field `device_count`: total count of devices
- Field `part_time_work_behavior_devices`: count of devices that go to workplaces for 3 to 6 hours
- Field `full_time_work_behavior_devices`: count of devices that go to workplaces for more than 6 hours

## Data Quality Control
To provide reliable and easy-to-use datasets, we implement a series of data checking and cleaning procedures, and also take advantage of different data sources for cross validation. When using the datasets in this folder, please check the following table to get some knowledge for the released data.

| Dataset Name         | Market     | Area         | Category       | Missing Dates        |
|----------------------|------------|--------------|----------------|----------------------|
| caiso_rto_genmix.csv | CAISO      | RTO Level    | Generation Mix | Sep 23 - Oct 3, 2019 |
| caiso_rto_lmp.csv    | CAISO      | RTO Level    | Day-Ahead LMP  | Jan 1 - Jan 18, 2017; Oct 5, Oct 9, 2020 |
| caiso_la_load.csv    | Near CAISO | Los Angeles  | Hourly Load    | Nov 5, 2017; Jan 11 - 12, Jun 29 - 30, Jul 1 - 9, Sep 27, Nov 4, 2018; Mar 10, Nov 3, 2019; Mar 8, Nov 1, 2020; Mar 14, 2021 |
| caiso_la_weather     | CAISO      | Los Angeles  | Weather        | Apr 7 - 8, 2021          |
| ercot_rto_load.csv   | ERCOT      | RTO Level    | Hourly Load    | Dec 13, 2020         |
| ercot_houston_load.csv| ERCOT     | Houston City | Hourly Load    | Dec 13, 2020         |
| ercot_houston_weather.csv | ERCOT | Houston City | Weather        | Feb 15 - 16, 2020         |
| isone_rto_genmix.csv | ISO-NE     | RTO Level    | Generation Mix | Apr 30, 2018; Jun 21, Oct 30-31, Dec 06, 2020 |
| isone_rto_load.csv   | ISO-NE     | RTO Level    | Hourly Load    | Dec 17, 2020         |
| pjm_rto_genmix.csv   | PJM        | RTO Level    | Generation Mix | Mar 29 - Apr 2, 2017 |
| spp_rto_genmix.csv   | SPP        | RTO Level    | Generation Mix | Mar 29, 2019         |
| spp_kck_weather.csv  | SPP        | Kansas City  | Weather        | Sep 22 - 23          |




