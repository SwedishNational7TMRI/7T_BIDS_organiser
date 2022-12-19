
from .lib.pymp2rage import pymp2rage
import nibabel as nib
from . import bids_util
from .bids_util import log_print
import os

class pymp2rage_module():
	"""
	mini class encapsulating stuff for pymp2rage things
	provided context by a runner
	"""
	
	def __init__(s, runner, run_num=1):
		"""
		not much to setup here
		arguments:
		- runner: task_runner parent 
		"""
		s.runner = runner
		s.subj = runner.subj
		s.long_subj = "sub-" + s.subj
		s.run_num = run_num
		
	def get_filename(s, inv, part):
		"""
		helper function to create filenames
		
		arguments:
			- inv: 1 or 2
			- part: name string
		returns: the desired filename
		"""
		
		pymp2rage_pre = s.runner.get_deriv_folder("pymp2rage", "anat")
		if(part == "UNIT1") or (part == "T1map"):
			return pymp2rage_pre + "/{}_run-{}_desc-pymp2rage_{}.nii.gz".format(s.long_subj, s.run_num, part) 
		if(part == "complex"):
			return pymp2rage_pre + "/{}_run-{}_inv-{}_MP2RAGE.nii.gz".format(s.long_subj, s.run_num, str(inv)) 
		return pymp2rage_pre + "/{}_run-{}_inv-{}_part-{}_MP2RAGE.nii.gz".format(s.long_subj, s.run_num, str(inv), str(part)) 

	def create_pymp2rage_input_files(s):
		"""
		create derivatives/pymp2rage directory, and put input files with 
		each inversion times magnitude and phase here. 
		
		input arguments:
			subj: subject label
		"""
		rawdata = s.runner.app_sd_on_task_conf("bids_input")
		raw_anat_path_pre = f"{rawdata}/{s.long_subj}/anat/{s.long_subj}"

		# Need to do the processing of both inversion times
		for inv in (1, 2):
			cplx = s.get_filename(inv, "complex")
			# if file cplx does not exist
			if not os.path.isfile(cplx):
				real = raw_anat_path_pre + f"_run-{s.run_num}_inv-{inv}_part-real_MP2RAGE.nii.gz"
				imag = raw_anat_path_pre + f"_run-{s.run_num}_inv-{inv}_part-imag_MP2RAGE.nii.gz"
				s.runner.sh_run(f"fslcomplex -complex {real} {imag} {cplx} {inv-1} {inv-1}", no_log=True)

			mag = s.get_filename(inv, "mag")
			phase = s.get_filename(inv, "phase")
			if not os.path.isfile(mag) or os.path.isfile(phase):
				s.runner.sh_run(f"fslcomplex -realpolar {cplx} {mag} {phase}", no_log=True)

			log_print("copying geometry to output files")
			for f in (mag, phase):
				s.runner.sh_run("fslcpgeom", cplx, f, no_log=True)
			

	def make_pymp2rage(s):
		"""
		Create a MP2RAGE object by passing the input files previously created. 
		TODO: use B1 map 
		
		See documentation at  
		https://github.com/Gilles86/pymp2rage/blob/master/pymp2rage/mp2rage.py
		"""
		log_print("calculating pyMP2RAGE..")
		inv1_mag = s.get_filename(1, "mag")
		inv1_phase = s.get_filename(1, "phase")
		inv2_mag = s.get_filename(2, "mag")
		inv2_phase = s.get_filename(2, "phase")
	#TODO:   B1_fieldmap=<insert fieldmap file here>
		
		mp2_obj = pymp2rage.MP2RAGE(
			**s.runner.config['mp2rage']['params'],
			inv1=inv1_mag,
			inv1ph=inv1_phase,
			inv2=inv2_mag,
			inv2ph=inv2_phase)
		

		#The object has these Attributes:
		#    t1map (Nifti1Image): Quantitative T1 map
		#    t1w_uni (Nifti1Image): Bias-field corrected T1-weighted image
		#    t1map_masked (Nifti1Image): Quantitative T1 map, masked
		#    t1w_uni_masked (Nifti1Image): Bias-field corrected T1-weighted map, masked
		
		nib.save(mp2_obj.t1w_uni, s.get_filename(1, "UNIT1"))
		log_print("saved " + s.get_filename(1, "UNIT1"))
		nib.save(mp2_obj.t1map, s.get_filename(1, "T1map"))
		log_print("saved " + s.get_filename(1, "T1map"))
