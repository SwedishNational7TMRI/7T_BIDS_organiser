#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base dicomdir sourcedir sID [options]
  Arrangement of DICOMs into organised folders in /sourcedata folder
  
  Required arguments:
  -d dicomdir    Directory of unordered dicoms (input)
  -i sID				 Subject ID (e.g. 107) 
  
  Options:
  -k			Key to translate MIPP running number into study Subject ID (BIDS), but if not provided MIPP running number = study Subject ID
  -h / -help / --help           Print usage.
"
  exit;
}

################ ARGUMENTS ################
[ $# -ge 1 ] || { usage; }

sourcedir=$STUDYDIR_7TBIDS/{sourcedata}
dicomdir=
sID=
studykey=
verbose=0

while getopts "d:s:i:k:vh" o; do
  case "${o}" in
  d)
    dicomdir=${OPTARG}
    ;;
  i)
    sID=${OPTARG}
    ;;
  k)
    studykey=${OPTARG}
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
folder_id=
if [[ ! -f $studykey ]]; then
	echo "No studykey file, folder = sID = $sID"
	folder_id=$sID;
else
	folder_id=`cat $studykey | grep $sID | awk '{ print $2 }'`
	if [[ $sID == "" ]]; then
		echo "Study Key file provided but no entry for $sID in $studykey"
		exit;
	fi
fi


################ PROCESSING ################

# Logging
logdir=$sourcedir/logs/sub-${sID}
if [ ! -d $logdir ]; then 
  mkdir -p $logdir
fi
echo "Executing $0 $@ "> $logdir/sub-${sID}_$scriptname.log 2>&1 
cat $0 >> $logdir/sub-${sID}_$scriptname.log 2>&1 

# Re-arrange DICOMs into sourcedata
if [ ! -d $sourcedir ]; then 
  mkdir $sourcedir; 
fi

logfile=$logdir/sub-${sID}_$scriptname.log
cmd="dcm2niix -b o -r y -w 0 -o $sourcedir -f sub-$sID/s%2s_%d/%d_%5r.dcm $dicomdir/${folder_id}"

if [ "$verbose" ]; then
  $cmd | tee $logfile
else
  $cmd >> $logfile 2>&1 
fi
