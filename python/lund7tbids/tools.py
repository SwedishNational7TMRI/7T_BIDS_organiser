import os
import subprocess as sp
from . import bids_util
from .pipeline import task_runner

def run_make_bids(study_dir, heuristic_file, subj_id,
                        do_organize=False, do_convert=False, do_validate=False, docker=False, verbose=False):

    module_path = os.path.dirname(__file__)
    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_dicom2bids.sh')
    cmd = f"sh {cmd} -i {subj_id} -q {study_dir} -f {heuristic_file}"
    if do_organize:
        cmd += " -1"
    if do_convert:    
        cmd += " -2"
    if do_validate:
        cmd += " -3"
    if docker:
        cmd += " -d"
    print(cmd)
    sp.call(cmd, shell=True)

def run_import_dicoms(study_dir, subj_id, verbose=False):
    module_path = os.path.dirname(__file__)
    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_sort_dicoms.sh')
    cmd = f"bash {cmd} -i {subj_id} -q {study_dir}"
    sp.call(cmd, shell=True)

def bids_remove_file(study_dir, subj_id, filename, config, verbose=False):
    runner = task_runner(study_dir, json_config=config, verbose=verbose)
    runner.subj = subj_id
    runner.task_list = ['fix_bids']
    runner.cur_task = 'fix_bids'

    # Find filename ending
    fbase, ext = os.path.splitext(filename)
    if ext == '.gz':
        fbase, ext2 = os.path.splitext(fbase)
        ext = ext2 + ext

    # Load the scanfile
    bids_util.load_original_scans(runner)
    # Remove the file entry
    bids_util.delete_scan_file(fbase + ext)
    bids_util.save_new_scans(runner)

    
    for fext in [ext, '.json']:
        try:
            fname_to_remove = os.path.join(study_dir, 'rawdata', 'sub-'+subj_id, fbase+fext)
            print(f"Removing {fname_to_remove}")
            os.remove(fname_to_remove)
        except FileNotFoundError:
            print(f"File {fname_to_remove} not found")
            pass
        