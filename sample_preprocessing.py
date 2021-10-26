# built-in
import os
import pickle

# get_baseline_data

patient_id = 'MSEL_01763'
file_path = '/Users/anascacais/Documents/MLB-Seer'
file_info = '/Users/anascacais/Documents/Patients-Info'
saving_directory = '/Users/anascacais/Documents/Data'

pat = pickle.load(open(os.path.join(file_info, patient_id), 'rb'))

if not os.path.isdir(os.path.join(saving_directory, pat.id)):
    os.mkdir(os.path.join(saving_directory, pat.id))

# TEST SEIZURES
if pat.id + '_seizures_data' not in os.listdir(os.path.join(saving_directory)):
    pat.get_seizures_data(pat, saving_directory=saving_directory, file_path = file_path)

seizures = pickle.load(open(os.path.join(saving_directory, patient_id + '_seizures_data'), 'rb'))

import matplotlib.pyplot as plt

for seizure in seizures.keys():
    plt.plot(seizures[seizure]['Empatica-EDA'])

# TEST BASELINE

if len([file for file in os.listdir(os.path.join(saving_directory)) if 'baseline in file']) > 0:
    pat.get_baseline_data(pat, saving_directory, file_path)

baseline = pickle.load(open(os.path.join(saving_directory, patient_id + '_baseline_data_Empatica-EDA'), 'rb'))

plt.figure()
plt.plot(baseline)
plt.show()
