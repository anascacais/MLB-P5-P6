# built-in
import os
import pickle


db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
patients_info_dir = '/Users/anascacais/Documents/Patients-Info'
saving_dir = '/Users/anascacais/Documents/Data'

list_patients = [patient_id for patient_id in os.listdir(patients_info_dir)]

lost_data = {}

for patient_id in list_patients:    
    
    # if patient_id != 'MSEL_01828':
    #     continue

    pat = pickle.load(open(os.path.join(patients_info_dir, patient_id), 'rb'))
    print(f'\n--- Checking patient {pat.id} ---')

    if not os.path.isdir(os.path.join(saving_dir, pat.id)):
        os.makedirs(os.path.join(saving_dir, pat.id))
        
    if os.path.exists(os.path.join(saving_dir, pat.id, 'baseline_data_NaN')):   
        print('    patient already has baseline with NaN')
    
    else:
        pat.get_baseline_data(os.path.join(saving_dir, pat.id))

