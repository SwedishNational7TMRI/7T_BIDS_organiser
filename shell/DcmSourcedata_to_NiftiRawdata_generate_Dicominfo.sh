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
3. Run of MRIQC on structural data

Arguments:
  sID				Subject ID (e.g. 107) 
Options:
  -h / -help / --help           Print usage.
"
  exit;
}

################ ARGUMENTS ################

[ $# -ge 1 ] || { usage; }
command=$@
sID=$1

shift
while [ $# -gt 0 ]; do
    case "$1" in
	-h|-help|--help) usage; ;;
	-*) echo "$0: Unrecognized option $1" >&2; usage; ;;
	*) break ;;
    esac
    shift
done

# Define Folders
codedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
studydir=`pwd` #studydir=`dirname -- "$codedir"`
rawdatadir=$studydir/rawdata;
sourcedatadir=$studydir/sourcedata;
scriptname=`basename $0 .sh`
logdir=$studydir/derivatives/logs/sub-${sID}

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

################ PROCESSING ################

###   Extract DICOMs into BIDS:   ###
# The images were extracted and organized in BIDS format:

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
               -c none \
               -b \
               -o /dataOut \
               --overwrite \
           > $logdir/sub-${sID}_$scriptname.log 2>&1 
           
