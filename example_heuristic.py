import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    allowed template fields - follow python string module:
    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    # ANATOMY
    # 7T anatomy is run with the MP2RAGE sequence
    # See https://portal.research.lu.se/portal/files/79469556/ASL_2020_1_Helms_version3.pdf
    # Raw data output are 3 images
    # 1) 4D image: real images with phase 1 and phase 2
    # 2) 4D image: imag images with phase 1 and phase 2
    # 3) 4D image: mag inv 1 and inv2
    # Optional output is reconstructed MP2RAGE T1w image
    # 4) 3D image: mag MP2RAGE T1w image (not salt-n-peppar noise in non-brain => hard for skull-stripping!)
    # The BIDS convention includes, which is "Siemens-based" with _inv-
    #sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<label>]_MP2RAGE.json
    #sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<label>]_MP2RAGE.nii[.gz]


    ## MP2RAGE
    # from Finn: image is reconstructed on the scanner and exported as seperat DICOM-image
    t1wmp2rage_real = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_inv-1and2_part-real_MP2RAGE')
    t1wmp2rage_imag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_inv-1and2_part-imag_MP2RAGE')
    # ... and toghether we can get 4D image which has a T1w (PD-like contrast)
    t1wmp2rage_mag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_inv-1and2_MP2RAGE')
    # ...the reconstructed MP2RAGE will get UNIT1 suffix, as in the BIDS convention
    t1wmp2rage_unit = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_acq-mp2rage_UNIT1')

    ## ANAT
    t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_T1w')
    t2w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_T2w')
    flair = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:01d}_FLAIR')

    # FUNC
    resting = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_run-{item:01d}_bold')

    # DWI
    dwi_ap = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dir-AP_run-{item:01d}_dwi')
    dwi_pa = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dir-PA_run-{item:01d}_dwi')

    # FMAP
    # B0 map for resting state fMRI
    fmap = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_run-{item:01d}_epi')
    # B1+ fieldmaps for MP2rage
    #b1plusfmap25 = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-dream25_run-{item:01d}_flip-25_MP2RAGE')
    #b1plusfmap40 = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-dream40_run-{item:01d}_flip-40_MP2RAGE')
    #b1plusfmap60 = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_acq-dream60_run-{item:01d}_flip-60_MP2RAGE')

    info = {
	        t1wmp2rage_real: [],t1wmp2rage_imag: [],t1wmp2rage_mag: [], t1wmp2rage_unit: [],
	        t1w: [],t2w: [],flair: [],
	        resting: [],
	        dwi_ap: [], dwi_pa: [],
	        fmap: []
            #b1plusfmap25: [], b1plusfmap40: [], b1plusfmap60: []
	       }

    for idx, s in enumerate(seqinfo):

	    # MP2RAGE (T1w)
        if ('real' in s.series_description) and not (s.is_derived):
            info[t1wmp2rage_real].append(s.series_id)
        if ('imag' in s.series_description) and not (s.is_derived):
            info[t1wmp2rage_imag].append(s.series_id)
        if ('MP2rage_' in s.series_description) and not (s.is_derived):
            info[t1wmp2rage_mag].append(s.series_id)
        if (('WIP-imag' in s.series_description) or ('WIP - imag' in s.series_description) or ('WIP - real' in s.series_description)) and (s.is_derived):
            info[t1wmp2rage_unit].append(s.series_id)

	    # ANAT
        if ('T1 3D TFE' in s.series_description) and not (s.is_derived):
            info[t1w].append(s.series_id)
        if ('3D T2 TSE' in s.series_description) and not (s.is_derived):
            info[t2w].append(s.series_id)
        if ('FLAIR' in s.series_description) and not (s.is_derived):
            info[flair].append(s.series_id)

	    # FUNC
        if ('Resting' in s.series_description) and not (s.is_derived) and (s.series_files >= 23800):
            info[resting].append(s.series_id)

	    # DIFF
        if ('DTI_FSz_S3_B1_10_2x2x2_AP' in s.series_description) and not (s.is_derived) and (s.series_files >= 3120):
            info[dwi_ap].append(s.series_id)
        if ('DTI_FSz_S3_B1_10_2x2x2_PA_short' in s.series_description) and not (s.is_derived) and (s.series_files >= 400):
            info[dwi_pa].append(s.series_id)

	    # FIELDMAP
        if ('B0MAP RS' in s.series_description) and not (s.is_derived):
            info[fmap].append(s.series_id)
        # if ('DREAM_25' in s.series_description) and not (s.is_derived):
        #     info[b1plusfmap25].append(s.series_id)
        # if ('DREAM_40' in s.series_description) and not (s.is_derived):
        #     info[b1plusfmap40].append(s.series_id)
        # if ('DREAM_60' in s.series_description) and not (s.is_derived):
        #     info[b1plusfmap60].append(s.series_id)

    return info
