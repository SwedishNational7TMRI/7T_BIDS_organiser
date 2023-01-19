import argparse
import subprocess as sp
from .task_runner import task_runner

def parse_inputs():
    parser = argparse.ArgumentParser(description='Process MP2RAGE')
    parser.add_argument('--study_dir', help='Study directory', type=str, required=True)
    parser.add_argument('--id', help='Subject ID', type=str, required=True)
    parser.add_argument('--b1', help='B1-map. Needs to be registered', action='store_true')
    parser.add_argument('--run', help='Which run to process', type=int, default=1)
    parser.add_argument('-c', '--config', default=None, type=str)
    parser.add_argument('-v', help='Verbose output', action="store_true", default=False)
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()

    runner = task_runner(args.study_dir, task_arg=['mp2rage'], json_config=args.config, verbose=args.v)
    runner.run_subject(args.id, run_num=args.run)
    
    runner.task_list = ['mask_remove_bg']
    runner.run_subject(args.id, run_num=args.run)

    runner.task_list = ['cat12']
    runner.run_subject(args.id, run_num=args.run)

if __name__ == '__main__':
    main()
