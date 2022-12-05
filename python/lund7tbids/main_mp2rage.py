import argparse
import subprocess as sp
from .tools import run_import_dicoms

def parse_inputs():
    parser = argparse.ArgumentParser(description='Process MP2RAGE')
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    parser.add_argument('--params', help='Sequence parameters (.json file)', type=str, required=True)
    parser.add_argument('--cat12', help='Run cat 12. Includes background removal', action='store_true')
    parser.add_argument('--b1', help='B1-map. Needs to be registered', action='store_true')
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    study_dir = args.study_dir
    subj_id = args.id
    run_cat12 = args.cat12
    verbose = args.v

    

if __name__ == '__main__':
    main()