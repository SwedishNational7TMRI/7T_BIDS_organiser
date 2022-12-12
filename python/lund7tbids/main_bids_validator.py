import argparse
import os
import subprocess as sp


def parse_inputs():
    parser = argparse.ArgumentParser(description='BIDS Validator')
    parser.add_argument('--rawdata_dir', help='BIDS directory', type=str, required=True)    
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    rawdata_dir = args.rawdata_dir
    module_path = os.path.dirname(__file__)

    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_validate_docker.sh')
    cmd = f'sh {cmd} {rawdata_dir}'
    sp.call(cmd, shell=True)

if __name__ == '__main__':
    main()
