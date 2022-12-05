"""
Tool to fix errors in BIDS structure
"""

import argparse
from .pipeline import task_runner
import sys

def parse_inputs():
    parser = argparse.ArgumentParser(description = "process BIDS data from 7T Philips MRI")
    parser.add_argument('-v', '--verbose',  action='store_true', default=False)
    parser.add_argument('-c', '--config', default=None, type=str)
    parser.add_argument('-t', '--task', nargs=1, default=None, type=str)
    parser.add_argument('-d', '--dummy', action='store_true', default=False)
    parser.add_argument('subj_list', nargs='*')
    args = parser.parse_args()

    return args

def main():
    
	args = parse_inputs()
	runner = task_runner(args.config, args.task, dummy=args.dummy, verbose=args.verbose)
	
	if (args.subj_list == []) and (args.config == None):
		sys.exit("Either subject list or config file must be set")
	elif (args.subj_list == []):
		print("using subject list from conf: " + str(runner.config["subj_list"]))
		subj_list = runner.config["subj_list"]
	else:
		subj_list = args.subj_list

	for subj in subj_list:
		runner.run_subject(subj)

    

if __name__ == '__main__':
    main()