#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 08:03:49 2022

@author: Peter Mannfolk
peter.mannfolk@med.lu.se

modified by: Theodor Rumetshofer
theodor.rumetshofer@med.lu.se

"""

#
import numpy as np
import pandas as pd

st = 'new'
TR = 1.8 # Repetition time (s), check dicom header 0018,0080
nSlices = 68 # Number of slices, check in the dicom header "2001,1018"
mbFactor = 2 # Multiband factor. This cannot be found in the Dicom header and have to be checked on the scanner.


# Calculate slice timing vector (https://en.wikibooks.org/wiki/SPM/Slice_Timing#cite_note-cbs-multiband-28)
# this if-else is a relic how slice timing has been handled in SPM
if st == 'classic':
    TA = float(TR) - (float(TR)/float(nSlices))
elif st == 'new':
    TA = 0.0
else:
    TA = 0.0 # Obsolete. ST, and hence TA will not be used


# create the slice timing vector in seconds
delta_t = float(TR)/(float(nSlices)/float(mbFactor))
slice_order = list(range(0,int(nSlices/mbFactor)))*mbFactor # Assuming 'ascending' Philips order
slice_timing = np.multiply(slice_order,delta_t).tolist()



# # adaptations by theo - save the slice timing in a txt file
# with open("sliceTiming.txt", "w") as output:
#     output.write(str(slice_timing))

# save as csv
#np.savetxt('slice_timing.csv', slice_timing)
df = pd.DataFrame(slice_timing, columns=['time'])
df.to_csv('sliceTiming.csv')
 
