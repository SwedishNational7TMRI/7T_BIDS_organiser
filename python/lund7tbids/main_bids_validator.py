import argparse
import os
import subprocess as sp
import datetime

def parse_inputs():
    parser = argparse.ArgumentParser(description='BIDS Validator')
    parser.add_argument('bids_directory', help='BIDS directory', type=str)
    parser.add_argument('--log', help='Log directory', type=str, default=None)
    parser.add_argument('-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    bids_directory = args.bids_directory
    module_path = os.path.dirname(__file__)

    #hack: assume study dir is parent of bids data dir 
    if not args.log:
        logdir = os.path.join(bids_directory, '..', 'derivatives', 'logs')
        #filename with current time
        now = datetime.datetime.now()
        logfile = os.path.join(logdir, f'7Tbids_validate_docker_{now.strftime("%Y%m%d_%H%M%S")}.log')

    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_validate_docker.sh')
    cmd = f'sh {cmd} {bids_directory} {logfile}'
    sp.call(cmd, shell=True)

if __name__ == '__main__':
    main()
