#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base sID study directory
    Validate BIDS structure
    
    Options:
    -h / -help / --help           Print usage.
  "
  exit;
}

studydir=$1
userID=$(id -u):$(id -g)

rawdatadir=$studydir/rawdata
scriptname=`basename $0 .sh`

logfile=$logdir/${scriptname}_validate.log
docker run --name BIDSvalidation_container \
          --user $userID \
          --rm \
          --volume $rawdatadir:/data:ro \
          bids/validator \
              /data \
          | tee $logfile
