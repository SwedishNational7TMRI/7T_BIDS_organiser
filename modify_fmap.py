##### add data to json file
import json
import numpy as np
from glob import glob as gl
import os

# get all fielmap json files
files = np.sort(gl('../rawdata/sub-*/ses-*/fmap/*_fieldmap.json'))
for f in files:
    s = f.split(os.sep)[:-2]
    str_intendedfor = os.path.join(*s)+'/func/*_bold.nii.gz'
    file_intendedfor = gl(str_intendedfor)
    func_file = file_intendedfor[-1].split("/")[-3:]
    func_file = '/'+os.path.join(*func_file)
    toadd = { "Units": "Hz", "IntendedFor": "bids::"+func_file, "B0FieldIdentifier": "b0map_fmap0"}

    with open (f, 'r') as data:
        json_data=json.load(data)
        json_data.update(toadd)

    with open (f, 'w') as data:
        json.dump(json_data, data, indent=2)
