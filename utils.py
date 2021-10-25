
import datetime

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
        base_index = pd.date_range(start_time, start_time + datetime.timedelta(seconds=len(signal)/edf.getSampleFrequency(0)), periods=len(signal))
        if n == 0:
            baseline_df = pd.DataFrame(signal, columns=[col_name], index = base_index)
            continue
        baseline_df[col_name + '_' + str(n)] = signal

    return baseline_df