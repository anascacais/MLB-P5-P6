# built-in
import os
import math
import datetime

# third-party
import pandas as pd
import pyedflib as pyedf

class patient:
    """
    usage example:

        import pickle

        with open([FILENAME], 'rb') as inp:
            pat = pickle.load(inp)

        print(pat.seizures)
    
    """

    def __init__(self, id, files_path):
        """
        Parameters
        ----------
        id : string
            ID of the patient
        files_path : string
            Directory where all the files of the corresponding patient are held
        modalities : dict
            Dict with the modalities recorded for that patient as keys and the sampling frequencies as values
        seizures_csv : list<dict<string,timestamp>>
            List in which each element corresponds to a dict with "start_time" and "end_time" as keys and the corresponding
            timestamp as value
        seizures : list<dict>
            List of dicts whose keys correspond to the file names that have at least a seizure segment and the values are 
            dicts with "sz_start" and "sz_end" as keys and the corresponding timestamp as value for the
              segment of the seizure event that are within that file 
        """

        self.id = id
        self.path = files_path
        self.modalities = None
        self.seizures_csv = None
        self.seizures = []


    def get_modalities_available(self):
       """
       Parameters
       ----------
       path : string
              Path to the directory that holds the patient's files.

       Returns
       -------
       list
              List with the unique modalities found within the patient's files.
       
       """

       # [-1] gets the last piece after the split by '-' ; [:-4] gets everything that comes before .edf
       list_files = [file.split('-')[-1][:-4] for file in os.listdir(self.path) if file.endswith('.edf')]

       return {key: None for key in list(set(list_files))}


    def get_seizure_timestamps(self, file_path, sz_event, mod):
       """
       Parameters
       ----------
       path : string
              Path to the directory that holds the patient's files.
       sz_event : map
              Dict with "start_time" and "end_time" as keys and the corresponding timestamp as value

       Returns
       -------
       dict, None
              Dict with the "sz_start" and "sz_end" as keys and the corresponding timestamp as value for the
              segment of the seizure event that are within that file 
              If the file cannot be opened or no part of the seizure event fits within the timeframe of the
              file, it returns None
       
       """

       try:
              edf = pyedf.EdfReader(file_path)
       except:
              print(f'        File {os.path.basename(file_path)} could not be opened')
              return None

       print(f'        channels: {edf.getSignalLabels()}')

       signal = edf.readSignal(0)
       fs = edf.getSampleFrequency(0)
       duration = len(signal) / fs

       self.modalities[mod] = fs

       start_time = datetime.datetime.timestamp(edf.getStartdatetime())
       end_time = start_time + duration

       edf.close()

       if (sz_event['start_time'] > end_time):
              print(f'             seizure not recorded for {mod} modality')
              return None

       else:
              # this covers all possibilities: (1) both the start and the end of the seizure are within the file 
              # (2) only the start or (3) the end of the seizure is within the file
              # (4) the start of the seizure is before the start of the file and the end is after the end of the file
              aux_start = math.floor((sz_event['start_time'] - start_time) * fs)
              aux_end = math.ceil((sz_event['end_time'] - start_time) * fs)

              start_ind = max(aux_start, 0)
              end_ind = min(aux_end, len(signal)-1)
              return {'sz_start': start_ind, 'sz_end': end_ind, 'type': sz_event['type']}


    def get_seizures_csv(self):
       """
       Parameters
       ----------
       path : string
              Path to the directory that holds the patient's files.

       Returns
       -------
       list<dict<string,timestamp>>
              List in which each element corresponds to a dict with "start_time" and "end_time" as keys ans the corresponding
              timestamp as value
       
       """

       csv_file = [file for file in os.listdir(self.path) if file.endswith('.csv')][0]
       df = pd.read_csv(os.path.join(self.path, csv_file))

       # divide by 1000 because it is in milliseconds and add the timezone
       return [{'start_time': int(df.iloc[isz]['start_time'])/1000, 'end_time': int(df.iloc[isz]['end_time'])/1000, 'type':df.iloc[isz]['note']} for isz in list(df.index)]
    
    




