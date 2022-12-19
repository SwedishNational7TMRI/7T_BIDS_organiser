from . import LUND7T_MODULEPATH
import shutil
from .lib.pymp2rage import pymp2rage
import os
import nibabel as nib
import numpy as np
from . import bids_util
from .bids_util import log_print
from nilearn import image

def resample_affine(affine_source, target):
	"""
	there are rounding error differences in the affine transformation matrix 
	when using QUIT t1w images, here the correctly rounded matrix is 
	copied to the other nifti image. the difference should be negligible. 
	This should only be needed when source is QUIT. 
	arguments:
		affine_source: nifti file name to copy affine from 
		target: nifti file name to open and return with the new affine
	"""
	nii_affine = nib.load(affine_source)
	nii_source = nib.load(target)
	new_nii = nib.Nifti1Image(nii_source.get_fdata(), nii_affine.affine)
	u_xyz, u_t = nii_source.header.get_xyzt_units()
	new_nii.header.set_xyzt_units(u_xyz, u_t)
	return new_nii

class spm12_module:
	"""
	Handles mask creatig, background removal and cat12 execution, using
	various options, (bet or spm12, pymp2rage or quit)
	"""
	def __init__(s, runner):
		"""
		setup file names needed for later
		arguments:
			- runner: task_runner parent 
		"""
		s.runner = runner
		s.subj = runner.subj
		s.long_subj = "sub-" + s.subj
		s.use_quit = runner.config["mask_remove_bg"]["use_quit"]
		if (not s.use_quit):
			s.src_dir = "pymp2rage"
		else:
			s.src_dir = "quit"
		
		s.spm12_path = runner.get_global("spm12_path")
		s.output_pre = s.runner.get_deriv_folder("spm12", "anat")
		
		s.input_inv2_pre =  s.runner.get_deriv_folder("pymp2rage", "anat")
		s.input_inv2 = s.input_inv2_pre +  "/{}_run-1_inv-2_part-mag_MP2RAGE.nii.gz".format(s.long_subj)
		s.input_pre = s.runner.get_deriv_folder(s.src_dir, "anat")
		s.input_t1w = s.input_pre + "/{}_run-1_desc-{}_UNIT1.nii.gz".format(s.long_subj, s.src_dir)	
		
		#TODO: UNIT1 or T1w?
		s.unit1_no_bg = s.input_pre + "/{}_run-1_desc-{}noBackground_UNIT1.nii.gz".format(s.long_subj, s.src_dir)
		
	def make_bet_mask(s):
		"""
		execute bet in shell with a given intensity configuration and saves
		the mask nifti. 
		"""
		bet_intensity = s.runner.get_task_conf("bet_intensity")
		log_print ("using BET for masking on " + s.src_dir + " intensity " + str(bet_intensity)) 
		s.runner.create_derivatives_destination("bet", "anat")
		bet_out_path = s.runner.get_deriv_folder("bet", "anat")
		bet_output_file = bet_out_path + "/{}_run-1_desc-bet.nii.gz".format(s.long_subj)
		s.mask_output_file = bet_out_path + "/{}_run-1_desc-bet_mask.nii.gz".format(s.long_subj)
		s.runner.sh_run("bet", s.input_inv2, bet_output_file, "-m -f {}".format(bet_intensity))

	def make_spm12_mask(s):
		"""
		execute spmmask create a brain mask. slower and less flexible than bet.  
		"""
		log_print("call_spmmask using " + s.src_dir)
		s. mask_output_file = s.output_pre + "/{}_run-1_desc-{}_mask.nii.gz".format(s.long_subj, s.src_dir)
		s.runner.sh_run("call_spmmask -s {} ".format(s.spm12_path), s.input_t1w, s.mask_output_file, " y")
		
	def remove_background(s):
		"""
		use a precomputed mask to remove the background of the t1w image. 
		"""
		log_print("applying mask and removing bg on " + s.input_t1w)
		t1w_output_file = s.unit1_no_bg
		
		t1w = image.load_img(s.input_t1w)
		t1w_mask = resample_affine(s.input_t1w, s.mask_output_file)
		inv2 = resample_affine(s.input_t1w, s.input_inv2)
		
		mask = image.math_img('(t1w_mask > 0)', t1w_mask=t1w_mask)
		#old tomas knapen/jurjen masking method
		new_t1w = image.math_img('t1w * t1w_mask * np.mean(inv2[t1w_mask == 1]/np.max(inv2))'
									'+ t1w * inv2/np.max(inv2) * (1-t1w_mask)',
								t1w=t1w,
								t1w_mask=mask,
								inv2=inv2)
		
		#using simple binary masking instead
		#new_t1w = image.math_img('t1w * t1w_mask',
		
		new_t1w.to_filename(t1w_output_file)
		log_print("saved " + t1w_output_file)

		
	def call_cat12(s):
		"""
		call cat12 to generate segmentation masks and a denoised, filtered 
		version of the image. stores output in /derivatives/cat12-{}/sub-{}/anat. 
		"""
		log_print("running cat12 on " + s.src_dir + " data" )
		input_pre = s.runner.get_deriv_folder("spm12", "anat")
		output_cat_dir = s.runner.get_deriv_folder("cat12", "anat")
		cat12_path = os.path.join(LUND7T_MODULEPATH, 'lib', 'linescanning', 'bin')
		my_env = os.environ.copy()
		my_env["PATH"] = my_env["PATH"] + ":" + cat12_path
		s.runner.sh_run("bash call_cat12 -s {} ".format(s.spm12_path), s.unit1_no_bg, output_cat_dir, env=my_env)
		os.remove(tmp_input)
		
class quit_module():	
	"""
	contains routines for generating a mp2rage T1w image with QUIT.
	"""

	def __init__(s, runner):
		"""
		arguments:
		sets up some file names needed later 
			- runner: task_runner parent 
		"""
		#first half of each bids fileanme
		s.runner = runner
		s.subj = runner.subj
		s.long_subj = "sub-" + s.subj
		rawdata = runner.app_sd_on_task_conf("bids_input")
		s.part_input_filename = "{}/{}/{}/{}".format(rawdata, s.long_subj, "anat", s.long_subj)
		s.deriv_quit_folder = runner.get_deriv_folder("quit", "anat")
		
		s.sc_pre_str = "anat/{}".format(s.subj)
		s.quit_complex_input = s.deriv_quit_folder + "/{}_run-1_desc-inv1and2_MP2RAGE".format(s.long_subj)
	
	def create_QUIT_nifti(s):
		"""
			creates a new file in derivatives that is the input data for QUIT 
			MP2RAGE and T1 calculation.   
		"""
		log_print("creating QUIT input files")
		real_filename = s.part_input_filename + "_run-1_inv-1and2_part-real_MP2RAGE"
		imag_filename = s.part_input_filename + "_run-1_inv-1and2_part-imag_MP2RAGE"
		
		output_file = s.quit_complex_input
		im_nii = nib.load(real_filename + ".nii.gz")
		im_nii_data = im_nii.get_fdata()
		re_nii = nib.load(imag_filename + ".nii.gz")
		re_nii_data = re_nii.get_fdata()
		quit_data = np.zeros(re_nii_data.shape)
		quit_data = re_nii_data + im_nii_data*1j
		
		quit_nii = nib.Nifti1Image(quit_data, re_nii.affine)
		u_xyz, u_t = re_nii.header.get_xyzt_units()
		quit_nii.header.set_xyzt_units(u_xyz, u_t)
		bids_util.update_json_shape(quit_nii, real_filename + ".json", output_file + ".json")
		nib.save(quit_nii, output_file + ".nii.gz")

	def gen_T1_map_mp2rage(s):
		"""
			function to call the QUIT library to generate a better mp2RAGE
			image. 
			https://quit.readthedocs.io/en/latest/Docs/Relaxometry.html#qi-mp2rage
			
		"""
		mp2rage_json_file = s.runner.code_path + "/mp2rage_parameters.json"
		qi_cmd = "qi mp2rage {} < {}".format(s.quit_complex_input, mp2rage_json_file, no_log=True)
		s.runner.sh_run(qi_cmd)
		
		dest = s.deriv_quit_folder + "/{}_run-1_desc-quit_UNIT1.nii.gz".format(s.long_subj)
		os.rename("MP2_UNI.nii.gz", dest)
		dest = s.deriv_quit_folder + "/{}_run-1_desc-quit_T1map.nii.gz".format(s.long_subj)
		os.rename("MP2_T1.nii.gz", dest)

