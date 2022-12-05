import argparse
import subprocess as sp
from .tools import run_make_bids


def parse_inputs():
    parser = argparse.ArgumentParser(description='Make BIDS Nifti structure')
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--heuristic_file', help='Heuristic file for heudiconv', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    
    parser.add_argument('--organize', help='Run organize step (1)', action='store_true')
    parser.add_argument('--convert', help='Run convert step (2)', action='store_true')
    parser.add_argument('--validate', help='Run validatino step (3)', action='store_true')
    parser.add_argument('--docker', help='Run with docker', action='store_true')
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    study_dir = args.study_dir
    heuristic_file = args.heuristic_file
    subj_id = args.id
    do_organize = args.organize
    do_convert = args.convert
    do_validate = args.validate
    verbose = args.v
    docker = args.docker

    run_make_bids(study_dir=study_dir,
                    heuristic_file=heuristic_file, 
                    subj_id=subj_id,
                    do_organize=do_organize,
                    do_convert=do_convert,
                    do_validate=do_validate,
                    docker=docker,
                    verbose=verbose)

if __name__ == '__main__':
    main()