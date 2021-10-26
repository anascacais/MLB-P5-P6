import pandas as pd
import os
import pickle

db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'
patient_dir = os.path.join('/Users/anascacais/Documents', 'Patients-Info')

list_patients = [patient_dir for patient_dir in os.listdir(db_dir) if (
    os.path.isdir(os.path.join(db_dir, patient_dir)))]

print(f'Patients to check: {list_patients}')

for patient_id in list_patients:

    print(f'\n--- Checking patient {patient_id} ---')

    with open(os.path.join(patient_dir, patient_id), 'rb') as inp:
        pat = pickle.load(inp)

    csv_file = [file for file in os.listdir(pat.path) if file.endswith('.csv')][0]
    df = pd.read_csv(os.path.join(pat.path, csv_file))

    if len(df) == len(pat.seizures): 
        print('     all good!')
    else:
        print(f'    expected: {len(df)} | real: {len(pat.seizures)}')