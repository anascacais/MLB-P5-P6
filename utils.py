# built-in
import datetime

# third-party
import pandas as pd
import numpy as np
import biosppy as bp


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


def get_seizure_files(patient):

    seizure_files = []

    for sz in list(patient.seizures.keys()):

        seizure_files += list(patient.seizures[sz].keys()) 

    return seizure_files


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
    elif 'hr' in label.lower():
        filtered = (signal*fs) / 60

    return filtered