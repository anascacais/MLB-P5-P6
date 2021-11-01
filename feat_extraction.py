# built-in
import os
import datetime 
import pickle

# third-party
import numpy as np
import pandas as pd

# local
from features.get_feat_segments import get_feat, get_feat_names

# --------- CHANGE BEFORE RUNNING --------- #

db_dir = 'MLB-Seer'
src_dir = 'C:\\Users\\Mariana\\PycharmProjects\\MLB\\Project_2021'
window = 5 # in seconds
# ----------------------------------------- #

patients_info_dir = os.path.join(src_dir, db_dir, 'Patients-info')
filt_data_dir = os.path.join(src_dir, 'Df_filt_data')
saving_dir = os.path.join(src_dir, 'Df_raw_data')

def feat_extraction(preseizure = 0, postseizure = 0, feat_types = [''], modalities = ['']):

    list_patients = [patient_id for patient_id in os.listdir(filt_data_dir) if os.path.isdir(os.path.join(filt_data_dir, patient_id))] 

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if modalities == ['']:
            modalities = pat.modalities

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        all_pat_files = [f for f in os.listdir(os.path.join(filt_data_dir, pat.id))]
        select_files = [file for file in all_pat_files if file.split('_')[-1] in modalities]

        for filename in select_files:
            fs = 128

            df = pd.read_pickle(os.path.join(filt_data_dir, pat.id, filename))
            modality = filename.split('_')[-1]
            preseizure = int(preseizure * fs)
            postseizure = int(postseizure * fs)
            if '_b' in filename:
                file_type = 'baseline'
            else:
                file_type = 'seizure'
            
            segments = segment_df(df, modality, file_type, preseizure, postseizure, fs, feat_types)
            print(segments)


# ---------- AUXILIARY FUNCTIONS ---------- #

def segment_df(df, modality, file_type, preseizure, postseizure, fs, feat_types, resolution='ms'):

    # find where the diff between timestamps is different than what expected, to the millisecond ((1/fs)*1000)
    diff_time = np.diff(df.index).astype(f'timedelta64[{resolution}]')
    diff_time = np.argwhere(diff_time != datetime.timedelta(milliseconds=np.floor((1/fs)*1000))) 

    feature_names = get_feat_names(sig_lab=modality, feat_type=feat_types)

    feat_df = pd.DataFrame(columns=feature_names)

    start, end = 0, -1

    if len(diff_time) != 0:

        for diff in diff_time:
            
            end = diff[0]+1
            crop_df = df.iloc[start:end]
            aux_feat_df = pd.DataFrame()

            print(np.unique(np.diff(crop_df.index).astype(f'timedelta64[{resolution}]')))

            for m in df.columns:
                aux_df = crop_df[m]
                aux_feat_df = pd.concat([aux_feat_df, extract_feat_seg(aux_df, modality, fs, window, feat_types)], axis=1)
            
            start = diff[0]+1
            feat_df = pd.concat([feat_df, aux_feat_df], axis=0)
            
    else:
        for m in df.columns:
            feat_df = pd.concat([feat_df, extract_feat_seg(df, modality, fs, window, feat_types)], axis=1)

    print(feat_df)


def extract_feat_seg(df, modality, fs, window, feat_types):

    print(f'     extracting features for {modality}')

    feat_type = ['geo', 'stat', 'spec', 'reg']

    # get segments
    
    aux_df = get_feat(df.values, sig_lab=modality, sampling_rate=fs, feat_type=feat_types, windows_len=window)
    #verify number of samples and compare to expected
    # concatenate initial timestamp to each feature vector
    return aux_df



feat_extraction(preseizure=30, postseizure=30, feat_types = ['temp', 'stat', 'spec', 'signal'], modalities = ['EDA'])