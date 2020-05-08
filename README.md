# Combined Data Hub with and Electricity Market and Coronavirus Case Data in U.S.

[![GitHub commit](https://img.shields.io/github/last-commit/GuangchunRuan/COVID-EMDA)](https://github.com/GuangchunRuan/COVID-EMDA/commits/master) &nbsp;
[![GitHub license](https://img.shields.io/badge/license-MIT-yellow)](https://choosealicense.com/licenses/mit/)


> This data hub, **COVID-EMDA** (**C**oronavirus **D**isease - **E**lectricity **M**arket **D**ata **A**ggregation), is orginally designed to track the potential impacts of COVID-19 on the electricity markets in the United States of America, and could also contribute to relevant interdisciplinary researches.

<p align="center">
<img src="figure/covid_emda_logo.JPG" alt="COVID-EMDA Logo" />
</p>


## Features
- Overall, this data hub contains the `coronavirus case`, `weather`, `generation mix`, `load` and `price data` for all the existing U.S. electricity marketplaces (CAISO, MISO, ISO-NE, NYISO, PJM, SPP , ERCOT) and seven typical cities in each market (San Francisco, Chicago, Boston, New York City, Philadelphia, Kansas City, Houston). 
- All the coronavirus case, weather and electricity market data are carefully verified and coordinated to match the geological scale.
- `Daily load profile`, `hourly generation mix` and `day-ahead price` are recorded and tidied in a consistent, compact and ready-to-use data format that makes it easy for cross-market analysis.
- Historical data dating back to 2017 are included as a time-series benchmark.



## Navigation
This github repository is structured as follows.
```text
  COVID-EMDA
  |
  ├── db1_source/
  │    ├── caiso/
  │    ├── miso/
  │    ├── isone/
  │    ├── nyiso/
  │    ├── pjm/
  │    ├── spp/
  │    ├── ercot/
  │    ├── covid/
  │    ├── weather/
  │    ├── README.md
  ├── db2_release/
  │    ├── caiso/
  │    ├── miso/
  │    ├── isone/
  │    ├── nyiso/
  │    ├── pjm/
  │    ├── spp/
  │    ├── ercot/
  │    ├── README.md
  ├── quick_start/
  ├── parser/
  ├── README.md
```
All the data source files are archived in folder `db1_source/`, the cleaned and processed data are stored in folder `db2_release`. The supporting team will provide daily updates to capture the latest sitation. All these files are properly collected by location. The file naming rule is: `MARKET_AREA_CATEGORY.csv`, e.g. `nyiso_nyc_load.csv`. This is a dataset of load profile in New York City, from 2017 to present.

Readers can turn to folder `quick_start/` for information about basic applications. For the need of extension, we provide the parser codes, which can be found in folder `parser/`.


## Data Source
This data hub contains three major sources: U.S. electricity market data, COVID-19 cases and weather data. For some categories, multiple data sources are carefully gathered to ensure accuracy.

- Electricity Market Data:\
[CAISO](http://oasis.caiso.com/mrioasis/logon.do), &nbsp; [MISO](https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/), &nbsp; [ISO-NE](https://www.iso-ne.com/markets-operations/iso-express), &nbsp; [NYISO](https://www.nyiso.com/energy-market-operational-data), &nbsp; [PJM](https://dataminer2.pjm.com/list), &nbsp; [SPP](https://marketplace.spp.org/groups/operational_data), &nbsp; [ERCOT](http://www.ercot.com/), &nbsp; [EIA](https://www.eia.gov/beta/electricity/gridmonitor/dashboard/electric_overview/US48/US48), &nbsp; [EnergyOnline](http://www.energyonline.com/).
- COVID-19 Case Data:\
[John Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19).
- Weather Data:\
[Iowa State Univ IEM](https://mesonet.agron.iastate.edu/request/download.phtml).

## Additional Dataset
- **Cellphone Dataset**:\
**Description**: This dataset aggregates and processes the real-time GPS location of cellphone users by Census Block Group. It includes social distancing data and patterns of visits to Point of Interests (POIs). To obtain the access, please click the link below and apply for SafeGraph's permission which is totally free.\
**Link**:  [Cellphone Dataset from SafeGraph](https://docs.safegraph.com/docs)

- Night Time Light Satellite Dataset:\
**Description**: This dataset includes the raw satellite image taken at night time in each area.\
**Link**:  [NTL Dataset from NASA](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A1/)

## Contact Us
Please contact our emails: &ensp; [Guangchun Ruan](mailto:guangchun@tamu.edu?subject=[GitHub]%20COVID-EMDA), &nbsp; [Le Xie](mailto:le.xie@tamu.edu?subject=[GitHub]%20COVID-EMDA).

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Aknowledgements
This data repository is based on the collaborated work of our fellow group members and our instructor Professor Le Xie at Texas A&M University:

<p float="left">
    <img src="figure/ruan.png" alt="ruan" style="width:20%">
    <p> Guangchun Ruan </p>
    <img src="figure/wu.png"" alt="Forest" style="width:20%">
    <img src="figure/zheng.png"" alt="Mountains" style="width:20%">
    <img src="figure/xie.png"" alt="Mountains" style="width:20%">
    <img src="figure/alimi.png"" alt="Mountains" style="width:20%">                                                            
</p>


@ [Guangchun Ruan](mailto:guangchun@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;\
@ [Dongqi Wu](mailto:dqwu@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;\
@ [Xiangtian Zheng](mailto:zxt0515@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;\
@ [Le Xie](mailto:le.xie@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;\
@ [Suraj Abolaji Alimi](mailto:alimiabolaji@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;\
@ [Jiahan Wu](mailto:jiahwu95@tamu.edu?subject=[GitHub]%20COVID-EMDA)&ensp;

