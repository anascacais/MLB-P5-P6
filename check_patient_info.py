import pandas as pd
import os
import pickle

db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
src_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/Data'

patients_info_dir = os.path.join(src_dir, 'patients-info')

list_patients = [patient_dir for patient_dir in os.listdir(db_dir) if (
    os.path.isdir(os.path.join(db_dir, patient_dir)))]

print(f'Patients to check: {list_patients}')

for patient_id in list_patients:

    print(f'\n--- Checking patient {patient_id} ---')

    with open(os.path.join(patients_info_dir, patient_id), 'rb') as inp:
        pat = pickle.load(inp)

    csv_file = [file for file in os.listdir(os.path.join(patients_info_dir, pat.id)) if file.endswith('.csv')][0]
    df = pd.read_csv(os.path.join(patients_info_dir, pat.id, csv_file))

    if len(df) == len(pat.seizures): 
        print('     all good!')
    else:
        print(f'    expected: {len(df)} | real: {len(pat.seizures)}')