
import datetime

import biosppy as bp
from biosppy import signals
import numpy as np
import pandas as pd


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
        base_index = pd.date_range(start_time, start_time + datetime.timedelta(seconds=len(signal)/edf.getSampleFrequency(0)), freq='128H')
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
        seizure_df[col_name + '_' + str(n)] = signal[sz_dict['sz_start']-pre_ : post_ + sz_dict['sz_end']]

    return seizure_df


def filter_modality(crop_signal, label, fs=128):

    # ensure numpy
    signal = np.array(crop_signal)
    fs = float(fs)

    if 'eda' in label.lower():
        aux, _, _ = bp.signals.tools.filter_signal(
        signal=signal,
        ftype="butter",
        band="lowpass",
        order=4,
        frequency=5,
        sampling_rate=fs,)
        # smooth
        sm_size = int(0.75 * fs)
        filtered, _ = bp.signals.tools.smoother(signal=aux, kernel="boxzen", size=sm_size, mirror=True)

    elif 'bvp' in label.lower():
        filtered, _, _ = bp.signals.tools.filter_signal(signal=signal,
                                      ftype='butter',
                                      band='bandpass',
                                      order=4,
                                      frequency=[1, 8],
                                      sampling_rate=fs)
        
    elif 'temp' in label.lower():
        sm_size = int(0.75 * fs)
        filtered, _ = bp.signals.tools.smoother(signal=signal, kernel="boxzen", size=sm_size, mirror=True)

    elif 'acc' in label.lower():
        sm_size = int(0.75 * fs)
        filtered, _ = bp.signals.tools.smoother(signal=signal, kernel="boxzen", size=sm_size, mirror=True)

    return filtered

