import os
import subprocess as sp

def run_make_bids(study_dir, code_dir, heuristic_file, subj_id,
                        do_organize=False, do_convert=False, do_validate=False, docker=False, verbose=False):

    module_path = os.path.dirname(__file__)
    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_import_step2.sh')
    cmd = f"sh {cmd} -i {subj_id} -q {study_dir} -c {code_dir} -f {heuristic_file}"
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

def run_import_dicoms(dicom_dir, study_dir, subj_id, study_key=None, verbose=False):
    module_path = os.path.dirname(__file__)
    cmd = os.path.join(module_path, '..', '..', 'shell', '7Tbids_sort_dicoms.sh')
    cmd = f"sh {cmd} -d {dicom_dir} -i {subj_id} -q {study_dir}"
    if study_key:
        cmd += f" -k {study_key}"
    
    sp.call(cmd, shell=True)