import argparse
import subprocess as sp
from .tools import run_import_dicoms

def parse_inputs():
    parser = argparse.ArgumentParser(description='Import DICOMS')
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    study_dir = args.study_dir
    subj_id = args.id
    verbose = args.v
    run_import_dicoms(study_dir=study_dir,subj_id=subj_id,verbose=verbose)

if __name__ == '__main__':
    main()
