# Guidelines for the City-Level NTL Data

## Introductions
This compressed dataset is the original and unmodified NTL dataset from the [NASA VNP46A1 product](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A1/). Instead of the original `.h5` data format which contains the NTL data for entire geographic tiles that are 1,200 km by 1,200 km, the data is cropped to only include the small region around each of the cities. The data is stored using [pickle](https://docs.python.org/3/library/pickle.html) as `.pcl` files. Each `.pcl` file contains a daily snapshot of NTL datas sampled around midnight local time (the exact time can be accessed in the data file). The data object can be easily extracted using `pickle` APIs. A simple example is given below:
```
# import the modules
import pickle
import matplotlib.pyplot as plt

# path to pickle file
file = 'nyc/nyiso_nyc_ntl_01-01.pcl'

# load the data object to variable "data" and plot the raw NTL data using Matplotlib
with open(file,'rb') as fh:
    data = pickle.load(fh)
    plt.imshow(data['dnb_radiance'])
    plt.show()

```

## Field Description
Please refer to the [NASA VIIRS Black Marble Userguide](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_BlackMarble_UserGuide.pdf) for a detailed description of each measurement entry.
The data object from pickle is a dictionary containing the following fields: 
- `dnb_radiance` is the raw 500m resolution light radiance level measured at the sensor.
- `cloud_mask` is the information of cloud and weather above each datapoint. The number should be intepreted as concatenated binary flags where different bits represents different information. Please refer to the userguide for details.
- `utc_time` is the UTC timestamp recorded at the time the data was sampled.
- `moon_fraction` is the moon illumination fraction at the time of measurement. 
- `lunar_zenith` and `lunar_azimuth` are the Zenith and Azimuth angle of the moon at the time of measurement.
- `moon_glint` is the moon glint angle at the time of measurement

Other data exists in the original `.h5` file, such as radiance intensity and brightness temperature at different infared frequency bands. The data are not used in this dataset but can be accessed from the NASA database freely.
