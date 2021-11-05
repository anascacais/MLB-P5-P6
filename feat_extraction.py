# built-in
import os
import datetime 
import pickle

# third-party
import numpy as np
import pandas as pd

# local
from features.get_feat_segments import get_feat, get_feat_names


def feat_extraction(patients_info_dir, filt_data_dir, saving_dir, feat_types, modalities=None, list_patients=None, preseizure=0, postseizure=0, window=30, overlap=0.5):

    if list_patients is None:
        list_patients = [patient_id for patient_id in os.listdir(filt_data_dir) if os.path.isdir(os.path.join(filt_data_dir, patient_id))] 

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if modalities is None:
            modalities = list(pat.modalities.keys())

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        all_pat_files = [f for f in os.listdir(os.path.join(filt_data_dir, pat.id))]
        select_files = [file for file in all_pat_files if file.split('_')[-1][:-3] in modalities]

        for filename in select_files:
            

            df = pd.read_hdf(os.path.join(filt_data_dir, pat.id, filename))

            modality = filename.split('_')[-1][:-3]
            fs = pat.modalities[modality]

            preseizure_ = int(preseizure * fs)
            postseizure_ = int(postseizure * fs)

            new_file_name = f'features_{filename.split("_")[1]}_{modality}_{window}s_{int(overlap*100)}'

            if new_file_name+'.h5' in os.listdir(os.path.join(saving_dir, patient_id)):
                print('features already extract for patient ', patient_id, ' - ', new_file_name)
                continue
            
            segments = segment_df(df, preseizure_, postseizure_, window, overlap, fs, feat_types[modality])
            
            if len(segments) != 0:
                segments.to_hdf(os.path.join(saving_dir, patient_id, new_file_name+'.h5'), mode='w', key='df')


# ---------- AUXILIARY FUNCTIONS ---------- #

def segment_df(df, preseizure, postseizure, window, overlap, fs, feat_types, resolution='ms'):

    # find where the diff between timestamps is different than what expected, to the millisecond ((1/fs)*1000)
    diff_time = np.diff(df.index).astype(f'timedelta64[{resolution}]')
    diff_time = np.argwhere(diff_time != datetime.timedelta(milliseconds=np.floor((1/fs)*1000))) 

    feat_df = pd.DataFrame()
    window = int(window * fs)
    overlap_window = int(window * (1 - overlap))
    start, end = 0, -1

    if len(diff_time) != 0:

        diff_time = np.append(diff_time, [len(df)-1])

        for d,diff in enumerate(diff_time):

            if (d % 2 == 0 and 'sz' not in df.columns):
                # avoid half of baselines
                continue
            
            print(f'    Extracting features for segment {d+1} of {len(diff_time)}')

            end = diff+1
            crop_df = df.iloc[start:end]

            if len(crop_df) < window: 
                print(f'        segment smaller than window: {len(crop_df)} ')
                continue

            aux_feat_df = pd.DataFrame()
            
            
            if 'sz' in df.columns:
                sz_ = expand_pre_post_sz(crop_df['sz'].values, preseizure, postseizure)
                crop_df = crop_df.assign(sz=sz_)
                crop_df = crop_df[crop_df.sz != 0.]
                sz_ = [crop_df.sz[i] for i in range(0, len(crop_df)-window, overlap_window)]
                
            
            time_ = [crop_df.index[i] for i in range(0, len(crop_df)-window, overlap_window)]


            for m in [df.columns[0]]:
                
                aux_df = crop_df[m]
                aux_feat_df = pd.concat((aux_feat_df, extract_feat_seg(aux_df, m, fs, feat_types, window, overlap_window)), axis=1)
            
            aux_feat_df.index = time_

            if 'sz' in df.columns:
                aux_feat_df['sz'] = sz_
                #aux_feat_df = aux_feat_df.assign(sz=sz_)

            feat_df = pd.concat([feat_df, aux_feat_df], axis=0)

            start = diff+1
            
    else:

        print(f'    Extracting features for the whole segemnt')

        if len(df) >= window: 
        
            if 'sz' in df.columns:
                sz_ = expand_pre_post_sz(df['sz'].values, preseizure, postseizure)
                df['sz'] = sz_
                df = df[df.sz != 0.]
                sz_ = [sz_[i] for i in range(0, len(df)-window, overlap_window)]

            time_ = [df.index[i] for i in range(0, len(df)-window, overlap_window)]

            for m in [df.columns[0]]:
                feat_df = pd.concat((feat_df, extract_feat_seg(df, m, fs, feat_types, window, overlap_window)), axis=1)

            feat_df.index = time_
            #feat_df = feat_df.set_index(time_)

            if 'sz' in df.columns:
                feat_df['sz'] = sz_
        
        else:
            print(f'        segment smaller than window: {len(df)}')

    feat_df = feat_df.dropna()
    return feat_df


def extract_feat_seg(df, modality, fs, feat_types, window, overlap_window):

    #print(f'        extracting features for {modality}')
    
    feature_names = get_feat_names(sig_lab=modality, feat_type=feat_types)
    aux = np.vstack([get_feat(df.values[i: i+ window].reshape(-1,), sig_lab=modality, sampling_rate=fs, feat_type=feat_types, feat_names=feature_names) for i in range(0, len(df)-window, overlap_window)])


    # for i in range(0, len(df)-window, overlap_window):

    #     if len(aux) == 0: 
    #         aux = get_feat(df.values[i: i + window].reshape(-1,), sig_lab=modality, sampling_rate=fs, feat_type=feat_types, feat_names=feature_names)
    #     else: 
    #         f = get_feat(df.values[i: i + window].reshape(-1,), sig_lab=modality, sampling_rate=fs, feat_type=feat_types, feat_names=feature_names)
    #         if len(f) != 0: 
    #             aux = np.vstack((aux, f))

    #aux = np.vstack([get_feat(df.values[i: i+ window].reshape(-1,), sig_lab=modality, sampling_rate=fs, feat_type=feat_types) for i in range(0, len(df)-window, overlap_window)])
    
    return pd.DataFrame(aux, columns=feature_names)


def expand_pre_post_sz(seizures, preseizure, postseizure):

    expanded_seizures = np.copy(seizures)

    uni = np.unique(seizures)

    for sz in uni:
        if sz == 0: 
            continue
        indx = np.argwhere(seizures == sz)
        start_ind = max(int(indx[0])-preseizure, 0)
        end_ind = min(int(indx[-1])+postseizure+1, len(seizures))
        aux_ind = np.arange(start_ind, end_ind)
        np.put(expanded_seizures, aux_ind, sz*np.ones((len(aux_ind),)))

    return expanded_seizures


