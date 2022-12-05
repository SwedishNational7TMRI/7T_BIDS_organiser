
from .lib.pymp2rage import pymp2rage
import nibabel as nib
from . import bids_util
from .bids_util import log_print

class pymp2rage_module():
	"""
	mini class encapsulating stuff for pymp2rage things
	provided context by a runner
	"""
	
	def __init__(s, runner):
		"""
		not much to setup here
		arguments:
		- runner: task_runner parent 
		"""
		s.runner = runner
		s.subj = runner.subj
		
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
			return pymp2rage_pre + "/{}_run-1_desc-pymp2rage_{}.nii.gz".format(s.subj, part) 
		if(part == "complex"):
			return pymp2rage_pre + "/{}_run-1_inv-{}_MP2RAGE.nii.gz".format(s.subj, str(inv)) 
		return pymp2rage_pre + "/{}_run-1_inv-{}_part-{}_MP2RAGE.nii.gz".format(s.subj, str(inv), str(part)) 

	def create_pymp2rage_input_files(s):
		"""
		create derivatives/pymp2rage directory, and put input files with 
		each inversion times magnitude and phase here. 
		
		input arguments:
			subj: subject label
		"""
		rawdata = s.runner.get_global("orig_bids_root")
		raw_anat_path_pre = "{}/{}/anat/{}".format(rawdata, s.subj, s.subj)
		real_1and2 = raw_anat_path_pre +  "_run-1_inv-1and2_part-real_MP2RAGE.nii.gz"
		imag_1and2 = raw_anat_path_pre +  "_run-1_inv-1and2_part-imag_MP2RAGE.nii.gz"
		cplx_1 = s.get_filename(1, "complex")
		cplx_2 = s.get_filename(2, "complex")

		log_print("making split complex niftis")	
		s.runner.sh_run("fslcomplex -complex",  real_1and2 + " " + imag_1and2, cplx_1, " 0 0", no_log=True)
		s.runner.sh_run("fslcomplex -complex",  real_1and2 + " " + imag_1and2, cplx_2, " 1 1", no_log=True)

		inv2_mag = s.get_filename(2, "mag")
		inv2_phase = s.get_filename(2, "phase")

		log_print("getting magnitude and phase for inv 1")
		inv1_mag = s.get_filename(1, "mag")
		inv1_phase = s.get_filename(1, "phase")
		s.runner.sh_run("fslcomplex -realpolar ", cplx_1, inv1_mag + " " + inv1_phase, no_log=True)
		
		log_print("getting magnitude and phase for inv 2")
		inv2_mag = s.get_filename(2, "mag")
		inv2_phase = s.get_filename(2, "phase")
		s.runner.sh_run("fslcomplex -realpolar ", cplx_2, inv2_mag + " " + inv2_phase, no_log=True)

		log_print("copying geometry to output files")
		for f in (inv1_mag, inv1_phase):
			s.runner.sh_run("fslcpgeom", cplx_1, f, no_log=True)
		for f in (inv2_mag, inv2_phase):
			s.runner.sh_run("fslcpgeom", cplx_2, f, no_log=True)

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

	#use default settings now to prevent crashing
		mp2_obj = pymp2rage.MP2RAGE(
			MPRAGE_tr=5.0,
			invtimesAB=[0.921, 2.771],
			flipangleABdegree=[8, 6],
			nZslices=257,
			FLASH_tr=[0.0068, 0.0068], B0=7.0, 
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

if __name__ == "__main__":
	print("This file is no longer executable")
	print("run with pipeline.py -t mp2rage <subj> -c <conf.json>")
