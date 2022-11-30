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
    # 1) 4D image: mag inv 1 and inv2
    # 2) 4D image: real images with phase 1 and phase 2
    # 3) 4D image: imag images with phase 1 and phase 2
    # Optional output is reconstructed MP2RAGE T1w image
    # 4) 3D image: mag MP2RAGE T1w image (not salt-n-peppar noise in non-brain => hard for skull-stripping!)
    # The BIDS convention includes, which is "Siemens-based" with _inv-
    #sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<label>]_MP2RAGE.json
    #sub-<label>[_ses-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_echo-<index>][_flip-<index>]_inv-<index>[_part-<label>]_MP2RAGE.nii[.gz]

    # The MP2RAGE image is reconstructed on the scanner and exported as seperat DICOM-image (see below for identifiers)
    t1wmp2rage_real = create_key('sub-{subject}/anat/sub-{subject}_run-{item:01d}_inv-1and2_part-real_MP2RAGE')
    t1wmp2rage_imag = create_key('sub-{subject}/anat/sub-{subject}_run-{item:01d}_inv-1and2_part-imag_MP2RAGE')
    # and toghether we can get 4D image which has a T1w (PD-like contrast)
    t1wmp2rage_inv = create_key('sub-{subject}/anat/sub-{subject}_run-{item:01d}_inv-1and2_MP2RAGE')
    # The reconstructed MP2RAGE will get UNIT1 suffix, as in the BIDS convention
    t1wmp2rage_mp2rage = create_key('sub-{subject}/anat/sub-{subject}_acq-mp2rage_run-{item:01d}_UNIT1')
    
    # FLAIR
    # Some subjects will have a FLAIR included, but this is not necessarily run with the same sequence
    # Therefor it is converted into a BIDS FLAIR sequence with running number
    flair = create_key('sub-{subject}/anat/sub-{subject}_run-{item:01d}_FLAIR')

    # DWI
    dwi_ap = create_key('sub-{subject}/dwi/sub-{subject}_dir-AP_run-{item:01d}_dwi')
    dwi_pa = create_key('sub-{subject}/dwi/sub-{subject}_dir-PA_run-{item:01d}_dwi')
    
    # fMRI
    fmri_8bars = create_key('sub-{subject}/func/sub-{subject}_task-8bars_dir-AP_run-{item:01d}_bold')
    
    # FIELDMAP/s
    fmap_se_ap = create_key('sub-{subject}/fmap/sub-{subject}_acq-se_dir-AP_run-{item:01d}_epi')
    fmap_se_pa = create_key('sub-{subject}/fmap/sub-{subject}_acq-se_dir-PA_run-{item:01d}_epi')
    fmap_gre_ap = create_key('sub-{subject}/fmap/sub-{subject}_acq-gre_dir-AP_run-{item:01d}_epi')
    #fmap_gre_ap_mag = create_key('sub-{subject}/fmap/sub-{subject}_acq-gre_dir-AP_run-{item:01d}_magnitude')
    #fmap_gre_ap_phase = create_key('sub-{subject}/fmap/sub-{subject}_acq-gre_dir-AP_run-{item:01d}_phasediff')
    fmap_b1 = create_key('sub-{subject}/fmap/sub-{subject}_acq-b1_run-{item:01d}_epi')
    
    #info = {t1wmp2rage_real: [],t1wmp2rage_imag: [],t1wmp2rage_inv: [],t1wmp2rage_mp2rage: [], flair: [], dwi_ap: [], dwi_pa: [], fmri_8bars: [], fmap_se_ap: [], fmap_se_pa: [], fmap_gre_ap: [], fmap_b1: []}
    info = {t1wmp2rage_real: [],t1wmp2rage_imag: [],t1wmp2rage_inv: [],t1wmp2rage_mp2rage: [],
        flair: [], dwi_ap: [], dwi_pa: [], fmri_8bars: [], fmap_se_ap: [], 
        fmap_se_pa: [], fmap_gre_ap: [], fmap_b1: []}
    
    for idx, s in enumerate(seqinfo):
        # ANATOMY
        # T1w - MP2RAGE
        if ('real' in s.series_description) and not (s.is_derived):
            info[t1wmp2rage_real].append(s.series_id) # assign if a single series meets criteria
        if ('imag' in s.series_description) and not (s.is_derived):
            info[t1wmp2rage_imag].append(s.series_id) # assign if a single series meets criteria
        if ('WIP-imag' in s.series_description) or ('WIP - imag' in s.series_description) and (s.is_derived):
            info[t1wmp2rage_mp2rage].append(s.series_id) # assign if a single series meets criteria
        if ('T1w_acq-mp2rage' in s.series_description):
            info[t1wmp2rage_inv].append(s.series_id) # assign if a single series meets criteria            
            
        # FLAIR
        if ('FLAIR' in s.series_description):
            info[flair].append(s.series_id) # assign if a single series meets criteria            
        
            
        # FIELDMAP/s
        # gre-fieldmap
        if ('fmap_acq-B0mapShimmed' in s.series_description):
            # magnitude image
            info[fmap_gre_ap].append(s.series_id)
        if ('NOT YET SORTED' in s.series_description) and (s.image_type[2] == 'M') and ('NORM' in s.image_type):
            # magnitude image
            info[fmap_gre_ap_mag].append(s.series_id) #     
        if ('NOT YET SORTED' in s.series_description) and (s.image_type[2] == 'P'):
            # phase image
            info[fmap_gre_ap_phase].append(s.series_id) #
        #Get B1 fieldmap
        #TODO: this tends to overwrite the other fmap files, dont know why. 
        #if ('B1map_dual_TR' in s.series_description):
        #    info[fmap_b1].append(s.series_id)
        
        # se-fieldmap
        if ('fmap_acq-se_dir-AP' in s.series_description):
            info[fmap_se_ap].append(s.series_id) # assign if a single series meets criteria
        if ('fmap_acq-se_dir-PA' in s.series_description):
            info[fmap_se_pa].append(s.series_id) # assign if a single series meets criteria
        
        # FMRI 
        # pRF fMRI - run with 8bars stimulus
        if ('fmri_8bars_dir-AP' in s.series_description):
            info[fmri_8bars].append(s.series_id) # assign if a single series meets criteria
        
        
        # DIFFUSION
        # dir AP
        # include is_derived = FALSE as additional criteria
        if ('dmri_acq-60deg_dir-AP' in s.series_description) and not (s.is_derived):
            info[dwi_ap].append(s.series_id) # append if multiple series meet criteria
        # dir PA
        # include is_derived = FALSE as additional criteria
        if ('dmri_acq-60deg_dir-PA' in s.series_description) and not (s.is_derived):
            info[dwi_pa].append(s.series_id) # append if multiple series meet criteria 
            
            
    return info
