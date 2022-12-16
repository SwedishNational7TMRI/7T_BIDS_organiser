#!/bin/bash

usage()
{
  base=$(basename "$0")
  echo "usage: $base bids_dir log_file
    Validate BIDS structure
    
    Options:
    -h / -help / --help           Print usage.
  "
  exit;
}

userID=$(id -u):$(id -g)

rawdatadir=$1
logfile=$2
scriptname=`basename $0 .sh`

# check if logfile exists
if [ -e $logfile ]; then
  echo "Logfile $logfile exists. Exiting."
  rm $logfile
fi
touch $logfile

docker run --name BIDSvalidation_container \
          --user $userID \
          --rm \
          --volume $rawdatadir:/data:ro \
          bids/validator \
              /data \
          | tee $logfile

echo "\n\nlogging finished  at" `date` >> $logfile
echo "Validated the following folder: " $rawdatadir >> $logfile