#!/bin/bash
## 7T049_CVI/VisualBrain study
#
usage()
{
  base=$(basename "$0")
  echo "usage: $base sID [options]
  Arrangement of DICOMs into organised folders in /sourcedata folder
  
  Arguments:
  sID				MIPP running number (e.g. 107) 
  
  Options:
  -studykey			Key to translate MIPP running number into study Subject ID (BIDS), but if not provided MIPP running number = study Subject ID
  -h / -help / --help           Print usage.
"
  exit;
}

################ ARGUMENTS ################

# Defaults
studydir=$PWD
studykey=$studydir/dicomdir/MIPP_running_nbr_2_Study_ID.tsv

[ $# -ge 1 ] || { usage; }
command=$@
MIPPsID=$1

shift
while [ $# -gt 0 ]; do
    case "$1" in
	-h|-help|--help) usage; ;;
	-studykey) studykey=$1; ;;
	-*) echo "$0: Unrecognized option $1" >&2; usage; ;;
	*) break ;;
    esac
    shift
done

# Define Folders
codedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
origdcmdir=$studydir/dicomdir;
dcmdir=$studydir/sourcedata
scriptname=`basename $0 .sh`

if [[ ! -f $studykey ]]; then
	echo "No studykey file, sID = MIPPsID = $MIPPsID"
	sID=$MIPPsID;
else
	sID=`cat $studykey | grep $MIPPsID | awk '{ print $2 }'`
	if [[ $sID == "" ]]; then
		echo "Study Key file provided but no entry for $MIPPsID in $studykey"
		exit;
	fi
fi

################ PROCESSING ################

# Simple log
logdir=$studydir/derivatives/logs/sub-${sID}
if [ ! -d $logdir ]; then mkdir -p $logdir; fi
echo "Executing $0 $@ "> $logdir/sub-${sID}_$scriptname.log 2>&1 
cat $0 >> $logdir/sub-${sID}_$scriptname.log 2>&1 

# Re-arrange DICOMs into sourcedata
if [ ! -d $dcmdir ]; then mkdir $dcmdir; fi
dcm2niix -b o -r y -w 1 -o $dcmdir -f sub-$sID/s%2s_%d/%d_%5r.dcm $origdcmdir/${MIPPsID} \
	>> $logdir/sub-${sID}_$scriptname.log 2>&1 

