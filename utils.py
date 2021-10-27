# built-in
import os
import math
import datetime

# third-party
import pandas as pd
import pyedflib as pyedf
import numpy as np


def get_possible_files(list_files, sz_event):

       """
       Parameters
       ----------
       path : string
              Path to the directory that holds the patient's files.
       list_files : list
              List with the names of the files for corresponding patient and modality.
       sz_event : map
              Dict with "start_time" and "end_time" as keys ans the corresponding timestamp as value

       Returns
       -------
       list
              List with the names of the files that may contain (segments) of the desired seizure event
       
       """

       # from the names of the files, get start time of files (frist to datetime and then convert to timestamp)
       files_starts = {datetime.datetime.timestamp(datetime.datetime.strptime(file.split('-')[1], ' %y.%m.%d %H.%M.%S ')) : file for file in list_files}

       aux_list = list(files_starts.keys()) + [sz_event['start_time'], sz_event['end_time']]
       aux_list.sort()
       
       idx_aux = [i for i,t in enumerate(aux_list) if (t == sz_event['start_time'] or t == sz_event['end_time'])]
       
       # this gets the file immediately before the seizure start and the one that includes the seizure end (which could be the same)
       return [files_starts[t] for t in aux_list[idx_aux[0]-1 : idx_aux[1]-1] if t != sz_event['start_time']]


def edf_to_df(edf, col_name):
    """
    Parameters
    ----------
        edf : edf file
                edf to process
        col_name: str
                example: Empatica-HR-0

    Returns
    -------
    dataframe
            Dataframe with timestamps as index and the modality as column name
            If there is more than one column, they will be stacked with the suffix "_1", "_2", as it happens for the ACC
    
    """
    
    for n in range(edf.signals_in_file):

        signal = edf.readSignal(n)

        if 'HR' in col_name:
            start_time = edf.getStartdatetime() - datetime.timedelta(seconds = 10)
        
        else:
            start_time = edf.getStartdatetime()
        
        base_index = pd.date_range(start_time, start_time + datetime.timedelta(seconds=len(signal)/edf.getSampleFrequency(0)), periods=len(signal))
        
        if n == 0:
            baseline_df = pd.DataFrame(signal, columns=[col_name], index = base_index)
            continue
        
        baseline_df[col_name + '_' + str(n)] = signal

    return baseline_df



def edf_to_df_seizure(edf, col_name, sz_dict, preseizure=0, postseizure=0):
    """
    Parameters
    ----------
        edf : edf file
                edf to process
        sz_dict: dict
                contains file name, sz start and sz end 

    Returns
    -------
    dataframe
            Dataframe with timestamps as index and the modality as column name
            If there is more than one column, they will be stacked with the suffix "_1", "_2", as it happens for the ACC
    
    """

    start_time = edf.getStartdatetime()
    sz_start_time = start_time + datetime.timedelta(seconds = (-preseizure + sz_dict['sz_start']/edf.getSampleFrequency(0)))
    sz_end_time = start_time + datetime.timedelta(seconds = (postseizure + sz_dict['sz_end']/edf.getSampleFrequency(0)))
    
    pre_ = int(preseizure * edf.getSampleFrequency(0))
    post_ = int(postseizure * edf.getSampleFrequency(0))
    label_ = np.hstack([np.zeros(pre_), np.ones(sz_dict['sz_end'] - sz_dict['sz_start']), np.zeros(post_)])

    time_index = pd.date_range(start=sz_start_time, end= sz_end_time, periods = len(label_))
    seizure_df = pd.DataFrame(label_, columns=['SZ'], index=time_index)

    for n in range(edf.signals_in_file):        
        signal = edf.readSignal(n)
        sig_crop = signal[sz_dict['sz_start']-pre_ : sz_dict['sz_start']-pre_ + len(time_index)]
        if len(sig_crop) < len(time_index):
            seizure_df = seizure_df[:len(sig_crop)]
        seizure_df[col_name + '_' + str(n)] = sig_crop

    return seizure_df