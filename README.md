 # MLB Epilepsy Projects 2021/22
## _Dealing with this hell-born database_

This repository was created to failitate the use of [Seer Medical Epilepsy database][db] (DB) and provides the necessary scripts for:
- Describing the database
- Turning the information into machine-learning-readable format


## Pipeline:

- Download the Seer Medical DB with the following structure: a folder containing folders with the patients' IDs, each containing all the patient's files (e.g.: *MSEL_01808*);
- When running the script *pipeline.py*, you'll have to provide (1) the directory where the original database is stored, (2) the directory where all data will be stored hereinafter and (3) the modalities for which the data should be extracted.*

*_Note: choosing the modalities will only take effect on the filtering and feature extraction (i.e. the raw data will be extracted for all modalities regardless)._ 

The script "pipeline.py" will perform the following actions in order:
- Extract information from the database (annot2patient.py)
- Extract and concatenate all baseline data for each patient, as well as for seizure data (individually for each modality)
- Filter data according to each modality
- Extract features using a sliding window approach (with overlap), individually for each modality
- ✨Magic ✨



## 1. How to get the DB information (*annot2patient.py*):

- A folder called "patient-info" will be created and populated with the DB info for each patient;
- Each patient object holds the information of the corresponding patient from all the patient's files, including: directory with the original patient's files, available modalities and seizure information (i.e.: seizure type, files that contain those seizures and respective indexes).

Note: the script *check_patient_info* can be run after *annot2patient* and checks if the number of seizures in the DB annotations corresponds to the number of seizures in the patient object created.

## 2. How to get the patients' data into something workable (*get_baseline_seizure_data.py*):

- A folder called "raw-data-df" will be created and populated with a folder for each patient which, in turn, will hold the baseline and seizure dataframes for that patient, one for each modality;
- These dataframes correspond to the concatenated baseline/seizure files for each modality, individually. However, seizure dataframes have an additional column that labels each timestamp with a 0 (if it does not correspond to an annotated seizure) or with a number i (corresponding to the i-th annotated seizure for that patient) - check the notebook in *example* to take a look at these structures.

## 3. Filtering (*filtering.py*)

- A folder called "filtered-data-df" will be created - with the same structure as "raw-data-df", but with the filtered data instead (the data frames have the same structure as well).

## 4. Feature extraction (*feat_extraction.py*)

- A folder called "features" will be created - with the same structure as "raw-data-df";
- This script needs a window size (in seconds) and an overlap (in percentage) to perform feature extraction, individually for each modality, in a sliding window approach;
- During this process, the discontinuities in time are taken into account (so that non-continuous segments are not put inside the same window);
- The resulting dataframe is very similar to the previous ones, but the timestamps in index correspond to the start of the corresponding segment (whose length = *window*) - check the notebook in *example* to take a look at these structures.

## 5. Joining modalities

- In order to join modalities, we need to make sure the timestamps are aligned (so that they correspond to the same interval in time). However, since the timestamps have a resolution up to the nanosecond, many of them are only slightly misaligned - but it would still cause an error of alignment.
- To deal with this, we reduce the resolution to the millisecond, which still allows to preserve the necessary time information, as well as reducing the alignment issues;
- In this script, we provide the modalities whose features we want to join and it joins the corresponding dataframes and removes the time intervals that do not contain at least one of the modalities - check the notebook in *example* to take a look at this process.


## License

MIT

**Powered by [Ana Sofia Carmo][asc] & [Mariana Abreu][ma]**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [db]: <https://app.seermedical.com/au/studies>
   [asc]: <https://github.com/anascacais>
   [ma]: <https://github.com/MarianaAbreu>