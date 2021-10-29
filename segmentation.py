
import os

import datetime 
import biosppy as bp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import utils

patient_id = '01097'
modalities = ['TEMP']

start_directory = 'Df_raw_data'
saving_directory = 'Df_filt_data'
if not os.path.isdir(saving_directory):
    os.mkdir(saving_directory)

file_name = [file for file in os.listdir(os.path.join(start_directory, patient_id)) if 'TEMP' in file][0]
file = pd.read_pickle(os.path.join(start_directory, patient_id, file_name))

file_name = [file for file in os.listdir(os.path.join(start_directory, patient_id)) if 'EDA' in file][0]
file_eda = pd.read_pickle(os.path.join(start_directory, patient_id, file_name))

all = file.join(file_eda, how='outer')
int_window = 20*128
window = datetime.timedelta(seconds=2)
for i in range(0, len(all)-1, int_window):
    val_temp = (all.between_time(all.index[i].time(), (all.index[i+1]+window).time())['Empatica-TEMP.edf'].dropna().shape[0])
    val_eda = (all.between_time(all.index[i].time(), (all.index[i+1]+window).time())['Empatica-EDA.edf'].dropna().shape[0])    
    
    if (val_temp < int_window or val_eda < int_window):
        print(val_temp, val_eda)
        print('----------\n')

for modality in modalities:

    file_name = [file for file in os.listdir(os.path.join(start_directory, patient_id)) if modality in file][0]
    file = pd.read_pickle(os.path.join(start_directory, patient_id, file_name))
    

    diff_time_aux = np.diff(file.index).astype('timedelta64[ms]')
    diff_time = np.argwhere(diff_time_aux != datetime.timedelta(milliseconds=7))

    start = 0
    end = -1
    filtered_df = pd.DataFrame()
    if len(diff_time) > 0:
        for diff in diff_time:

            end = diff[0]
        
            crop_signal = file[modality][start:end]
            signal = utils.filter_modality(crop_signal, modality)
            

            start = int(diff[0])
    else:
        crop_signal = file[start:end].values.reshape(-1)
        signal = utils.filter_modality(crop_signal, modality)
    
    print('here')