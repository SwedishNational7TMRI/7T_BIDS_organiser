
import json
import subprocess
import os
import nibabel as nib
import numpy as np
from . import bids_util
from .bids_util import log_print

	#fix 1a: separate the inversion times functions from notebooks
	 # call the code from the jupyter notebook here
	#fix 1b: remove the anat/sub-7T049C10_run-1_inv-1and2_part-real_MP2RAGE_heudiconv141_real.nii.gz
	#fix 1c: reshape data cube of UNIT1
	#fix 1d: create a 4dim cube of both real and imag data

class fix_anat:	
	"""
	class for fixing the anat folder
	"""
	
	def __init__(s, runner):
		"""put
		arguments: 
			- runner: task runner executing fix bids
		"""
		s.name = "anat"
		s.bids_out = runner.app_sd_on_task_conf("bids_output")
		s.subj = runner.subj
		long_subj = "sub-" + s.subj
		#first half of each bids fileanme
		s.root_folder = "{}/{}/{}/".format(s.bids_out, long_subj, s.name)
		s.part_filename = s.root_folder + long_subj

		s.nruns = bids_util.count_scans('_inv-1and2_MP2RAGE')
		print("Number of MP2RAGE runs: " + str(s.nruns))
		
		s.deriv_quit_folder = runner.get_deriv_folder("quit", "anat")
		
		#"./derivatives/quit/{}/anat".format(subj)
		s.sc_pre_str = "anat/{}".format(long_subj)
		
		s.quit_complex_input = s.deriv_quit_folder + "/{}_run-%d_inv_1and2_MP2RAGE".format(long_subj)
		#these are the files to be deleted
		s.blacklist=[s.part_filename + "*heudiconv*", 
					s.part_filename + "*inv-1and2*"]

	#update the BIDS json file
	def update_json_shape2(s, nii, input_json_file, output_json_file):
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
		json.dump(json_dict, out_file)
		out_file.close()

	def reshape_UNIT1_dims(s, run):
		"""
		function to change the shape of the UNIT1 mp2rage file. 
		a new nifty file will be written to disk that has the format
		(x,z,y) instead of (x,y,0,z)
		"""
		
		log_print("fixing the shape of UNIT1 mp2rage file")
		input_nii_file = s.part_filename + f"_acq-mp2rage_run-{run}_UNIT1.nii.gz"
		temp_file = ".UNIT1.nii.gz"
		os.rename(input_nii_file, temp_file)
		nii = nib.load(temp_file)
		nii_data = nii.get_fdata()
		
		new_data = np.zeros((nii_data.shape[0], nii_data.shape[1], nii_data.shape[3]))
		new_data = nii_data[:,:,0,:]
		nii_updated = nib.Nifti1Image(new_data, nii.affine)
		json_file = s.part_filename + f"_acq-mp2rage_run-{run}_UNIT1.json"
		json_file_temp = json_file + ".tmp"
		bids_util.update_json_shape(nii_updated, json_file, json_file_temp)
		u_xyz, u_t = nii.header.get_xyzt_units()
		nii_updated.header.set_xyzt_units(u_xyz, u_t)
		nib.save(nii_updated, input_nii_file)
		os.rename(json_file_temp, json_file)
		log_print("wrote " + input_nii_file)
		os.remove(temp_file)

	def get_separate_nii(s, input_nii_file, inv_index):
		nii = nib.load(input_nii_file)
		nii_data = nii.get_fdata()
		dual_header = nii.header
		inv_data = nii_data[:, :, :, inv_index]
		nii_inv = nib.Nifti1Image(inv_data, nii.affine)
		u_xyz, u_t = nii.header.get_xyzt_units()
		nii_inv.header.set_xyzt_units(u_xyz, u_t)
		return nii_inv

	def split_combined_niftis(s,run):
		"""
		create new nifti files based on the run-1_inv-1and2 files
		for each inversion time. 
		"""
		#lets assume we only have one run for now
		
		for part in ['real', 'imag']:
			i_prefix_file = s.part_filename + "_run-{}_inv-1and2_part-{}_MP2RAGE".format(run, part)
			input_nii_file = i_prefix_file + ".nii.gz" 
			input_json_file = i_prefix_file + ".json" 
			log_print("splitting " + input_nii_file)
			
			for inv_idx in [0, 1]:
				o_prefix_file = s.part_filename + "_run-{}_inv-{}_part-{}_MP2RAGE".format(run, inv_idx + 1, part)
				output_nii_file = o_prefix_file + ".nii.gz" 
				output_json_file = o_prefix_file + ".json" 
				log_print(o_prefix_file + ".nii.gz" )
				#convert inversion time 
				nii_sep = s.get_separate_nii(input_nii_file, inv_idx)
				#edit json
				bids_util.update_json_shape(nii_sep, input_json_file, output_json_file)
				#write new nii file
				nib.save(nii_sep, output_nii_file)

	def gen_T1_map_mp2rage(s, run):
		"""
			function to call the QUIT library to generate a better mp2RAGE
			image. 
			https://quit.readthedocs.io/en/latest/Docs/Relaxometry.html#qi-mp2rage
			
			#pass the json file to th e
			qi mp2rage input_file.nii.gz --mask=mask_file.nii.gz < mp2rage_parameters.json
		"""
		code_path = os.path.dirname(os.path.relpath(__file__))
		mp2rage_json_file = code_path + "/mp2rage_parameters.json"
		qi_cmd = "qi mp2rage {} < {}".format(s.quit_complex_input%run, mp2rage_json_file)
		s.runner.sh_run(qi_cmd)
		for out in ("UNI", "T1"):
			src = "MP2_{}.nii.gz".format(out)
			dest = s.deriv_quit_folder + "/sub-{}_acq-mp2rage_run-{}_{}.nii.gz".format(s.subj, run, out)
			os.rename(src, dest)	

	def execute(s):
		"""
			performs all fixes for anat folder and updates scans.tsv file.
		"""
		for run in range(1,s.nruns+1):
			s.split_combined_niftis(run)
			s.reshape_UNIT1_dims(run)
			
			#fix the <subj>_scans.tsv file
			bids_util.rename_scan_file(s.sc_pre_str + f"_run-{run}_inv-1and2_part-imag_MP2RAGE.nii.gz"
				, [s.sc_pre_str + f"_run-{run}_inv-1_part-imag_MP2RAGE.nii.gz",
				s.sc_pre_str + f"_run-{run}_inv-2_part-imag_MP2RAGE.nii.gz"])
			bids_util.rename_scan_file(s.sc_pre_str + f"_run-{run}_inv-1and2_part-real_MP2RAGE.nii.gz"
				, [s.sc_pre_str + f"_run-{run}_inv-1_part-real_MP2RAGE.nii.gz",
				s.sc_pre_str + f"_run-{run}_inv-2_part-real_MP2RAGE.nii.gz"])
			bids_util.rename_scan_file(s.sc_pre_str + f"_run-{run}_inv-1and2_MP2RAGE.nii.gz", [])
		
		#delete unwanted files
		for f in s.blacklist:
			bids_util.wildcard_delete(f)
