# 7T BIDS organiser
Tools to organise 7T data into BIDS structure

Bash and python scripts to convert DICOM data into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

# People
...

# Recommended folder structure
- BIDS-organised NIfTIs in `/rawdata`
- Original DICOMs in `/dicomdir`
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
      ├── dicomdir # DICOM files
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

**4. Create your heuristic file (see example `example_heuristic.py`, according to your data and dicominfo file and save it under `/code/heuristic.py`**

**5. Transform one subject from DICOM to BIDS to test your heuristic file using DcmSourcedata_to_NiftiRawdata.sh, e.g.:**
```bash
./DcmSourcedata_to_NiftiRawdata.sh 105
```
This converts the DICOMs in `/dicomdir` to BIDS-organised NIfTIs in `/rawdata` using the heudiconv routine.
- [heudiconv](https://github.com/nipy/heudiconv) is run with using a Docker container using rules set in the python file `heuristic.py`
- The script also makes a BIDS-validation at the generated
- Docker images from heudiconv or BIDS-validator get automatically updated if needed

**6. Check your data in `/rawdata`**

**7. When the conversion is correct, transform all subjects to BIDS**

a. create a list of the subjects. Go into `/dicomdir` and run the following line to save all subject names in a txt-file saved in the code folder, e.g.:
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

**OPTIONAL: remove possible errors in the BIDS format**
Test the BIDS format online: https://bids-standard.github.io/bids-validator/

- Put files which do not fullfill BIDS and/or not needed now, into the hidden .bidsignore file manually. E.g.:
```text
sub-*/ses-*/anat/*_MP2RAGE.*
sub-*/ses-*/anat/*_UNIT1.*
sub-*/ses-*/dwi/*_ADC.*
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

- Add the SliceTiming to the BOLD json files (if applicable)
Open the file Slice_timing_snippet.py and adapt the following parameters: *TR*, *nSlices*, *mbFactor* according to your dataset. Run the python script which generates a CSV-file with the corresponding slice timing (sliceTiming.csv).
```bash
python slice_timing_snippet.py
```
Control the values in your CSV-file and double check the slice order, should be ASCENDING, at the MRI scanner. The number of rows should be the same as your number of slices and the highest number should be lower than your repetition time TR. Add the *SliceTiming* information as well as the *B0FieldSource* to each BOLD json file using the modify_func.py.
OBS! The *B0FieldSource* in the BOLD JSON file as well as the *B0FieldIdentifier* in the Fieldmap JSON file (see below) must be in line with the corresponding fieldmap case, see: https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#types-of-fieldmaps
```json
{
   "SliceTiming": [
     0.0,
     0.0529411764705882,
     ...
   ],
   "B0FieldSource": "b0map_fmap0"
}
```

```bash
python modify_func.py
```


- Add the *Unit*, *intented use for* and *B0FieldIdentifier* to the fieldmap-JSON file (see example below):
```json
{
   "Units": "Hz",
   "IntendedFor": "bids::/ses-post/func/sub-105_ses-post_task-rest_run-1_bold.nii.gz",
   "B0FieldIdentifier": "b0map_fmap0"
}
```
Example: Run the following lines in modify_fmap.py to add the above mentioned information to all fieldmap json files in a multisession dataset.
```bash
python modify_fmap.py
```


## open issues
(will be added later)
- Add the correct Phase Encoding Direction to the BOLD json files
