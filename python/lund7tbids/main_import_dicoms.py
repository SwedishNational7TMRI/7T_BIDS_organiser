import argparse
import subprocess as sp
from .tools import run_import_dicoms

def parse_inputs():
    parser = argparse.ArgumentParser(description='Import DICOMS')
    parser.add_argument('--dicom_dir', help='DICOM directory', type=str, required=True)
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    parser.add_argument('--key', help='Study key', type=str)
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    dicom_dir = args.dicom_dir
    study_dir = args.study_dir
    subj_id = args.id
    study_key = args.key
    verbose = args.v

    run_import_dicoms(dicom_dir=dicom_dir, 
                    study_dir=study_dir,
                    subj_id=subj_id, 
                    study_key=study_key, 
                    verbose=verbose)

if __name__ == '__main__':
    main()