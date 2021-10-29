# from this project
import utils

# built-in
import os
import math
import datetime

# third-party
import pandas as pd
import numpy as np
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
    
    

    def get_baseline_data(self, saving_dir, target_mod = None):
        """
       Parameters
       ----------
        pre_seizure : int
                seconds to include before a seizure
        post_seizure: int
                seconds to include after a seizure

       Returns
       -------
       dict<list<dataframe>>
              Dictionary where each entry is one seizure from one patient with an associated list of dataframes (seizure segments)
       
        """

        # get the baseline files
        baseline_files = [file for file in os.listdir(self.path) if (file not in self.get_seizure_files() and file.endswith('.edf') and 'Empatica' in file)]

        if baseline_files == []:
            print('    patient has no baseline Empatica files')
            return None

        #get the modalities present in the baseline files
        target_mod = set([base.split(' - ')[-1][:-4] for base in baseline_files])

        if all([os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}')) for modality in target_mod]):
            print('    patient already has baseline data')
            return None

        # run each date to join all corresponding modalities in a single dataframe
        for modality in target_mod:

            if os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}')):
                print(f'        patient already has modality {modality}')
                continue

            print(f'    --- Checking modality {modality} ---')

            #create a new dataframe for modality
            df = pd.DataFrame()

            # get the dates associated with the modality
            baseline_dates  = set([base.split(' - ')[1] for base in baseline_files if modality in base])

            for date in sorted(baseline_dates):

                name = f'{self.id} - {date} - {modality}.edf'
                print(f'        file {name}')

                edf = pyedf.EdfReader(os.path.join(self.path, name))

                # concatenate the new dataframe with df
                df = pd.concat((df, utils.edf_to_df(edf, modality)), axis=0) 

            df.to_pickle(os.path.join(saving_dir, f'baseline_data_{modality}'))



    def get_seizures_data(self, saving_dir):

        seizure_files = [file for file in self.get_seizure_files() if 'Empatica' in file]
        
        if seizure_files == []:
            print('    patient has no seizures recorded in Empatica files')
            return None

        target_mod = set([base.split(' - ')[-1][:-4] for base in seizure_files])

        if all([os.path.exists(os.path.join(saving_dir, f'baseline_data_{modality}.edf')) for modality in target_mod]):
            print('    patient already has seizures data')
            return None

        for modality in target_mod:

            if os.path.exists(os.path.join(saving_dir, f'seizures_data_{modality}')):
                print(f'        patient already has modality {modality}')
                continue

            print(f'    --- Checking modality {modality} ---')

            #create a new dataframe for each modality
            df = pd.DataFrame()

            #get the dates associated with the modality
            seizure_dates  = set([base.split(' - ')[1] for base in seizure_files if modality in base])

            for date in sorted(seizure_dates):

                name = f'{self.id} - {date} - {modality}.edf'
                print(f'        file {name}')

                edf = pyedf.EdfReader(os.path.join(self.path, name))

                # check which seizure this file has
                sz = list(self.seizures.keys())[[name in files for files in [list(d.keys()) for d in  self.seizures.values()]].index(True)]
                
                # turn to dataframe and add seizure column
                aux_df = utils.edf_to_df(edf, modality)

                aux_sz = np.zeros((len(aux_df),))
                aux_sz[self.seizures[sz][name]['sz_start'] : self.seizures[sz][name]['sz_end']+1] = int(sz.split('_')[-1]) * np.ones((self.seizures[sz][name]['sz_end']+1 - self.seizures[sz][name]['sz_start'],))

                aux_df = pd.concat((aux_df, pd.DataFrame(aux_sz, columns=['sz'], index=aux_df.index)), axis=1)    

                # concatenate the new dataframe with df
                df = pd.concat((df, aux_df), axis=0) 

            df.to_pickle(os.path.join(saving_dir, f'seizures_data_{modality}'))
            



    def get_joint_modalities(self, target_modalities, modalities_dir, saving_dir):

        df = pd.DataFrame()

        for modality in target_modalities:
            
            print(f'    joining modality {modality}')
            aux_df = pd.read_pickle(os.path.join(modalities_dir, self.id, f'baseline_data_{modality}'))
            df = df.join(aux_df, how='outer')

        # drop rows that have at least 1 NaN (i.e. timestamps with at least one modality missing)
        prev_len = len(df)
        df.dropna(inplace=True)
        print(df)
        print('   lost {:.2f}% of {:.0f} min of signal'.format(((prev_len - len(df)) / prev_len) * 100, (prev_len / self.modalities[modality.split('-')[1]]) / 60))

        # dump the final dataframe into a pickle
        df.to_pickle(os.path.join(saving_dir, f'{self.id}_baseline'))

    
    #def get_joint_modalities_sz(self, target_modalities, modalities_dir, saving_dir):


    def get_seizure_files(self):

        seizure_files = []

        for sz in list(self.seizures.keys()):

            seizure_files += list(self.seizures[sz].keys()) 

        return seizure_files



