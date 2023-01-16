#!/bin/bash
## 7T049 CVI/Visual Brain Study
#
usage()
{
  base=$(basename "$0")
  echo "usage: $base sID [options]
Conversion of DCMs in /sourcedata into NIfTIs in /rawdata
1. NIfTI-conversion to BIDS-compliant /rawdata folder
2. validation of BIDS dataset

Arguments:
  sID				Subject ID (e.g. 7T049S03)
Example:
./DcmSourcedata_to_NiftiRawdata.sh 7T049S03
Options:
  -heuristic                    Input heuristic file to heudiconv (default: $codedir/7T049_CVI_heuristic.py)
  -h / -help / --help           Print usage.
"
  exit;
}

################ ARGUMENTS ################

# Read required input arguments
[ $# -ge 1 ] || { usage; }
command=$@
sID=$1
shift

# Read optional input arguments
while [ $# -gt 0 ]; do
    case "$1" in
  	-heuristic) shift; heuristicfile=$1; ;;
    -h|-help|--help) usage; ;;
    -*) echo "$0: Unrecognized option $1" >&2; usage; ;;
    *) break ;;
    esac
    shift
done

# Define Folders
codedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#studydir=$PWD
studydir=`dirname -- "$codedir"`
rawdatadir=$studydir/rawdata;
#sourcedatadir=$studydir/sourcedata;
dicomdir=$studydir/dicomdir;  #use original dicom folder
scriptname=`basename $0 .sh`
logdir=$studydir/derivatives/logs/sub-${sID}

# Define Defaults
#heuristicfile=$codedir/heuristic.py

# Get location and name for heuristic file
#heuristicfiledir=`dirname $heuristicfile`
#heuristicfilename=`basename $heuristicfile`

if [ ! -d $rawdatadir ]; then mkdir -p $rawdatadir; fi
if [ ! -d $logdir ]; then mkdir -p $logdir; fi

# We place a .bidsignore here
if [ ! -f $rawdatadir/.bidsignore ]; then
echo -e "# Exclude following from BIDS-validator\n" > $rawdatadir/.bidsignore;
fi

# we'll be running the Docker containers as yourself, not as root:
userID=$(id -u):$(id -g)

###   Get docker images:   ###
docker pull nipy/heudiconv:latest
docker pull bids/validator:latest

################ PROCESSING ################

###   Extract DICOMs into BIDS:   ###
# The images were extracted and organized in BIDS format:

## Run multiple sessions
echo " | HEUDICONV is running with muliple sessions..."
echo " | subject:" ${sID}
# define sessions automatically
sessions=$(find $dicomdir/sub-${sID} -type d -maxdepth 1 -mindepth 1 | xargs -I {} basename {})
for sess in $sessions; do \
  echo "   session:" ${sess};
  docker run --name heudiconv_container \
             --user $userID \
             --rm \
             -i \
  	         --volume $codedir:/code \
             --volume $dicomdir:/dataIn:ro \
             --volume $rawdatadir:/dataOut \
             nipy/heudiconv \
                 -d /dataIn/sub-{subject}/{session}/*/*.dcm \
                 -f /code/heuristic.py \
                 -s ${sID} \
                 -ss ${sess} \
                 -c dcm2niix \
                 -b \
                 -o /dataOut \
                 --overwrite \
             > $logdir/sub-${sID}_ses-${sess}_$scriptname.log 2>&1;
done
echo " | ...done"


echo " | BIDS validator is running ..."
###   Run BIDS validator   ###
docker run --name BIDSvalidation_container \
           --user $userID \
           --rm \
           --volume $rawdatadir:/data:ro \
           bids/validator \
               /data \
           > $studydir/derivatives/bids-validator_report.txt 2>&1

echo " | ...done"
