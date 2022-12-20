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
Note, the only folder that needs to be truly [BIDS compliant](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html) is the `/rawdata` folder and its compliancy to the BIDS standard should be checked with a [BIDS validator](https://github.com/bids-standard/bids-validator), or the [online BIDS validator](https://bids-standard.github.io/bids-validator/). There is also a tool in this repository for doing this check.

This is an example of what the BIDS folder/file structure looks like for a single subject S01 with only one scans (session-level can be omitted):
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
or in the case of two sessions (pre and post):
```sh
/studydir
    └── rawdata
            ├── CHANGES
            ├── dataset_description.json
            ├── participants.json
            ├── participants.tsv
            ├── README
            ├── sub-S01
            │   └──ses-pre
	    │	│  ├── anat
            │   │  ├── dwi
            │   │  ├── fmap
            │   │  ├── func
            │   │  ├── sub-S01_ses-pre_scans.json
            │   │  └── sub-S01_ses-pre_scans.tsv
	    │	└──ses-post
	    │	   ├── anat
            │      ├── dwi
            │      ├── fmap
            │      ├── func
            │      ├── sub-S01_ses-post_scans.json
            │      └── sub-S01_ses-post_scans.tsv  
            └── task-rest_bold.json
```



## Dependencies
- Python 3.8. Suggest using a anaconda environment (here called `py38`)
```
conda create -n py38 python=3.8
```
- SPM
- Cat12. User version r1450 from this [download link](http://141.35.69.218/cat12/cat12_r1450.zip). See notes about SPM and CAT12 on mac below.
- To download the necessary docker containers execute
```sh
shell download_docker.sh
```

## Installation
This software is best used as a python package which is installed using `pip`. Python 3.8 or higher is required. Recommended that you do this in a an isolated conda or virtual environment. To install, navigate to the main directory and execute
```sh
python -m pip install -e .
```

After you have installed the python package you will have a set of tools available:
- `7Tbids_import_dicoms`: Takes dicoms from an "unsorted" DICOM directory and puts them in a organised folder structure `studydir/sourcedata`.
It is encouraged to use this conversion as it facilitates trouble-shooting and human readibility of your DICOM data. 
- `7Tbids_dicom2bids`: Takes your data from dicoms to BIDS-organised structure with NIfTI files in the `/rawdata` folder using the [heudiconv](https://heudiconv.readthedocs.io/en/latest/) routine. This is done in two steps
    1. Call with option `--organize` to run `heudiconv` without conversion. Generates `/rawdata/.heudiconv/sub-$sID/dicominfo.tsv` which is used to generate a relevant heuristic file for input to `heudiconv`. The `--organize` step is typically only needed to run once to create a study-specific heuristic-file which can be used on all subjects in the study. 
    2. Call with option `--convert` to do the actual nifti conversion. This requires input to appropriate heuristics file (see above).
    - Both of these tools need a `heuristics` file. This is assumed to be stored in  `studydir/code`.
    - Both of these tools can be called with the `--docker` option which runs heudiconv from the downloaded docker container.
- `7Tbids_validate`: Used to validate your BIDS tree structure.
- `7Tbids_remove`: Used to remove files after QC


The following folder structure and conventions are assumed to be used
- Original dicoms in `dicomdir`. These are "raw" DICOMS exported from the 7T archive. This folder will be used as inputs to some scripts and can be located anywhere.
- Your `studydir` is the path to where you want your study data to be stored.
- It is recommended to store your own study code in a specific directory, `studydir/code`. Suggestions from the BIDS standard is to put is in `studydir/code`.
- Re-named and re-arranged dicoms will be stored in  `studydir/sourcedata`, which is the BIDS sourcedata-folder.
- BIDS-organised NIfTIs in `studydir/rawdata`
- You need a heuristics file for `heudiconv`. This should be stored in your code-folder, i.e. `studydir/code`. See the `misc` folder here in the repo for example.

To convert data from raw DICOMS to a BIDS valid structure with NIFTI files it is recommended to set up a shell script with the following structure.

```sh
STUDYDIR=<my_bids_dir>
sID=<Study_ID>      #E.g. 7T049S02
heuristics_file=7T049_CVI_heuristic.py # This is assumed to live in STUDYDIR/code
pipeline_file=$STUDYDIR/code/pipeline_conf.json # Full path to where you keep your pipeline_conf.json-file

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
7Tbids_fix_bids -v --study_dir=$STUDYDIR -c $pipeline_file --id=$sID

# At this point you want to do some QC on your data. Decide which scans to discard and remove with command below
# This will remove the nii.gz+json files from rawdata and the entry from the .tsv file
7Tbids_remove --study_dir=$STUDYDIR --id=$SUB \
                --fname anat/sub-7T049S02_run-2_FLAIR.nii.gz \
                -c pipeline_conf.json

# Final step is to validate the rawdata directory
# Here you pass in the directory you want to run the validation on
7Tbids_validate -v ${STUDYDIR}/rawdata


# To process MP2RAGE run
mp2rage_runnum=1
7Tbids_mp2rage --study_dir=$STUDYDIR --id=$SUB -c $pipeline_file --run $mp2rage_runnum

# From this command you want to use the file with the naming mi<subject>_run-<run>_desc-pymp2ragenoBackground_UNIT1.nii
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
"mp2rage": {"bids_input": "rawdata", 
				"out_folder": "spm12", 
				"spm12_ver": "2022",
				"params": {
				"MPRAGE_tr":5,
				"invtimesAB":[0.90, 2.750],
				"flipangleABdegree":[5, 3],
				"nZslices":[257],
				"FLASH_tr":[0.0068, 0.0068],
				"B0":7.0}
			},
"mask_remove_bg": {"use_bet": true, "bet_intensity": 0.25, 
                    "use_quit": false},
"cat12": {"out_folder": "cat12", "cat12_ver": "r1450"},
"freesurfer": {"out_folder": "freesurfer", "fs-version": 0.1, "threads": 10}
}

```

### TODO:
- Remove code directory as input. Instead assume that there is a code directory where the file is stored. Add this to documentation.

# Running on mac
Most of these tools runs well on a mac, except some of the scripts in the `linescanning` repo. These uses the `readlink` command which works differently on linux and mac. You can install the linux type `readlink` tool from `brew` and then symlink it to fix it (although I have not been able to do this successfully yet (Emil Ljungberg))

Install readlink with brew
1. Install the coreutils package: `brew install coreutils`. This will install a tool called `greadlink` which is equivalent to the UNIX command `readlink`
2. Create a symlink to `greadlink` using
```
sudo ln -s /opt/homebrew/bin/greadlink /opt/homebrew/bin/readlink
```
3. If you want to revert back to the MacOS version of readlink just remove the symlink with
```
sudo rm /opt/homebrew/bin/readlink
```

## spm
Your mac will put all your compiled mex files in quarantine, to avoid this you can try to prevent it with:
```
sudo xattr -r -d com.apple.quarantine CAT12_PATH
sudo xattr -r -d com.apple.quarantine SPM_PATH
sudo find CAT12_PATH -name \*.mexmaci64 -exec spctl --add {} \;
sudo find SPM_PATH -name \*.mexmaci64 -exec spctl --add {} \;
```
For more info see [this page](https://www.fieldtriptoolbox.org/faq/mexmaci64_cannot_be_opened_because_the_developer_cannot_be_verified/)
