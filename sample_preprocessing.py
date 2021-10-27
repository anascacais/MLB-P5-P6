# built-in
import os
import pickle

# --------- CHANGE BEFORE RUNNING --------- #

db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
patients_info_dir = '/Users/anascacais/Documents/Patients-Info'
saving_dir = '/Users/anascacais/Documents/Data'

# choose target modalities (the order doesn't matter)
target_modalities = ['Empatica-ACC', 'Empatica-EDA', 'Empatica-BVP', 'Empatica-HR', 'Empatica-TEMP'] 

# ----------------------------------------- #

target_modalities = list(set(target_modalities))
list_patients = [patient_id for patient_id in os.listdir(patients_info_dir)]

for patient_id in list_patients:    

    if patient_id != 'MSEL_01828': ## this condition is just a test
        continue

    pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
    print(f'\n--- Checking patient {pat.id} ---')

    if not os.path.isdir(os.path.join(saving_dir, pat.id)):
        os.makedirs(os.path.join(saving_dir, pat.id))
        pat.get_baseline_data(os.path.join(saving_dir, pat.id))
        
    # if os.path.exists(os.path.join(saving_dir, pat.id, 'baseline_data_NaN')):   
    #     print('    patient already has baseline with NaN')
    
    else:
        print('    patient already has baseline data')

    if patient_id != 'MSEL_01828': ## this condition is just a test
        continue

    else:
        if not os.path.exists(os.path.join(saving_dir, pat.id, f'baseline_{"_".join(target_modalities)}')):
            pat.get_joint_modalities(target_modalities, os.path.join(saving_dir, pat.id))