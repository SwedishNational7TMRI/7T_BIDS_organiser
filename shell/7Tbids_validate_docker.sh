#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base sID study directory
    Validate BIDS structure
    
    Options:
    -d
    -h / -help / --help           Print usage.
  "
  exit;
}

userID=$(id -u):$(id -g)

rawdatadir=$1
scriptname=`basename $0 .sh`
#hack: assume study dir is parent of bids data dir 
logdir=$rawdatadir/../derivatives/logs
logfile=$logdir/${scriptname}_validate.log
docker run --name BIDSvalidation_container \
          --user $userID \
          --rm \
          --volume $rawdatadir:/data:ro \
          bids/validator \
              /data \
          | tee $logfile
