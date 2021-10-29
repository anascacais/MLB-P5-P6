
import os

import datetime 
import biosppy as bp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

import utils

patient_id = '01097'
modalities = ['TEMP', 'EDA', 'BVP', 'ACC']

start_directory = 'Df_raw_data'
saving_directory = 'Df_filt_data'


def get_filtered_data(diff_time, file):

    start, end = 0, -1

    filtered_df = pd.DataFrame(columns=file.columns)

    if len(diff_time) > 0:
        for diff in diff_time:
            end = diff[0]
            for col in file.columns:
        
                crop_signal = file[col][start:end].values.reshape(-1)
                signal = utils.filter_modality(crop_signal, col)
                filtered_df = pd.concat((filtered_df, pd.DataFrame(signal, index=file.index[start:end], columns=[col])))

            start = int(diff[0])
    else:
        for col in file.columns:
            crop_signal = file[start:end].values.reshape(-1)
            signal = utils.filter_modality(crop_signal, col)
            filtered_df = pd.concat((filtered_df, pd.DataFrame(signal, index=file.index[start:end], columns=[col])))
    
    return filtered_df


def filter_baseline_data(saving_directory, start_directory, patient_id, modalities):

    # confirm is patient is in the new directory and create new directory if not
    if not os.path.isdir(os.path.join(saving_directory, patient_id)):
        os.makedirs(os.path.join(saving_directory, patient_id))

    for modality in modalities:
        print('Filtering ... ' + modality)
        
        # if filtered data already exists in directory, continue without processing
        if 'filtered_b_data_' + modality in os.listdir(os.path.join(saving_directory, patient_id)):
            print(modality + ' was already filtered, this task be ignored.')
            continue
        
        # get the file name of the modality, within the start directory
        file_name = [file for file in os.listdir(os.path.join(start_directory, patient_id)) if modality in file][0]
        
        # open the file as a dataframe
        file = pd.read_pickle(os.path.join(start_directory, patient_id, file_name))

        # confirm if there are jumps in the timestamps 
        diff_time_aux = np.diff(file.index).astype('timedelta64[ms]')
        diff_time = np.argwhere(diff_time_aux != datetime.timedelta(milliseconds=7))

        
        # create new dataframe
        filtered_df = get_filtered_data(diff_time, file)
        pickle.dump(filtered_df, open(os.path.join(saving_directory, patient_id, 'filtered_b_data_' + modality), 'wb'))
        

filter_baseline_data(saving_directory, start_directory, '01828', modalities)