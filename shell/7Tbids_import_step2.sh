#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base sID [options]
    Conversion of DCMs in /sourcedata into NIfTIs in /rawdata
    1. NIfTI-conversion to BIDS-compliant /rawdata folder
    2. validation of BIDS dataset

    Required arguments:
    -i sID				      Subject ID (e.g. 107) 
    -f heuristics file
    
    Options:
    -o            Organize data
    -c            Convert data
    -v            Validate
    -h / -help / --help           Print usage.
  "
  exit;
}

################ ARGUMENTS ################

[ $# -ge 1 ] || { usage; }
command=$@

sID=
studykey=
organize=0
convert=0
validate=0
heuristics_file=

while getopts "i:f:covh" opt; do
  case "${opt}" in
  i)
    sID=${OPTARG}
    ;;
  o)
    organize=1
    ;;
  f)
    heuristics_file=${OPTARG}
    ;;
  c)
    convert=1
    ;;
  v)
    validate=1
    ;;
  h)
    usage
    ;;
  *)
    usage
    ;;
  esac
done


if [ -z $sID ]; then
  echo "Need to specify subject ID"
  exit
fi

if [ -z $heuristics_file ]; then
  echo "Need to specify heuristics file"
  exit
fi


# Define Folders
codedir=$CODEDIR_7TBIDS
studydir=$STUDYDIR_7TBIDS

rawdatadir=$studydir/rawdata;
sourcedatadir=$studydir/sourcedata;
scriptname=`basename $0 .sh`
logdir=$studydir/derivatives/logs/sub-${sID}

if [ ! -d $rawdatadir ]; then 
  mkdir -p $rawdatadir
fi

if [ ! -d $logdir ]; then
  mkdir -p $logdir
fi

# We place a .bidsignore here
if [ ! -f $rawdatadir/.bidsignore ]; then
  echo -e "# Exclude following from BIDS-validator\n" > $rawdatadir/.bidsignore;
fi

userID=$(id -u):$(id -g)

################ PROCESSING ################

# 1. Organize
if [ "$organize" ]; then
  echo "--- Organizing data ---"
  docker run --name heudiconv_container \
           --user $userID \
           --rm \
           -it \
           --volume $studydir:/base \
	         --volume $codedir:/code \
           --volume $sourcedatadir:/dataIn:ro \
           --volume $rawdatadir:/dataOut \
           --volume $
           nipy/heudiconv \
               -d /dataIn/sub-{subject}/*/*.dcm \
               -f /code/7T049_CVI_heuristic.py \
               -s ${sID} \
               -c none \
               -b \
               -o /dataOut \
               --overwrite \
           > $logdir/sub-${sID}_$scriptname.log 2>&1 
fi

# 2. Convert
if [ "$convert" ]; then
  docker run --name heudiconv_container \
            --user $userID \
            --rm \
            -it \
            --volume $studydir:/base \
      --volume $codedir:/code \
            --volume $sourcedatadir:/dataIn:ro \
            --volume $rawdatadir:/dataOut \
            nipy/heudiconv \
                -d /dataIn/sub-{subject}/*/*.dcm \
                -f /code/7T049_CVI_heuristic.py \
                -s ${sID} \
                -c dcm2niix \
                -b \
                -o /dataOut \
                --overwrite \
            > $logdir/sub-${sID}_$scriptname.log 2>&1 
fi

# 3. BIDS validator
if [ "$validate" ]; then
  docker run --name BIDSvalidation_container \
            --user $userID \
            --rm \
            --volume $rawdatadir:/data:ro \
            bids/validator \
                /data \
            > $studydir/derivatives/bids-validator_report.txt 2>&1
fi

           
# # heudiconv makes files read only
# #    We need some files to be writable, eg for defacing
# # (11 May) Commented out
# #chmod -R u+wr,g+wr $rawdatadir
