# built-in
import os
import pickle

# local
from patient import patient
import utils as utils

def annot2patient(db_dir, saving_directory):

    if not os.path.exists(saving_directory):
        os.makedirs(saving_directory)

    list_patients = [patient_dir for patient_dir in os.listdir(db_dir) if (
        os.path.isdir(os.path.join(db_dir, patient_dir)))]

    print(f'Patients to check: {list_patients}')

    for patient_id in list_patients:

        if patient_id in os.listdir(saving_directory):
            print(f'\n--- Patient {patient_id} already in patient dir ---')

        else:

            print(f'\n--- Checking patient {patient_id} ---')

            pat = patient(patient_id, files_path=os.path.join(
                db_dir, patient_id))
            pat.modalities = pat.get_modalities_available()

            # this will return a dict whose values are None, but that will be changed later on
            print(f'    modalities: {pat.modalities}')

            pat.seizures_csv = pat.get_seizures_csv()
            print(f'    number of seizure events: {len(pat.seizures_csv)}')
            dict_seizures = {}
            i = 0
            for sz_event in pat.seizures_csv:
                dict_seizures['Seizure_' + str(i+1)] = {}
                
                print(f'\n    --- Checking seizure {str(i+1)} ---')

                for mod in pat.modalities:

                    list_files = [file for file in os.listdir(pat.path) if (
                        file.endswith('.edf') and mod in file)]

                    sz_files = utils.get_possible_files(
                        list_files=list_files, sz_event=sz_event)

                    for file in sz_files:

                        aux = pat.get_seizure_timestamps(
                            file_path=os.path.join(pat.path, file), sz_event=sz_event, mod=mod)

                        if aux is not None:
                            dict_seizures['Seizure_' + str(i+1)][file] =  aux
                i += 1
            pat.seizures = dict_seizures

            print(f'\n    seizures: {pat.seizures}')

            with open(os.path.join(saving_directory, pat.id), 'wb') as outp:
                pickle.dump(pat, outp)
