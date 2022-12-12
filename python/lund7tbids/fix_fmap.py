import os
import json
from . import bids_util
from .bids_util import log_print

class fix_fmap:
	"""
	class for fixing the fmap, called by fix_bids
	"""
	
	def __init__(s, runner):
		"""
		arguments: 
			- runner: task runner executing fix bids
		"""
		s.name = "fmap"
		s.bids_out = runner.app_sd_on_task_conf("bids_output")
		s.subj = runner.subj
		s.long_subj = "sub-" + s.subj
		#first half of each bids filename
		s.root_folder = "{}/{}/{}/".format(s.bids_out, s.long_subj, s.name)
		s.part_filename = s.root_folder + s.long_subj
		s.epi_ap_ph_enc_dir = runner.get_task_conf("epi_ap_ph_enc_dir")
		s.part_bold_name = "{}/{}".format("func", s.long_subj)
		s.dicom_dir = runner.study_dir + "/sourcedata/{}/*fmap*/".format(s.long_subj)
		s.sc_pre_str = "fmap/{}".format(s.long_subj)
		
		s.blacklist=[]
	
	def add_missing_gre_data(s):
		"""
		update GRE fieldmap file to have  Units = rad/s
		"""
		#TODO: make wrapper code for json config handling?
		#would need to put that in separate utility py script, or pass to constructor
		json_file = s.part_filename + "_acq-gre_run-1_fieldmap.json"
		log_print("editing " + json_file)
		input_json = open(json_file)
		json_file_temp = json_file + ".tmp"
		json_dict = json.load(input_json)
		input_json.close()
		#update the json dict according to nii header?
		json_dict["Units"] = 'rad/s'
		out_file = open(json_file_temp, "w")
		json.dump(json_dict, out_file, indent=2)
		out_file.close()
		os.rename(json_file_temp, json_file)
	
	def add_missing_se_data(s):
		"""
		add the missing json config for the SE fieldmap. This includes
		IntendedFor. Since we now do TotalReadoutTime and PhaseEncodingDirection
		in bids_util.update_epi_json_files
		"""
		
		target_files = []
		#The target fMRI files the SE fieldmap will be used for. 
		#TODO: Cannot have sessions hardcoded here
		for i in (1, 2, 3 ,4):
			target_files.append(s.part_bold_name + "_task-8bars_dir-AP_run-{}_bold.nii.gz".format(i))
		for dr in ['AP', 'PA']:
			json_file = s.part_filename + "_acq-se_dir-" + dr + "_run-1_epi.json"
			log_print("editing " + json_file)
			try: 
				input_json = open(json_file)
				json_file_temp = json_file + ".tmp"
				json_dict = json.load(input_json)
				input_json.close()
				json_dict["IntendedFor"] = target_files	
				out_file = open(json_file_temp, "w")
				json.dump(json_dict, out_file, indent=2)
				out_file.close()
				os.rename(json_file_temp, json_file)
			except Exception as e:
				log_print(str(e), force=True)
				
	def rename_gre_fmap(s):
		"""
		function to make sure the GRE fieldmap files are named
		_fieldmap and _magnitude respectively. 
		"""
		base_gre_filename = s.part_filename + "_acq-gre_dir-AP_run-1_"
		out_fmap_filename = s.part_filename + "_acq-gre_run-1_" 
		
		for idx in [1, 2]:
			if(idx == 1):
				input_file = base_gre_filename + "epi1";
				output_file = out_fmap_filename + "fieldmap";
			elif(idx == 2): 
				input_file = base_gre_filename + "epi2";
				output_file = out_fmap_filename + "magnitude";
			else:
				print("wrong index")
				sys.quit();
			for ending in [".json", ".nii.gz"]:
				os.rename(input_file + ending, output_file + ending)
				log_print("renamed " + output_file + ending)
			
	def execute(s):
		"""
			executed by fix_bids_tree.py
			performs fixes for BIDS tree and updates scans.tsv
		"""
		bids_util.update_epi_json_files(s.root_folder, s.dicom_dir, s.epi_ap_ph_enc_dir)
		s.rename_gre_fmap()
		func_path = "{}/{}/{}/".format(s.bids_out, s.long_subj, "func")
		if(os.path.exists(func_path)):
			s.add_missing_se_data()
		else:
			log_print("not adding IntendedFor due to missing fMRI data")
			
		s.add_missing_gre_data()
		bids_util.rename_scan_file(s.sc_pre_str + "_acq-gre_dir-AP_run-1_epi1.nii.gz",
				[s.sc_pre_str + "_acq-gre_run-1_fieldmap.nii.gz"])
		bids_util.rename_scan_file(s.sc_pre_str + "_acq-gre_dir-AP_run-1_epi2.nii.gz",
				[s.sc_pre_str + "_acq-gre_run-1_magnitude.nii.gz"])
