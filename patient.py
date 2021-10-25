# from this project
import utils

# built-in
import os
import pickle

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
        modalities : list
            List with the modalities recorded for that patient
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

       return list(set(list_files))

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
       #return [{'start_time': int(df.iloc[isz]['start_time'])/1000, 'end_time': int(df.iloc[isz]['end_time'])/1000} for isz in list(df.index)]
