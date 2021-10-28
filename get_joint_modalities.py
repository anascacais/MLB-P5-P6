# built-in
import os
import pickle

# --------- CHANGE BEFORE RUNNING --------- #

patients_info_dir = '/Users/anascacais/Documents/Patients-Info'
modalities_dir = '/Users/anascacais/Documents/DF-Raw-Data'
saving_dir = '/Users/anascacais/Documents/DF-Joint-Modalities'

# choose target modalities (the order doesn't matter)
target_modalities = ['Empatica-ACC', 'Empatica-EDA'] 

# ----------------------------------------- #

target_modalities = list(set(target_modalities))

list_patients = [patient_id for patient_id in os.listdir(patients_info_dir)]

for patient_id in list_patients:  

    pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
    print(f'\n--- Checking patient {pat.id} ---') 

    if patient_id != 'MSEL_01828': ## this condition is just a test
        continue

    else:
        if not os.path.isdir(os.path.join(saving_dir, "_".join(target_modalities))):
            os.makedirs(os.path.join(saving_dir, "_".join(target_modalities)))

        # get joint modalities for baseline
        if not os.path.exists(os.path.join(saving_dir, "_".join(target_modalities), pat.id)):
            pat.get_joint_modalities(target_modalities, modalities_dir, os.path.join(saving_dir, "_".join(target_modalities)))

        # get joint modalities for seizures
        