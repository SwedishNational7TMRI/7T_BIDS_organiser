#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base dicomdir sourcedir sID [options]
  Arrangement of DICOMs into organised folders in /sourcedata folder.
  Assuming that the dicomdir is stored as a subfolder in the study directory
  
  Required arguments:
  -q folder      Study directory
  -i sID				 Subject ID (e.g. 107)
  
  Options:
  -h / -help / --help           Print usage.
"
  exit;
}

################ ARGUMENTS ################
[ $# -ge 1 ] || { usage; }

# Defaults
studydir=
sID=
studykey=
verbose=0

while getopts "q:i:vh" o; do
  case "${o}" in
  i)
    sID=${OPTARG}
    ;;
  q)
    studydir=${OPTARG}
    ;;
  v)
    verbose=1
    ;;
  h)
    usage
    ;;
  *)
    usage
    ;;
  esac
done

sourcedir=$studydir/sourcedata
dicomdir=$studydir/dicomdir

if [ -z $dicomdir ]; then
  echo "Need to specify dicomdir"
fi

if [ -z $sourcedir ]; then
  echo "Need to specify sourcedir"
fi

if [ -z $sID ]; then
  echo "Need to specify subject ID"
fi

scriptname=`basename $0 .sh`
folder_id=$sID

################ PROCESSING ################

# Logging
logdir=$sourcedir/logs/sub-${sID}
if [ ! -d $logdir ]; then 
  mkdir -p $logdir
fi
echo "Executing $0 $@ "> $logdir/sub-${sID}_$scriptname.log 2>&1 
cat $0 >> $logdir/sub-${sID}_$scriptname.log 2>&1 

# Re-arrange DICOMs into /sourcedata
if [ ! -d $sourcedir ]; then 
  mkdir -p $sourcedir; 
fi

logfile=$logdir/sub-${sID}_$scriptname.log
cmd="dcm2niix -v 0 -b o -r y -w 0 -o $sourcedir -f sub-$sID/s%2s_%d/%d_%5r.dcm $dicomdir/${folder_id}"

if [ "$verbose" ]; then
  $cmd | tee $logfile
else
  $cmd >> $logfile 2>&1 
fi
