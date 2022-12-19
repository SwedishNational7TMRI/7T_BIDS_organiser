# 7T BIDS organiser
Bash and python scripts to convert DICOM data from the 7T into [BIDS-organised](https://bids.neuroimaging.io/) NIfTI data.

The BIDS specification/standard is preferably browsed [online](https://bids-specification.readthedocs.io/en/stable/). A BIDS-organised `studydir` for a neuroimaging study can look like
```sh
/studydir
    ├── code        <= Any code or misc files you need
    ├── derivatives <= Processed data
    ├── sourcedata  <= DICOM images 
    ├── rawdata     <= BIDS organised NIfTI images
    ├── sequences
    └── stimuli
```
Note, the only folder that needs to be truly [BIDS compliant](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html) is the `/rawdata` folder and its compliancy to the BIDS standard should be checked with a [BIDS validator](https://github.com/bids-standard/bids-validator). There is also a tool in this repository for doing this check.

This is an example of what the subject structure looks like for a single session and single subject.
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
- `7Tbids_import_dicoms`: Takes dicoms from an unsorted `dicomdir` and puts them in a organised folder structure `/sourcedata`.
- `7Tbids_nifti2bids`: Takes your data from dicoms to BIDS-organised structure with NIfTI files in the `/rawdata` folder using the [heudiconv](https://heudiconv.readthedocs.io/en/latest/) routine. This is done in two steps
    1. Call with option `--organize` to run `heudiconv` without conversion. Generates `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`.
    2. Call with option `--convert` to do the actual nifti conversion. This requires input to appropriate heuristics file (see above).
    - Both of these tools need a `heuristics` file. This is assumed to be stored in  `/code`.
    - Both of these tools can be called with the `--docker` option which runs heudiconv from the downloaded docker container.
- `7Tbids_validate`: Used to validate your BIDS tree structure.
- `7Tbids_remove`: Used to remove files after QC


The following folder structure and conventions are assumed to be used
- Original dicoms in `dicomdir`. These are "raw" DICOMS exported from the 7T archive. This folder will be used as inputs to some scripts and can be located anywhere.
    - Your DICOM data might be stored with run numbers instead of subject ID. To do this mapping you can use a `study_key.tsv` file. See example in this repository.
- Your `studydir` is the path to where you want your study data to be stored.
- It is recommended to store your own study code in a specific directory, `studydir/code`. Suggestions from the BIDS standard is to put is in `studydir/code`.
- Re-named and re-arranged dicoms will be stored in  `studydir/sourcedata`, which is the BIDS sourcedata-folder
- BIDS-organised NIfTIs in `studydir/rawdata`
- You need a heuristics file for `heudiconv`. This should be stored in your code-folder. See the `misc` folder here in the repo for example.

To convert data from raw DICOMS to a BIDS valid structure with NIFTI files it is recommended to set up a shell script with the following structure.

```sh
STUDYDIR=<my_bids_dir>
sID=<Study_ID>      #E.g. 7T049S02
heuristics_file=7T049_CVI_heuristic.py # This is assumed to live in STUDYDIR/code

DICOMDIR=<my_dicom_dir>
# dicomdir -> sourcedata
7Tbids_import_dicoms --dicom_dir=$DICOMDIR --study_dir=$STUDYDIR --id=$sID

# Organize and analyze sourcedata folder
# creates temp_rawdata and maps which images goes where
7Tbids_nifti2bids --study_dir=$STUDYDIR \
                  --id=$sID \
                  --heuristic_file=$heuristics_file \
                  --organize

# Convert to nifti
# Converts from dicom to nifti and populates temp_rawdata
7Tbids_nifti2bids --study_dir=$STUDYDIR \
                  --id=$sID \
                  --heuristic_file=$heuristics_file \
                  --convert

# temp_rawdata contains a non-bids compliant tree.
# This command will fix issues in the bidstree
# for this you need to specify a configuration file with -c
# The pipeline configuration file is also assumed to live under studydir/code. Explanation for this file below
# The fix_bids command will create a rawdata directory that is bids-compliant from which all further analysis is performed
7Tbids_fix_bids -v --study_dir=$STUDYDIR -c pipeline_conf.json --id=$SUB

# At this point you want to do some QC on your data. Decide which scans to discard and remove with command below
# This will remove the nii.gz+json files from rawdata and the entry from the .tsv file
7Tbids_remove --study_dir=$STUDYDIR --id=$SUB \
                --fname anat/sub-7T049S02_run-2_FLAIR.nii.gz \
                -c pipeline_conf.json

# Final step is to validate the rawdata directory
# Here you pass in the directory you want to run the validation on
7Tbids_validate -v ${STUDYDIR}/rawdata

# If you don't pass a logfile name to the validate command, it will make a logfile in the derivaties/log directory
# with a timestamp. 
```

## pipeline_conf.json
Explanation of `pipeline_conf.json`. You need to remove the comments (`<-`) before using this file.
```
{
"global": {
    "config_name": "test",	
    "orig_bids_root": "temp_rawdata", <- Where the "unfixed" bids is
    "deriv_folder": "derivatives", <- Where derivaties ends up
    "fix_bids": "rawdata", <- Name of the fixed data folder
    "spm12_path": "/Users/emil/Code/spm12", <- Path to SPM for analysis
    "freesurfer_license": "$FREESURFER_HOME/license.txt"
},
"fix_bids": {"bids_output": "rawdata", "epi_ap_ph_enc_dir": "j-"}, <- Specific options for fix bids
"mp2rage": {"bids_input": "rawdata", "out_folder": "spm12",  <- Specific options for mp2rage
            "spm12_ver": "2022"},
"mask_remove_bg": {"use_bet": true, "bet_intensity": 0.25, 
                    "use_quit": false},
"cat12": {"out_folder": "cat12", "cat12_ver": "r1450"},
"freesurfer": {"out_folder": "freesurfer", "fs-version": 0.1, "threads": 10}
}

```

### TODO:
- Change nifti2bids -> dicom2bids
- Remove code directory as input. Instead assume that there is a code directory where the file is stored. Add this to documentation.
- Subject ID is 7T049XXX, the full string, and not only S02 for instance. Change this. Participant ID is then sub-<SUBJECT_ID>, e.g., sub-7T049S02

# Running on mac
Most of these tools runs well on a mac, except some of the scripts in the `linescanning` repo. These uses the `readlink` command which works differently on linux and mac. You can install the linux type `readlink` tool from `brew` and then symlink it to fix it (although I have not been able to do this successfully yet (Emil Ljungberg))

Install readlink with brew
1. Install the coreutils package: `brew install coreutils`
2. Create an Alias or Symlink
    - You can place your alias in ~/.bashrc, ~/.bash_profile, or wherever you are used to keeping your bash aliases. I personally keep mine in ~/.bashrc
    - alias readlink=greadlink