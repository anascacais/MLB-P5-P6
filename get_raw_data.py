# built-in
import os
import pickle

# third-party 
import pandas as pd
import numpy as np
import pyedflib as pyedf

# local
import utils

def get_baseline_seizure_data(patients_info_dir, saving_dir):

    list_patients = [patient_id for patient_id in os.listdir(patients_info_dir) if 'MSEL' in patient_id]

    for patient_id in list_patients:    

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        get_baseline_data(os.path.join(saving_dir, pat.id), pat)
        get_seizures_data(os.path.join(saving_dir, pat.id), pat)

        # remove patient folder if empty
        if os.listdir(os.path.join(saving_dir, pat.id)) == []:
            os.rmdir(os.path.join(saving_dir, pat.id))




# ---------- AUXILIARY FUNCTIONS ---------- #

def get_baseline_data(saving_dir, pat):

    # get the baseline files
    baseline_files = [file for file in os.listdir(pat.path) if (file not in utils.get_seizure_files(pat) and file.endswith('.edf') and 'Empatica' in file)]

    if baseline_files == []:
        print('    patient has no baseline Empatica files')
        return None

    #get the modalities present in the baseline files
    target_mod = set([base.split(' - ')[-1][:-4] for base in baseline_files])

    if all([os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}')) for modality in target_mod]):
        print('    patient already has baseline data')
        return None

    # run each date to join all corresponding modalities in a single dataframe
    for modality in target_mod:

        if os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}')):
            print(f'        patient already has modality {modality}')
            continue

        print(f'    --- Checking modality {modality} ---')

        #create a new dataframe for modality
        df = pd.DataFrame()

        # get the dates associated with the modality
        baseline_dates  = set([base.split(' - ')[1] for base in baseline_files if modality in base])

        for date in sorted(baseline_dates):

            name = f'{pat.id} - {date} - {modality}.edf'
            print(f'        file {name}')

            try:
                edf = pyedf.EdfReader(os.path.join(pat.path, name))
            except Exception as e:
                print(e)

            # concatenate the new dataframe with df
            df = pd.concat((df, utils.edf_to_df(edf, modality)), axis=0) 

        df.to_pickle(os.path.join(saving_dir, f'baseline_data_{modality}'))



def get_seizures_data(saving_dir, pat):

    seizure_files = [file for file in utils.get_seizure_files(pat) if 'Empatica' in file]
    
    if seizure_files == []:
        print('    patient has no seizures recorded in Empatica files')
        return None

    target_mod = list(set([base.split(' - ')[-1][:-4] for base in seizure_files]))

    if all([os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}.edf')) for modality in target_mod]):
        print('    patient already has seizures data')
        return None

    for modality in target_mod:

        if os.path.exists(os.path.join(saving_dir, f'seizures_data_{modality}')):
            print(f'        patient already has modality {modality}')
            continue

        print(f'    --- Checking modality {modality} ---')

        #create a new dataframe for each modality
        df = pd.DataFrame()

        #get the dates associated with the modality
        seizure_dates  = set([base.split(' - ')[1] for base in seizure_files if modality in base])

        for date in sorted(seizure_dates):

            name = f'{pat.id} - {date} - {modality}.edf'
            print(f'        file {name}')

            edf = pyedf.EdfReader(os.path.join(pat.path, name))

            # check which seizure this file has
            sz = list(pat.seizures.keys())[[name in files for files in [list(d.keys()) for d in  pat.seizures.values()]].index(True)]
            
            # turn to dataframe and add seizure column
            aux_df = utils.edf_to_df(edf, modality)

            aux_sz = np.zeros((len(aux_df),))
            aux_sz[pat.seizures[sz][name]['sz_start'] : pat.seizures[sz][name]['sz_end']+1] = int(sz.split('_')[-1]) * np.ones((pat.seizures[sz][name]['sz_end']+1 - pat.seizures[sz][name]['sz_start'],))

            aux_df = pd.concat((aux_df, pd.DataFrame(aux_sz, columns=['sz'], index=aux_df.index)), axis=1)    

            # concatenate the new dataframe with df
            df = pd.concat((df, aux_df), axis=0) 

        df.to_pickle(os.path.join(saving_dir, f'seizures_data_{modality}'))
        