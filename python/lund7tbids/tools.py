import os
import subprocess as sp

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