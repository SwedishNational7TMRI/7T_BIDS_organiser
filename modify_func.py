##### add data to json file
import json
import numpy as np
from glob import glob as gl
import os
import pandas as pd


# get all BOLD json files
files = np.sort(gl('../rawdata/sub-*/ses-*/func/*_bold.json'))


# read the slicetiming from the csv file
st = pd.read_csv('sliceTiming.csv', index_col=0)
st = st['time'].tolist()

# create the json entry, which should be the same for each bold sequence
toadd = {"SliceTiming": st}


for f in files:

    with open (f, 'r') as data:
        json_data=json.load(data)
        json_data.update(toadd)

    with open (f, 'w') as data:
        json.dump(json_data, data, indent=2)
