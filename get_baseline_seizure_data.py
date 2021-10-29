# built-in
import os
import pickle

# --------- CHANGE BEFORE RUNNING --------- #

db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
patients_info_dir = '/Users/anascacais/Documents/Patients-Info'
saving_dir = '/Users/anascacais/Documents/DF-Raw-Data'

# ----------------------------------------- #

list_patients = [patient_id for patient_id in os.listdir(patients_info_dir)]
print(list_patients)

for patient_id in list_patients:    

    pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
    print(f'\n--- Checking patient {pat.id} ---')

    if not os.path.isdir(os.path.join(saving_dir, pat.id)):
        os.makedirs(os.path.join(saving_dir, pat.id))

    pat.get_baseline_data(os.path.join(saving_dir, pat.id))
    pat.get_seizures_data(os.path.join(saving_dir, pat.id))

    # remove patient folder if empty
    if os.listdir(os.path.join(saving_dir, pat.id)) == []:
        os.rmdir(os.path.join(saving_dir, pat.id))
