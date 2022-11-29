#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base sID [options]
    Conversion of DCMs in /sourcedata into NIfTIs in /rawdata

    Required arguments:
    -i sID				      Subject ID (e.g. 107) 
    -q study directory
    -f heuristics file
    -c Code directory
    
    Options:
    -d            Run with docker
    -1            (1) Organize data
    -2            (2) Convert data
    -h / -help / --help           Print usage.
  "
  exit;
}

################ ARGUMENTS ################

[ $# -ge 1 ] || { usage; }
command=$@

sID=
studykey=
organize=
convert=
use_docker=
heuristics_file=
codedir=
studydir=

while getopts "i:q:f:c:123dh" opt; do
  case "${opt}" in
  i)
    sID=${OPTARG}
    ;;
  q)
    studydir=${OPTARG}
    ;;
  f)
    heuristics_file=${OPTARG}
    ;;
  c)
    codedir=${OPTARG}
    ;;
  d)
    use_docker=1
    ;;
  1)
    organize=1
    ;;
  2)
    convert=1
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
  heudi_opt="-s ${sID} -c none -b  --overwrite "
  logfile=$logdir/sub-${sID}_${scriptname}_organize.log
  if [ "$use_docker" ]; then
    echo "Using docker"
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
                -f /code/${heuristics_file} \
                -o /dataOut \
                $heudi_opt \
            | tee $logfile
  else
    heudiconv -d $sourcedatadir/sub-{subject}/*/*.dcm \
              -f $codedir/${heuristics_file} -o $rawdatadir \
              $heudi_opt | tee $logfile
  fi
fi

# 2. Convert
if [ "$convert" ]; then
  logfile=$logdir/sub-${sID}_${scriptname}_convert.log
  heudi_opt="-s ${sID} -c dcm2niix -b --overwrite"
  if [ "$use_docker" ]; then
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
                -f /code/${heuristics_file} \
                -o /dataOut \
                $heudi_opt \
            | tee $logdir/sub-${sID}_$scriptname.log
  else
    heudiconv -d $sourcedatadir/sub-{subject}/*/*.dcm -o $rawdatadir -f $codedir/${heuristics_file} \
              $heudi_opt | tee $logfile
  fi

fi

# 3. BIDS validator


# # heudiconv makes files read only
# #    We need some files to be writable, eg for defacing
# # (11 May) Commented out
# #chmod -R u+wr,g+wr $rawdatadir
