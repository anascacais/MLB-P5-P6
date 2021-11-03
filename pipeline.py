# built-in
import os
import pickle

# local
from annot2patient import annot2patient
from get_raw_data import get_baseline_seizure_data
from filtering import filter_data, get_filtered_data
from feat_extraction import feat_extraction

# --------- CHANGE BEFORE RUNNING --------- #

# the directory should be a folder containing folders with the patients' IDs,
# each containing all the patient's files
db_dir = 'MLB-Seer'
# choose directory where to save the project's data
src_dir = os.getcwd()

# choose modalities
modalities = ['EDA']

# ----------------------------------------- #

patients_info_dir = os.path.join(src_dir, 'Patients-Info')
raw_data_dir = os.path.join(src_dir, 'raw_data_df')
filt_data_dir = os.path.join(src_dir, 'filtered-data-df')
features_dir = os.path.join(src_dir, 'features_data')

annot2patient(db_dir, patients_info_dir)
print('Get baseline and seizure data ...')
get_baseline_seizure_data(patients_info_dir, raw_data_dir)
print('Filter baseline and seizure data ...')
filter_data(filt_data_dir, patients_info_dir, raw_data_dir, modalities)
print('Extract baseline and seizure data ...')
feat_extraction(patients_info_dir, filt_data_dir, features_dir, preseizure=300, postseizure=120, window=20, feat_types=['temp', 'stat', 'spec', 'signal'], modalities=['EDA'])

