# built-in
import os
import pickle
from datetime import timedelta

# third-party
import pandas as pd
import numpy as np


# --------- CHANGE BEFORE RUNNING --------- #

src_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/Data'

# choose a new directory to save the joint modalities LOCALLY - so there's no issue with altering your colleagues' work
saving_dir = '/Users/anascacais/Documents/MLB-features'

# choose modalities and patients (for all available, choose None)
modalities = ['EDA', 'BVP'] 
patients = ['MSEL_01870']

window = 20
overlap = 0.5

# ----------------------------------------- #

def join_modalities(src_dir, patients, modalities): 

    patients_info_dir = os.path.join(src_dir, 'patients-info')
    features_dir = os.path.join(src_dir, 'features-data')

    if patients is None:
        patients = [patient_id for patient_id in os.listdir(features_dir) if os.path.isdir(features_dir, patient_id)]

    for patient_id in patients:

        pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
        print(f'\n--- Checking patient {pat.id} ---')

        if modalities is None:
            modalities = list(pat.modalities.keys())

        modalities.sort()

        if not os.path.isdir(os.path.join(saving_dir, pat.id)):
            os.makedirs(os.path.join(saving_dir, pat.id))

        filename = f'features_b_{"-".join(modalities)}_{window}s_{int(overlap*100)}.npy'
        if filename in os.listdir(os.path.join(saving_dir, pat.id)):
            print('     modalities already joint for baseline')
        else:
            join(modalities, features_dir, pat, saving_path= os.path.join(saving_dir, pat.id, filename), type='baseline')
        
        filename = f'features_s_{"-".join(modalities)}_{window}s_{int(overlap*100)}.npy'
        if filename in os.listdir(os.path.join(saving_dir, pat.id)):
            print('     modalities already joint for seizures')
        else:
            join(modalities, features_dir, pat, saving_path= os.path.join(saving_dir, pat.id, filename), type='seizures')


def join(modalities, features_dir, pat, saving_path, type):

    print(f'     handling {type}')

    joint = pd.DataFrame()
    for m,modality in enumerate(modalities):

        print(f'        joining {modality}')
        
        mod = pd.read_hdf(os.path.join(features_dir, pat.id, f'features_{type[0]}_{modality}_{window}s_{int(overlap*100)}.h5'))
        mod = mod.set_index(mod.index.round('ms'))
        
        if type == 'seizures':
            joint = joint.join(mod, how='outer', lsuffix=f'_{modalities[m-1]}')
        else:
            joint = joint.join(mod, how='outer')

    joint_ = joint.dropna()

    # computing lost time by joining modalities and discarding non-aligned samples
    diffs_ind_joint_ = np.where(np.diff(joint_.index).astype('timedelta64[s]') > timedelta(seconds=10))[0]
    diffs_joint_ = [joint_.index[diffs_ind_joint_[i]+1] - joint_.index[diffs_ind_joint_[i]] for i in range(len(diffs_ind_joint_))]

    diffs_ind_joint = np.where(np.diff(joint.index).astype('timedelta64[s]') > timedelta(seconds=10))[0]
    diffs_joint = [joint.index[diffs_ind_joint[i]+1] - joint.index[diffs_ind_joint[i]] for i in range(len(diffs_ind_joint))]

    print(f'        -- lost time by joining modalitites: {np.sum(diffs_joint_) - np.sum(diffs_joint)}')

    if type == 'seizures':
        joint_ = joint_.drop(columns=['sz_'+m for m in modalities[:-1]])

    joint_array = joint_.to_numpy()
    with open(saving_path, 'wb') as f:
        np.save(f, joint_array)


if __name__ == "__main__":
    join_modalities(src_dir, patients, modalities)