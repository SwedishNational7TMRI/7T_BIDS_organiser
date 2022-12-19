import argparse
import subprocess as sp
from .tools import bids_remove_file


def parse_inputs():
    parser = argparse.ArgumentParser(description='Remove file')
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    
    parser.add_argument('--folder', help='Folder to remove file from')
    parser.add_argument('--fname', help='Filename to remove')
    parser.add_argument('-c', help='Config file')
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()

    bids_remove_file(study_dir=args.study_dir,
                    subj_id=args.id,
                    filename=args.fname,
                    config=args.c,
                    verbose=args.v)

if __name__ == '__main__':
    main()