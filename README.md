# A Cross-Domain Data Hub to Track the Impact of COVID-19 on the U.S. Electricity Markets

[![GitHub commit](https://img.shields.io/github/last-commit/tamu-engineering-research/COVID-EMDA)](https://github.com/GuangchunRuan/COVID-EMDA/commits/master) &nbsp;
[![GitHub license](https://img.shields.io/badge/license-MIT-yellow)](https://choosealicense.com/licenses/mit/)


> This data hub, **COVID-EMDA+** (**C**oronavirus **D**isease - **E**lectricity **M**arket **D**ata **A**ggregation+), is orginally designed to track the potential impacts of COVID-19 on the electricity markets in the United States of America, and could also contribute to relevant interdisciplinary researches.

<p align="center">
<img src="figure/covid_emda_logo.jpg" alt="COVID-EMDA Logo" />
</p>


## Features
- Overall, this data hub contains the `coronavirus case`, `weather`, `generation mix`, `load` and `price data` for all the existing U.S. electricity marketplaces (CAISO, MISO, ISO-NE, NYISO, PJM, SPP , ERCOT) and some typical cities in these markets (Los Angeles, Boston, New York City, Philadelphia, Chicago, Kansas City, Houston). We also integrate the cellphone and night-time lighting datasets as additional resources.
- All the coronavirus case, weather and electricity market data are carefully verified and coordinated to match the geological scale.
- `Daily load profile`, `hourly generation mix` and `day-ahead price` are recorded and tidied in a consistent, compact and ready-to-use data format that makes it easy for cross-market analysis.
- Historical data dating back to 2017 are included as a time-series benchmark.


## Navigation
This github repository is structured as follows.
<p align="center">
<img src="figure/folder-structure-0725.png" alt="COVID-EMDA Logo" />
</p>

All the data source files are archived in folder `date_source/`, the cleaned and processed data are stored in folder `data_release/`. The support team will conduct daily updates to capture the latest data. All these files are properly collected by location. The file naming convetion for this data hub is: `MARKET_AREA_CATEGORY.csv`, e.g. `nyiso_nyc_load.csv` is a dataset of load profile in New York City from 2017 to present.

Readers can turn to folder `startup/` for quick start, `supplementary/` for addtional data and codes in our research work, and `parser/` for the basic tools to handle the source files.


## Suggested Citation 
- Please cite the following paper when using this data hub:  
`
G. Ruan, D. Wu, X. Zheng, S. Sivaranjani, H. Zhong, C. Kang, M. A. Dahleh and L. Xie, A Cross-Domain Approach to Analyzing the Short-Run Impact of COVID-19 on the U.S. Electricity Sector, arXiv preprint: https://arxiv.org/abs/2005.06631, 2020.
`  
This paper conducts a comprehensive introduction of the data hub and some preliminary analysis results.  
Available at: [arXiv](https://arxiv.org/abs/2005.06631) and [EnerarXiv](http://www.enerarxiv.org/page/thesis.html?id=1840) 



## Data Source
This data hub contains three major sources: U.S. electricity market data, COVID-19 cases and weather data. For some categories, multiple data sources are carefully gathered to ensure accuracy.

- Electricity Market Data:\
**Link**: &nbsp; [CAISO](http://oasis.caiso.com/mrioasis/logon.do), &nbsp; [MISO](https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/), &nbsp; [ISO-NE](https://www.iso-ne.com/markets-operations/iso-express), &nbsp; [NYISO](https://www.nyiso.com/energy-market-operational-data), &nbsp; [PJM](https://dataminer2.pjm.com/list), &nbsp; [SPP](https://marketplace.spp.org/groups/operational_data), &nbsp; [ERCOT](http://www.ercot.com/), &nbsp; [EIA](https://www.eia.gov/beta/electricity/gridmonitor/dashboard/electric_overview/US48/US48), &nbsp; [EnergyOnline](http://www.energyonline.com/).
- COVID-19 Case Data:\
**Link**: &nbsp; [John Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19).
- Weather Data:\
**Link**: &nbsp; [Iowa State Univ IEM](https://mesonet.agron.iastate.edu/request/download.phtml), &nbsp; [NOAA](https://www.nws.noaa.gov/ost/asostech.html).

## Additional Dataset
- **Cellphone Dataset**:\
**Description**: &nbsp; This dataset aggregates and processes the real-time GPS location of cellphone users by Census Block Group. It includes social distancing data and patterns of visits to Point of Interests (POIs). To obtain the access, please click the link below and apply for SafeGraph's permission which is totally free.\
**Link**: &nbsp; [Cellphone Dataset from SafeGraph](https://docs.safegraph.com/docs)

- **Night Time Light (NTL) Satellite Dataset**:\
**Description**: &nbsp; This dataset includes the raw satellite image taken at night time in each area.\
**Link**: &nbsp; [NTL Dataset from NASA](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A1/)

## Contact Us
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Email contact: &nbsp; [Le Xie](mailto:le.xie@tamu.edu?subject=[GitHub]%20COVID-EMDA), &nbsp; [Dongqi Wu](mailto:dqwu@tamu.edu?subject=[GitHub]%20COVID-EMDA), &nbsp; [Xiangtian Zheng](mailto:zxt0515@tamu.edu?subject=[GitHub]%20COVID-EMDA).



## Support Team
This project is a collaboration of our group members under the supervision of Prof. Le Xie at Texas A&M University:

<p align="center">
<img src="figure/contributor-0725.png" alt="COVID-EMDA Logo" />
</p>

Please also check our [Group Website](https://gridx.engr.tamu.edu/?page_id=30) for the detailed biography of each group member.
