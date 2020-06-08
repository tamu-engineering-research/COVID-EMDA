## Guidelines for the city-level NTL data

# Introductions
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

# Field Description
