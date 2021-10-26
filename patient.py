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
       return [{'start_time': int(df.iloc[isz]['start_time'])/1000, 'end_time': int(df.iloc[isz]['end_time'])/1000, 'type':df.iloc[isz]['note']} for isz in list(df.index)]
    
    

    def get_baseline_data(self, saving_directory = None, file_path = 'MLB-Seer'):
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
        if saving_directory is None:
            saving_directory = file_path
        # get the updated patient class
        pat = pickle.load(open(os.path.join(file_path, 'Patients-Info', self.id), 'rb'))

        # get the baseline files
        baseline_files = [file for file in os.listdir(os.path.join(file_path, self.id)) if (file not in pat.seizures.keys() and file.endswith('.edf') and 'Empatica' in file)]
        
        #get the modalities present in the baseline files
        baseline_mod = set([base.split(' - ')[-1] for base in baseline_files])

        # run each date to join all corresponding modalities in a single dataframe
        for modality in baseline_mod:
            #create a new dataframe for each modality
            df = pd.DataFrame()
            #get the dates associated with the modality
            baseline_dates  = set([base.split(' - ')[1] for base in baseline_files if modality in base])
            for date in sorted(baseline_dates):
                name = [file for file in baseline_files if modality in file and date in file][0]
                # open the corresponding edf file
                edf = pyedf.EdfReader(os.path.join(file_path, self.id, name))

                # concatenate the new dataframe with df
                df = pd.concat((df, utils.edf_to_df(edf, modality)))

            # dump the final dataframe into a pickle
            pickle.dump(df, open(os.path.join(saving_directory, self.id, 'baseline_data_'+modality[:-4]),'wb'))


    def get_seizures_data(self, saving_directory = None, file_path = 'MLB-Seer', preseizure=None, postseizure=None):

        if saving_directory is None:
            saving_directory = file_path
        # get the updated patient class
        pat = pickle.load(open(os.path.join(file_path, 'Patients-Info', self.id), 'rb'))
        final_dict = {}
        # get the seizure files
        for seizure in list(pat.seizures.keys()):
            final_dict[seizure] = {} 
            seizure_files = pat.seizures[seizure]
            # get each modality
            for name in seizure_files:
                edf = pyedf.EdfReader(os.path.join(file_path, self.id, name))
                modality = name.split(' - ')[-1][:-4]

                df = utils.edf_to_df_seizure(edf, modality, seizure_files[name])
                final_dict[seizure][modality] = df

        pickle.dump(final_dict, open(os.path.join(saving_directory, self.id, 'seizures_data'),'wb'))






