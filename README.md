# 7T BIDS organiser
Tools to organise 7T data into BIDS structure

Bash and python scripts to convert DICOM data into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

# People
...

# folder structure
- BIDS-organised NIfTIs in `/rawdata`
- Original dicoms in `/dicomdir`
Inside the `/dicomdir` your should have all your subjects, sessions (if applicable) and than the different folders for each sequence

The folder structure needs to be:
Readme.md
|-> code
  |-> heuristic.py # will be generated later
  |-> DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh
  |-> DcmSourcedata_to_NiftiRawdata.sh
  |-> MRIQC.sh
|-> rawdata # will be generated
|-> derivatives # will be generated
|-> dicomdir
  |-> sub-001
    |-> session1 (if applicable)
      |-> folder sequence
        |-> *.DCM
      |-> folder sequence
        |-> *.DCM
    |-> session2
  |-> sub-002
  ...

# Installation
Docker...

...pull the github repo

...make the bash files executeable

# Usage
1. Open Terminal and step into the `/code` folder

2. Run the DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh only for one subject, e.g.:
```bash
./DcmSourcedata_to_NiftiRawdata_generate_Dicominfo.sh 105
```
This runs heudiconv without conversion but it generates the hidden folder .heudiconv in `/rawdata` which includes a template for the heuristic file as well as the dicominfo file `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`.

3. Create your heuristic file (see example) according to your data and dicominfo file and put it into `/code/heuristic.py`

4. Test the dicom2bids transformation on one subject:
```bash
./DcmSourcedata_to_NiftiRawdata.sh 105
```
This converts the dicoms in `/dicomdir` to BIDS-organised NIfTIs in `/rawdata` using the heudiconv routine.
- [heudiconv](https://github.com/nipy/heudiconv) is run with using a Docker container using rules set in the python file `7T049_CVI_heuristic.py`
- The script also makes a BIDS-validation

5. Check your data in `/rawdata`

6. Transform all subjects
a. create a list of the subjects and save it in a txt-file, e.g.:
```bash
for f in sub-*; do echo $f | cut -d"-" -f2; done > ../code/subjects.txt
```

b. go back to `/code` folder and convert all subjects from dicom2bids, e.g.:
```bash
for sub in $(cat subjects.txt); do ./DcmSourcedata_to_NiftiRawdata.sh $sub; done
```

7. adaptations to BIDS format...


## open issues
-
