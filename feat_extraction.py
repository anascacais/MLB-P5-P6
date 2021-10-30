# built-in
import os
import datetime 
import pickle

# third-party
import numpy as np
import pandas as pd

# local
from get_feat_segments import get_feat

# --------- CHANGE BEFORE RUNNING --------- #

db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
src_dir = '/Users/anascacais/Documents/'
window = 5 # in seconds
# ----------------------------------------- #

patients_info_dir = os.path.join(src_dir, 'patients-info')
filt_data_dir = os.path.join(src_dir, 'filtered-data-df')
saving_dir = os.path.join(src_dir, 'features')

def feat_extraction():

    list_patients = [patient_id for patient_id in os.listdir(filt_data_dir) if os.path.isdir(os.path.join(filt_data_dir, patient_id))]

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        for filename in [f for f in os.listdir(os.path.join(filt_data_dir, pat.id))]:

            df = pd.read_pickle(os.path.join(filt_data_dir, pat.id, filename))
            modality = filename.split('-')[-1]
            
            segments = segment_df(df, modality, fs=pat.modalities[modality])
            print(segments)


# ---------- AUXILIARY FUNCTIONS ---------- #

def segment_df(df, modality, fs, resolution='ms'):

    # find where the diff between timestamps is different than what expected, to the millisecond ((1/fs)*1000)
    diff_time = np.diff(df.index).astype(f'timedelta64[{resolution}]')
    diff_time = np.argwhere(diff_time != datetime.timedelta(milliseconds=np.floor((1/fs)*1000))) 

    feat_df = pd.DataFrame()

    start = 0
    end = -1

    if len(diff_time) != 0:

        for diff in diff_time:
            
            end = diff[0]+1
            crop_df = df.iloc[start:end]
            aux_feat_df = pd.DataFrame()

            print(np.unique(np.diff(crop_df.index).astype(f'timedelta64[{resolution}]')))

            for m in df.columns:
                aux_df = crop_df[m]
                aux_feat_df = pd.concat([aux_feat_df, extract_feat_seg(aux_df, modality, fs, window)], axis=1)
            
            start = diff[0]+1
            feat_df = pd.concat([feat_df, aux_feat_df], axis=0)
            
    else:
        for m in df.columns:
            feat_df = pd.concat([feat_df, extract_feat_seg(df, modality, fs, window)], axis=1)

    print(feat_df)


def extract_feat_seg(df, modality, fs, window):

    print(f'     extracting features for {modality}')
    
    aux_df = get_feat(df.values, sig_lab=modality, sampling_rate=fs, windows_len=window)
    #verify number of samples and compare to expected
    # concatenate initial timestamp to each feature vector
    return aux_df



feat_extraction()