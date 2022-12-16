# 7T BIDS organiser
Tools to organise 7T data into BIDS structure

Bash and python scripts to convert DICOM data into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

# People
...

# Recommended folder structure
- BIDS-organised NIfTIs in `/rawdata`
- Original dicoms in `/dicomdir`
Inside the `/dicomdir` your should have all your subjects, sessions (if applicable) and than the different folders for each sequence

The folder structure needs to be:
```sh
  /studydir
      ├── code
        ├── README.md
        ├── heuristic.py # will be generated later
        ├── DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh
        ├── DcmSourcedata_to_NiftiRawdata.sh
        ├── MRIQC.sh      
      ├── rawdata # will be generated
      ├── derivatives # will be generated
      ├── dicomdir # dicom files
        ├── sub-001
          ├── session 1 (if applicable)
            ├── folder sequence
              ├── *.DCM
            ├── folder sequence
              ├── *.DCM
          ├── session 2 (if applicable)
            ├── sub-002
            ...
```

# Installation
... Docker...

# Changes to the original files
**DcmDicomdir_to_DcmSourcedata.sh**
- deleted this file (renaming of DICOM files) due to possible disk space issues.

**DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh**
- added additional help with an example
- instead of the "sourcedatadir", "dicomdir" is used (because DICOM renaming was skipped)
- parameter ""-f convertall" instead of the heuristic file - not really needed at this step
- added some echos to show what the programme is doing
- added sessions to your run by checking the folder name within the subject folder of the dicomdir + added session name to log file

**DcmSourcedata_to_NiftiRawdata.sh**
- added additional help with an example
- instead of the "sourcedatadir", "dicomdir" is used (because DICOM renaming was skipped)
- apply the heuristic file from the /code folder
- added sessions to your run by checking the folder name within the subject folder of the dicomdir + added session name to log file
- removed -t from the docker command to run multiple subjects


# Usage
**1. Open Terminal and pull the repository into your study folder**
```bash
git clone https://github.com/SwedishNational7TMRI/7T_BIDS_organiser.git
```

**2. Rename the downloaded folder into `/code`. Step into the `/code` folder and make all bash-files executeabel, e.g.:**
```bash
chmod a+x *.sh
# ... or using admin rights:
sudo chmod a+x *.sh
```

**3. Run the DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh only for one subject, e.g.:**
```bash
./DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh 105
```
This runs heudiconv without conversion but it generates the hidden folder .heudiconv in `/rawdata` which includes a template for the heuristic file as well as the dicominfo file `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`.

**4. Create your heuristic file (see example `example_heuristic.py`, according to your data and dicominfo file and save it into `/code/heuristic.py`**

**5. Test the dicom2bids transformation on one subject:**
```bash
./DcmSourcedata_to_NiftiRawdata.sh 105
```
This converts the dicoms in `/dicomdir` to BIDS-organised NIfTIs in `/rawdata` using the heudiconv routine.
- [heudiconv](https://github.com/nipy/heudiconv) is run with using a Docker container using rules set in the python file `heuristic.py`
- The script also makes a BIDS-validation at the generated
- Docker images from heudiconv or BIDS-validator get automatically updated if needed

**6. Check your data in `/rawdata`**

**7. Transform all subjects**
a. create a list of the subjects. go into `/dicomdir` and run the following line to save all subject names in a txt-file, e.g.:
```bash
for f in sub-*; do echo $f | cut -d"-" -f2; done > ../code/subjects.txt
```

b. go back to `/code` folder and convert all subjects from dicom2bids, e.g.:
```bash
for sub in $(cat subjects.txt); do ./DcmSourcedata_to_NiftiRawdata.sh $sub; done
```

c. control if the conversion was successful for each subject.
```bash
for f in ../derivatives/logs/sub-1*/*ses-*.log; do grep -i "INFO: PROCESSING DONE:" < $f; echo $f; done
# ... or looking for the word "error" in the log files
for f in ../derivatives/logs/sub-1*/*ses-*.log; do grep -i "error:" < $f; echo $f; done
```

**optional: remove possible errors in the BIDS format**
Test the BIDS format online: https://bids-standard.github.io/bids-validator/

- Put files which do not fullfill BIDS and/or not needed now, into the hidden .bidsignore file manually. E.g.:
```text
sub-\*/ses-\*/anat/\*_MP2RAGE.\*
sub-\*/ses-\*/anat/\*_UNIT1.\*
sub-\*/ses-\*/dwi/\*_ADC.\*
```

- Delete the MP2rage sequences from the .tsv file in each session folder, e.g.:
```bash
for f in ../rawdata/sub-*/ses-*/sub-*scans.tsv; do sed -i "" -e '/mp2rage/Id' $f ; done
```

- Rename the filemaps files for resting state _epi2 = _fieldmap and _ep1 = _magntiude (nii and json files):
```bash
for f in ../rawdata/sub-*/ses-*/fmap/*_epi1.*; do mv $f "${f//_epi1./_magnitude.}" ; done
for f in ../rawdata/sub-*/ses-*/fmap/*_epi2.*; do mv $f "${f//_epi2./_fieldmap.}" ; done
```

- Rename also the fmaps in the .tsv file
```bash
for f in ../rawdata/sub-*/ses-*/sub-*scans.tsv; do sed -i "" -e "s/_epi1/_magnitude/" $f; done
for f in ../rawdata/sub-*/ses-*/sub-*scans.tsv; do sed -i "" -e "s/_epi2/_fieldmap/" $f; done
```

- Add the *Unit*, *intented use* as well as *B0FieldIdentifier* to the fieldmap-JSON file (see example below):
```json
{
   "Units": "Hz",
   "IntendedFor": "bids::/ses-post/func/sub-105_ses-post_task-rest_run-1_bold.nii.gz",
   "B0FieldIdentifier": "b0map_fmap0"
}
```
Example: Run the following lines in modify_fmap.py to add the above mentioned information to all fieldmap json files in a multisession dataset:
```python
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
```

- Add the SliceTiming to the BOLD json files
(script from Peter Mannfolk - will be added soon)

- Add the correct Phase Encoding Direction to the BOLD json files
?


## open issues
(will be added later)
