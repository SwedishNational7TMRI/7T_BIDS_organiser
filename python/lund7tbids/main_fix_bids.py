"""
Tool to fix errors in BIDS structure
"""

import argparse
from .task_runner import task_runner
import sys

def parse_inputs():
    parser = argparse.ArgumentParser(description = "process BIDS data from 7T Philips MRI")
    parser.add_argument('-v', '--verbose',  action='store_true', default=False)
    parser.add_argument('-c', '--config', default=None, type=str)
    parser.add_argument('-d', '--dummy', action='store_true', default=False)
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    args = parser.parse_args()

    return args

def main():
	args = parse_inputs()
	task = ['fix_bids']
	runner = task_runner(args.study_dir, json_config=args.config, task_arg=task, dummy=args.dummy, verbose=args.verbose)
	runner.run_subject(args.id)

if __name__ == '__main__':
    main()