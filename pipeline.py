# built-in
import os
import pickle

# local
from annot2patient import annot2patient
from get_raw_data import get_baseline_seizure_data
from feat_extraction import feat_extraction

# --------- CHANGE BEFORE RUNNING --------- #

# the directory should be a folder containing folders with the patients' IDs,
# each containing all the patient's files
db_dir = '/Users/anascacais/OneDrive - Universidade de Lisboa/BD-SEER'

# choose directory where to save the project's data
src_dir = '/Users/anascacais/Documents'

# ----------------------------------------- #

patients_info_dir = os.path.join(src_dir, 'patient-info')
raw_data_dir = os.path.join(src_dir, 'raw_data_df')
filt_data_dir = os.path.join(src_dir, 'filtered-data-df')
features_dir = os.path.join(src_dir, 'features')

annot2patient(db_dir, patients_info_dir)
get_baseline_seizure_data(patients_info_dir, raw_data_dir)
# filter_data()
feat_extraction()
