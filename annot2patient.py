# built-in
import os
import pickle

# local
from patient import patient
import utils as utils

# --------- CHANGE BEFORE RUNNING --------- #

# the directory should be a folder containing folders with the patients' IDs,
# each containing all the patient's files
directory = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'

# choose directory where to save the patient class objects created below
saving_directory = os.path.join('/Users/anascacais/Documents', 'Patients-Info')

# ----------------------------------------- #

if not os.path.exists(saving_directory):
    os.makedirs(saving_directory)

list_patients = [patient_dir for patient_dir in os.listdir(directory) if (
    os.path.isdir(os.path.join(directory, patient_dir)))]

print(f'Patients to check: {list_patients}')

for patient_id in list_patients:

    if patient_id in os.listdir(saving_directory):
        print(f'\n--- Patient {patient_id} already in patient dir ---')

    else:

        print(f'\n--- Checking patient {patient_id} ---')

        pat = patient(patient_id, files_path=os.path.join(
            directory, patient_id))
        pat.modalities = pat.get_modalities_available()

        print(f'    modalities: {pat.modalities}')

        pat.seizures_csv = pat.get_seizures_csv()
        print(f'    number of seizure events: {len(pat.seizures_csv)}')
        dict_seizures = {}
        i = 0
        for sz_event in pat.seizures_csv:
            dict_seizures['Seizure_' + str(i)] = {}
            

            print(f'\n    --- Checking seizure {sz_event["start_time"]} ---')

            for mod in pat.modalities:

                list_files = [file for file in os.listdir(pat.path) if (
                    file.endswith('.edf') and mod in file)]

                sz_files = utils.get_possible_files(
                    list_files=list_files, sz_event=sz_event)

                for file in sz_files:

                    aux = utils.get_seizure_timestamps(
                        file_path=os.path.join(pat.path, file), sz_event=sz_event, mod=mod)

                    if aux is not None:
                        dict_seizures['Seizure_' + str(i)][file] =  aux
            i += 1
        pat.seizures = dict_seizures

        print(f'\n    seizures: {pat.seizures}')

        with open(os.path.join(saving_directory, pat.id), 'wb') as outp:
            pickle.dump(pat, outp)
