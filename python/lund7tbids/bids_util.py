import os
import glob
import json
import pydicom
import pandas as pd

"""
various utility functions to clean up the implementation of 
fix_bids_tree.py
"""

#global vars used by the log function
verbose = False
task_log = None

def update_log(arg_log_handle, arg_verbose):
	"""
	called from the log_item created by task_runner when a new task 
	is started, will provide a file handle that log messages will be 
	written to.  
	arguments:
		- arg_log_handle: file handle to opened writable log file
		- arg_verbose: task_runners current verbose config option
	"""
	global task_log, verbose
	task_log = arg_log_handle
	verbose = arg_verbose
	
def log_print(msg, force = False):
	"""
	print a log message to the log, and the terminal if verbose mode. 
	also print if force argument is true. 
	arguments:
		- msg: message string
		- force: optional bool flag to force terminal printing. 
			typically used for errors that shouldnt be ignored. 
	"""
	do_print = verbose or force
	try:
		task_log.write(f"{msg}\n")
	except:
		#cannot log with no current task in progress, just print
		do_print = True
	if do_print:
		print(msg) 

#update the BIDS json file
def update_json_shape(nii, input_json_file, output_json_file):
	"""
	function to write a json file to disc that updates the dimension 
	of the dcmmeta_shape value to match the new nifti file data shape. 
	does not change any other values in the json file, but might 
	change newlines and whitespace. 
	
	arguments:
		- nii: nifti file to read data shape from
		- input_json_file: original json input file to use as template
		- output_json_file: destination to disk of new json file
	"""
	input_json = open(input_json_file)
	json_dict = json.load(input_json)
	input_json.close()
	#update the json dict according to nii header
	nii_data = nii.get_fdata()
	json_dict["dcmmeta_shape"] = nii_data.shape
	out_file = open(output_json_file, "w")
	json.dump(json_dict, out_file, indent=2)
	out_file.close()

#used when writing the scans.tsv files
bids_out = ""
scans_lines = []
subj = ""
def load_original_scans(bids_out_arg, subj_arg):
	"""
	Load the original list of files in scans.tsv to a buffer that can 
	be modified before writing back to disk.
	arguments:
		- bids_out_arg: root of new bids tree
		- subj_arg: subject ID string
	"""
	global scans_lines, bids_out, subj
	bids_out = bids_out_arg
	subj = subj_arg
	scans = "{}/{}/{}_scans.tsv".format(bids_out, subj, subj)
	f = open(scans, 'r')
	scans_lines = f.readlines()
	f.close()

def save_new_scans(runner):
	global scans_lines
	"""
	Save the updates list of files in a new <subj>_scans.tsv, after
	the buffer has been modified 
	arguments
		-runner: parent task runner
	"""
	bids_out = runner.get_task_conf("bids_output")
	scans = "{}/{}/{}_scans.tsv".format(bids_out, runner.subj, runner.subj)
	with open(scans, 'w') as f:
		for line in scans_lines:
			f.write(f"{line}")

def delete_scan_file(f):
	"""
	Delete one filename and its row from <subj>_scans.tsv buffer
	arguments:
		- f: filename as described from subject folder as root. 
	"""
	global scans_lines, new_lines
	new_lines = [] 
	for line in scans_lines:
		line_file, rest_line  = line.split('\t', 1)
		if(f == line_file):
			log_print("--Removed " + f + " from scans.tsv")
		else:
			new_lines.append(line)
	scans_lines = new_lines
	
def rename_scan_file(src, dests):
	"""
	Rename one filename and its row from <subj>_scans.tsv buffer
	Can have several target destination filenames, resulting in
	copying the original row several times. 
	arguments:
		- src: target source filename as described from subject folder as root. 
		- dests: list of filenames that the old will be reinserted with.
		use list of one filename if doing a simple rename only, 
		use several names if one file has been split into multiple.  
	"""
	global scans_lines, new_lines
	new_lines = []
	found = False 
	for line in scans_lines:
		line_file, rest_line  = line.split('\t', 1)
		if(src == line_file):
			for dest in dests:
				log_print("--Renamed " + src + " to " + dest)
				line = dest + "\t" + rest_line 
				found = True
				new_lines.append(line)
		else:
			new_lines.append(line)
	scans_lines = new_lines
	if not found:
		log_print("Error: rename_scan_file didnt find " + src, force=True)

def set_epi_json_settings(json_file, dcm_file, phase_enc_dir):
	"""
	read DICOM files to calculate total readout time according to 
	https://osf.io/xvguw/wiki/home/?view_only=6887e555825743c7bbdfce114500fb8d
	also set the PhaseEncodingDirection to the correct value. 
	
	arguments.
		- json_file: file to edit
		- dcm_file: dicom to read scanner data from 
		- phase_enc_dir: the phase direction: [i, j, k, i-, j-, or k-] 
	"""
	log_print("updating {} using {} header".format(json_file, dcm_file))
	input_json = open(json_file)
	json_file_temp = json_file + ".tmp"
	json_dict = json.load(input_json)
	input_json.close()
	
	ds = pydicom.read_file(dcm_file)
	water_fat_shift = ds[0x2001, 0x1022].value #'WaterFatShift'
	imag_freq = ds[0x0018, 0x0084].value #'ImagingFrequency'
	epi_factor = ds[0x2001, 0x1013].value #'EPIFactor'
	actual_echo_spacing = water_fat_shift / (imag_freq * 3.4
							* (epi_factor + 1))
	total_readout_time = actual_echo_spacing * epi_factor
	log_print("calculated total readout time as " +  str(total_readout_time))

	json_dict["PhaseEncodingDirection"] = phase_enc_dir
	json_dict["TotalReadoutTime"] = total_readout_time
	out_file = open(json_file_temp, "w")
	json.dump(json_dict, out_file, indent=2)
	out_file.close()
	os.rename(json_file_temp, json_file)

def update_epi_json_files(search_path_minus_se_dir, dicom_dir, ap_phase_dir):
	"""
	arguments:
		- search path_minus_se_dir: the wildcard path to look for json files
			up until the AP/PA which is added
		- dcm_search_path: the dicom directory for this folder to be processed
		- ap_phase_enc: the phase direction for AP scans: [i, j, k, i-, j-, or k-] 
	"""
	phase_dirs = { "AP": ap_phase_dir }
	if (len(ap_phase_dir) == 2):
		phase_dirs["PA"] = ap_phase_dir[0]
	elif (len(ap_phase_dir) == 1):
		phase_dirs["PA"] = ap_phase_dir + "-"
	else:
		raise Exception("illegal ap_phase_enc_dir in json config")
	search_path = search_path_minus_se_dir
	for se_dir in ("AP", "PA"):
		json_list = glob.glob(search_path + "*" + se_dir + "*.json")
		if(len(json_list) > 0):
			dcm_file = glob.glob(dicom_dir + "*.dcm")[0]
			for json_file in json_list:
				set_epi_json_settings(json_file, dcm_file, phase_dirs[se_dir])

def wildcard_delete(f_wc):
	"""
	deletes one or more files that match the filename passed
	Inputs:
		- f_wc: a file name that can include wildcard characters
				to match one or several files
	
	"""
	#support wildcards
	log_print("deleting " + f_wc)
	matching_files = glob.glob(f_wc)
	# Iterate over the list of filepaths & remove each file.
	f_ct = 0
	for f in matching_files:
		try:
			os.remove(f)
			f_ct += 1
			p1, p2, scans_name  = f.split('/', 2)
			#try to remove the deleted file from <subj>_scans.tsv
			#this will fail for json files, but no matter. 
			delete_scan_file(scans_name)
		except:
			pass
	log_print(str(f_ct) + " files deleted")
	

def find_subject(tsv_file, subj):
	"""
	Make sure 
	arguments:
		- tsv_file: path to participants.tsv
		- subj: subject to find 
	returns True if found, else false
	"""
	part_df = pd.read_csv(tsv_file, sep='\t', header=0)
	participants = list(part_df['participant_id'])

	for p in participants:
		if p == subj:
			return True
	
	return False
