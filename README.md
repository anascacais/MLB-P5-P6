# MLB Epilepsy Projects 2021/22
## _Dealing with this hell-born database_

This repository was created to failitate the use of [Seer Medical Epilepsy database][db] (DB) and provides the necessary scripts for:
- Describing the database
- Turning the information into machine-learning-readable format

## 1. How to get the DB information:

- Download the Seer Medical DB with the following structure: a folder containing folders with the patients' IDs, each containing all the patient's files (e.g.: *MSEL_01808*);
- In the script *annot2patient.py*, change the two directories to fit your needs and RUN the script;
- A folder called "patient-info" will be created and populated with the DB info for each patient;
- Each patient object holds the information of the corresponding patient from all the patient's files, including: directory with the original patient's files, available modalities and seizure information (i.e.: seizure type, files that contain those seizures and respective indexes).

Note: the script *check_patient_info* can be run after annot2patient and checks if the number of seizures in the DB annotations corresponds to the number of seizures in the patient object created.

## 2. How to get the patients' data into something workable:

- In the script *get_baseline_seizure_data.py*, change the three directories and RUN the script;
- A folder called "raw-data-df" will be created and populated with a folder for each patient which, in turn, will hold the baseline and seizure dataframes for that patient;
- These dataframes correspond to the concatenated baseline/seizure files for each modality, individually. However, seizure dataframes have an additional column that labels each timestamp with a 0 (if it does not correspond to an annotated seizure) or with a number i (corresponding to the i-th annotated seizure for that patient)(check the notebook in *example* to take a look at these structures).
- ✨Magic ✨

## License

MIT

**Powered by [Ana Sofia Carmo][asc] & [Mariana Abreu][ma]**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [db]: <https://app.seermedical.com/au/studies>
   [asc]: <https://github.com/anascacais>
   [ma]: <https://github.com/MarianaAbreu>
