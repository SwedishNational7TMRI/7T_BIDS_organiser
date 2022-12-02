# 7T BIDS organiser
Bash and python scripts to convert DICOM data from the 7T into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

The BIDS specification/standard is preferably browsed [online](https://bids-specification.readthedocs.io/en/stable/). A BIDS-organised `studydir` for a neuroimaging study can look like
```sh
/studydir
    ├── code
    ├── derivatives <= harbours processed data
    ├── sourcedata  <= harbours DICOM images 
    ├── rawdata     <= harbours BIDS organised NIfTI images
    ├── sequences
    └── stimuli
```
Note, the only folder that needs to be truely [BIDS compliant](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html) is the `/rawdata` folder
```sh
/studydir
    └── rawdata
            ├── CHANGES
            ├── dataset_description.json
            ├── participants.json
            ├── participants.tsv
            ├── README
            ├── sub-S01
            │   ├── anat
            │   ├── dwi
            │   ├── fmap
            │   ├── func
            │   ├── session.tsv
            │   ├── sub-S01_scans.json
            │   └── sub-S01_scans.tsv
            └── task-rest_bold.json
```
and its compliancy to the BIDS standard should be checked with a [BIDS validator](https://github.com/bids-standard/bids-validator).

## Installation
This software is best used as a python package which is installed using `pip`. Python 3.8 or higher is required. Recommended that you do this in a an isolated conda or virtual environment. To install, navigate to the main directory and execute
```sh
python -m pip install -e .
```

To install python 3.8 in conda use:
```
conda create -n py38 python=3.8
```

To download the necessary docker containers execute
```sh
shell download_docker.sh
```

After you have installed the python package you will have a set of tools available:
- `7Tbids_import_dicoms`: Takes dicoms from an unsorted `dicomdir` and puts them in a organised folder structure `/sourcedata.
- `7Tbids_nifti2bids`: Takes your data from dicoms to BIDS-organised structure with NIfTI files in the `/rawdata` folder using the [heudiconv](https://heudiconv.readthedocs.io/en/latest/) routine. This is done in two steps
    1. Call with option `--organize` to run `heudiconv` without conversion. Generates `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`.
    2. Call with option `--convert` to do the actual nifti conversion. This requires input to appropriate heuristics file (see above).
- `7Tbids_validate`: Used to validate your BIDS tree structure.


The following folder structure and conventions are assumed to be used
- Original dicoms in `dicomdir`. These are "raw" DICOMS exported from the 7T archive. This folder will be used as inputs to some scripts and can be located anywhere.
    - Your DICOM data might be stored with run numbers instead of subject ID. To do this mapping you can use a `study_key.tsv` file. See example in this repository.
- Your `studydir` is the path to where you want your study data to be stored.
- It is recommended to store your own study code in a specific directory, `code`. Suggestions from the BIDS standard is to put is in `studydir/code`.
- Re-named and re-arranged dicoms will be stored in  `studydir/sourcedata`, which is the BIDS sourcedata-folder
- BIDS-organised NIfTIs in `studydir/rawdata`
- You need a heuristics file for `heudiconv`. This should be stored in your code-folder. See the `misc` folder here in the repo for example.

To convert data from raw DICOMS to a BIDS valid structure with NIFTI files it is recommended to set up a shell script with the following structure.

```sh
STUDYDIR=<my_bids_dir>
CODEDIR=<my_code_dir>
DICOMDIR=<my_dicom_dir>
sID=<Study_ID>      #E.g. S02

study_key=${STUDYDIR}/study_key.tsv
heuristics_file=7T049_CVI_heuristic.py # This is assumed to live in the CODEDIR

# dicomdir -> sourcedata
7Tbids_import_dicoms --dicom_dir=$DICOMDIR --study_dir=$STUDYDIR --id=$sID --key=$study_key

# Organize and analyze sourcedata folder
7Tbids_nifti2bids --study_dir=$STUDYDIR \
                  --code_dir=$CODEDIR --id=$sID \
                  --heuristic_file=$heuristics_file \
                  --organize

# sourcedata -> rawdata
7Tbids_nifti2bids --study_dir=$STUDYDIR \
                  --code_dir=$CODEDIR --id=$sID \
                  --heuristic_file=$heuristics_file \
                  --convert

# Validate rawdata
7Tbids_validate --study_dir=$STUDYDIR
```

### TODO:
- Change nifti2bids -> dicom2bids
- Remove code directory as input. Instead assume that there is a code directory where the file is stored. Add this to documentation.
- Make the default that `dicomdir` lives under `studydir` if not provided as input. If input provided, then use that one.
- Subject ID is 7T049XXX, the full string, and not only S02 for instance. Change this. Participant ID is then sub-<SUBJECT_ID>, e.g., sub-7T049S02
