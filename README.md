# 7T BIDS organiser
Tools to organise 7T data into BIDS structure


Bash and python scripts to convert DICOM data into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

The folder structure will be
- Original dicoms in `/dicomdir`
- Re-named and re-arranged dicoms in are `/sourcedata`, which is the BIDS sourcedata-folder
- BIDS-organised NIfTIs in `/rawdata`


To complete the conversion: 

1. Run script `DcmDicomdir_to_DcmSourcedata.sh` \
This re-names the dicoms and sorts them into `/sourcedata`

2. Run script `DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh` \
Runs `heudiconv` without conversion
Generates `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`.

3. Run script `DcmSourcedata_to_NiftiRawdata.sh` \
This converts the dicoms in `/sourcedata` to BIDS-organised NIfTIs in `/rawdata` using the heudiconv routine. 
- [heudiconv](https://github.com/nipy/heudiconv) is run with using a Docker container using rules set in the python file `7T049_CVI_heuristic.py`
- The script also makes a BIDS-validation

4. Run script `MRIQC.sh` \
This script runs [MRIQC](https://github.com/bids-standard/bids-validator) on the data
