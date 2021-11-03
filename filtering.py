# built-in
import os
import datetime 
import pickle

# third-party
import numpy as np
import pandas as pd

# local
import utils


def filter_data(saving_dir, patients_info_dir, raw_data_dir, modalities=None, list_patients=None):

    if list_patients is None:
        list_patients = [patient_id for patient_id in os.listdir(raw_data_dir) if os.path.isdir(os.path.join(raw_data_dir, patient_id))] 

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if modalities is None:
            modalities = list(pat.modalities.keys())

        filter_pat_data(saving_dir, raw_data_dir, pat, modalities)

        
# ---------- AUXILIARY FUNCTIONS ---------- #            

def filter_pat_data(saving_directory, start_directory, pat, modalities):

    # confirm is patient is in the new directory and create new directory if not
    if not os.path.isdir(os.path.join(saving_directory, pat.id)):
        os.makedirs(os.path.join(saving_directory, pat.id))

    for modality in modalities:
        print('     Filtering --- ' + modality)
        
        # get the file name of the modality, within the start directory
        file_names = [file for file in os.listdir(os.path.join(start_directory, pat.id)) if modality in file]

        for file_name in file_names:

            if ('baseline' in file_name and 'filtered_b_data_' + modality in os.listdir(os.path.join(saving_directory, pat.id))):
                print(f'     modality was already filtered for baseline, this task will be ignored')
                continue
            elif ('seizure' in file_name and 'filtered_s_data_' + modality in os.listdir(os.path.join(saving_directory, pat.id))):
                print(f'     modality was already filtered for seizure, this task will be ignored')
                continue
            
            # open the file as a dataframe
            file = pd.read_pickle(os.path.join(start_directory, pat.id, file_name))

            # create new dataframe
            fs = pat.modalities[modality]
            filtered_df = get_filtered_data(file, fs)

            if 'baseline' in file_name:
                letter = 'b'

            elif 'seizure' in file_name:
                letter = 's'
                filtered_df['sz'] = file['sz']

            pickle.dump(filtered_df, open(os.path.join(saving_directory, pat.id, 'filtered_'+ letter +'_data_' + modality), 'wb'))
            

def get_filtered_data(df, fs, resolution='ms'):

    # confirm if there are jumps in the timestamps 
    diff_time = np.diff(df.index).astype(f'timedelta64[{resolution}]')
    diff_time = np.argwhere(diff_time != datetime.timedelta(milliseconds=np.floor((1/fs)*1000))) 

    start, end = 0, -1
    filtered_df = pd.DataFrame(columns=df.columns)

    if len(diff_time) != 0:

        diff_time = np.append(diff_time, [len(df)-1])

        for diff in diff_time:
            
            end = diff+1
            crop_df = df.iloc[start:end]

            for m in [df.columns[0]]:
                crop_signal = crop_df[m].values.reshape(-1)
                signal = utils.filter_modality(crop_signal, m)
                filtered_df = pd.concat((filtered_df, pd.DataFrame(signal, index=df.index[start:end], columns=[m])))
            
            start = diff+1

    else:
        for m in [df.columns[0]]:
            crop_signal = df[start:end][m].values.reshape(-1)
            signal = utils.filter_modality(crop_signal, m)
            filtered_df = pd.concat((filtered_df, pd.DataFrame(signal, index=df.index[start:end], columns=[m])))


    return filtered_df
