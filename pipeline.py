# built-in
import os
import pickle
import time

# local
from annot2patient import annot2patient
from get_raw_data import get_baseline_seizure_data
from filtering import filter_data
from feat_extraction import feat_extraction

# --------- CHANGE BEFORE RUNNING --------- #

# the directory should be a folder containing folders with the patients' IDs,
# each containing all the patient's files
db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-Seer'

# choose directory where to save the project's data
src_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/Data'

# choose modalities and patients (for all available, choose None)
modalities = ['EDA', 'HR', 'BVP', 'TEMP', 'ACC'] 
patients = ['MSEL_01870']

# choose time interval to consider as seizure before and after the annotated seizure
preseizure = 300
postseizure = 120

# choose type of features to extract
feat_types = {'EDA': ['temp', 'stat', 'spec', 'signal'], 'HR' : ['temp', 'signal'], 'BVP':['temp', 'stat'],'TEMP': ['temp', 'stat'], 'ACC': ['temp', 'stat']}

# choose parameters of sliding window approach
window = 20 # in seconds
overlap = 0.5 # in percentage (of window)

# ----------------------------------------- #

patients_info_dir = os.path.join(src_dir, 'patients-info')
raw_data_dir = os.path.join(src_dir, 'raw-data-df')
filt_data_dir = os.path.join(src_dir, 'filtered-data-df')
features_dir = os.path.join(src_dir, 'features-data')

#annot2patient(db_dir, patients_info_dir)

start_time = time.time()
print('Get baseline and seizure data ...')
get_baseline_seizure_data(patients_info_dir, raw_data_dir)
print('Raw data time ', time.time() - start_time)

#print('Filter baseline and seizure data ...')
start_time = time.time()
print('\n------------------------------------')
print('Filter baseline and seizure data ...')
filter_data(filt_data_dir, patients_info_dir, raw_data_dir, modalities, patients)
print('Raw data time ', time.time() - start_time)
#print('Extract baseline and seizure features ...')
start_time = time.time()
print('\n---------------------------------------')
print('Extract baseline and seizure features ...')
feat_extraction(patients_info_dir, filt_data_dir, features_dir, feat_types, modalities, patients, preseizure, postseizure, window, overlap)
print('Raw data time ', time.time() - start_time)
