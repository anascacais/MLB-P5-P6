# built-in
import os
import datetime 
import pickle

# third-party
import numpy as np
import pandas as pd

# local
from features.get_feat_segments import get_feat, get_feat_names

# # --------- CHANGE BEFORE RUNNING --------- #

# src_dir = '/Users/anascacais/Documents'
# window = 5 # in seconds
# preseizure = 30 # in seconds
# postseizure = 10 # in seconds
# # ----------------------------------------- #

# patients_info_dir = os.path.join(src_dir, 'patients-info')
# filt_data_dir = os.path.join(src_dir, 'filtered-data-df')
# saving_dir = os.path.join(src_dir, 'features')

def feat_extraction(patients_info_dir, filt_data_dir, saving_dir, feat_types, modalities=None, preseizure=0, postseizure=0, window=30):

    list_patients = [patient_id for patient_id in os.listdir(filt_data_dir) if os.path.isdir(os.path.join(filt_data_dir, patient_id))] 

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if modalities is None:
            modalities = list(pat.modalities.keys())

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        all_pat_files = [f for f in os.listdir(os.path.join(filt_data_dir, pat.id))]
        select_files = [file for file in all_pat_files if file.split('_')[-1] in modalities]

        for filename in select_files:

            df = pd.read_pickle(os.path.join(filt_data_dir, pat.id, filename))

            modality = filename.split('_')[-1]
            fs = pat.modalities[modality]

            preseizure = int(preseizure * fs)
            postseizure = int(postseizure * fs)
            
            segments = segment_df(df, preseizure, postseizure, window, fs, feat_types)


# ---------- AUXILIARY FUNCTIONS ---------- #

def segment_df(df, preseizure, postseizure, window, fs, feat_types, resolution='ms'):

    # find where the diff between timestamps is different than what expected, to the millisecond ((1/fs)*1000)
    diff_time = np.diff(df.index).astype(f'timedelta64[{resolution}]')
    diff_time = np.argwhere(diff_time != datetime.timedelta(milliseconds=np.floor((1/fs)*1000))) 

    overlap = 0.5

    feat_df = pd.DataFrame()
    window = int(window * fs)
    overlap_window = int(window * (1 - overlap))
    start, end = 0, -1

    if len(diff_time) != 0:

        diff_time = np.append(diff_time, [len(df)-1])

        for diff in diff_time:
            
            end = diff+1
            crop_df = df.iloc[start:end]
            aux_feat_df = pd.DataFrame()

            for seg in range(0, len(crop_df) - window):
                aux_df = crop_df[seg:seg + window]

            #print(np.unique(np.diff(crop_df.index).astype(f'timedelta64[{resolution}]')))
            
            if 'sz' in df.columns:
                sz_ = expand_pre_post_sz(df['sz'].values, preseizure, postseizure)
                sz_ = [sz_[i] for i in range(0, len(crop_df)-window, overlap_window)]


            time_ = [df.index[i] for i in range(0, len(crop_df)-window, overlap_window)]

            for m in [df.columns[0]]:
                
                aux_df = crop_df[m]
                aux_feat_df = pd.concat((aux_feat_df, extract_feat_seg(aux_df, m, fs, feat_types, window, overlap_window)), axis=1)
            
            aux_feat_df.index = time_
            feat_df = pd.concat([feat_df, aux_feat_df], axis=0)

            start = diff+1
            
    else:
        for m in [df.columns[0]]:
            feat_df = pd.concat((feat_df, extract_feat_seg(df, m, fs, feat_types, window, overlap_window)), axis=1)

    return feat_df


def extract_feat_seg(df, modality, fs, feat_types, window, overlap_window):

    print(f'     extracting features for {modality}')
    
    feature_names = get_feat_names(sig_lab=modality, feat_type=feat_types)
    aux = np.vstack([get_feat(df.values[i: i+ window].reshape(-1,), sig_lab=modality, sampling_rate=fs, feat_type=feat_types) for i in range(0, len(df)-window, overlap_window)])
    
    return pd.DataFrame(aux, columns=feature_names)


def expand_pre_post_sz(seizures, preseizure, postseizure):
    import matplotlib.pyplot as plt
    expanded_seizures = np.copy(seizures)
    plt.figure()

    uni = np.unique(seizures)
    for sz in uni:
        if sz == 0: 
            continue
        indx = np.argwhere(seizures == sz)
        aux_ind = np.arange(int(indx[0])-preseizure, int(indx[-1])+postseizure)
        np.put(expanded_seizures, aux_ind, sz*np.ones((len(aux_ind),)))
        plt.plot(aux_ind, sz*np.ones((len(aux_ind),)))

    uni = np.unique(expanded_seizures)
    for sz in uni:
        if sz == 0: 
            continue
        indx = np.argwhere(expanded_seizures == sz)
        aux_ind = np.arange(int(indx[0])-preseizure, int(indx[-1])+postseizure)
        print(f'{len(np.argwhere(seizures == sz))} vs {len(np.argwhere(expanded_seizures == sz))}')
        plt.plot(aux_ind, sz*np.ones((len(aux_ind),)))
    
    plt.show()

    return expanded_seizures


