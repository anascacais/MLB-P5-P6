# built-in
import os
import pickle

# local
from annot2patient import annot2patient
from get_raw_data import get_baseline_seizure_data
from filtering import filter_data
from feat_extraction import feat_extraction

# --------- CHANGE BEFORE RUNNING --------- #

# the directory should be a folder containing folders with the patients' IDs,
# each containing all the patient's files
db_dir = 'MLB-Seer'
# choose directory where to save the project's data
src_dir = os.getcwd()

# choose modalities (for all modalities available, choose None)
modalities = ['EDA'] 

# choose time interval to consider as seizure before and after the annotated seizure
preseizure = 30
postseizure = 10

# choose type of features to extract
feat_types = ['temp', 'stat', 'spec', 'signal']

# choose parameters of sliding window approach
window = 5 # in seconds
overlap = 0.5 # in percentage (of window)

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
feat_extraction(patients_info_dir, filt_data_dir, features_dir, feat_types, modalities, preseizure, postseizure, window, overlap)


