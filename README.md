# MLB Epilepsy Projects 2021/22
## _Dealing with this hell-born database_

This repository was created to failitate the use of [Seer Medical Epilepsy database][db] (DB) and provides the necessary scripts for:
- Describing the database
- Turning the information into machine-learning-readable format

## How to get the DB information:

- Download the Seer Medical DB with the following structure: a folder containing folders with the patients' IDs, each containing all the patient's files (e.g.: *MSEL_01808*);
- In the script *annot2patient.py*, change the two directories to fit your needs and RUN the script;
- A folder called "Patient-Info" will be created and populated with the DB info for each patient;
- Each patient object hols the information of the corresponding patient from all the patient's files, including: directory with the original patient's files, available modalities and seizure information (i.e.: seizure type, files that contain those seizures and respective indexes).

Note: the script *check_patient_info* can be run after annot2patient and checks if the number of seizures in the DB annotations corresponds to the number of seizures in the patient object created.

## How to get the patients' data into something workable:

- This is still a work in progress
- ✨Magic ✨

## License

MIT

**Powered by [Ana Sofia Carmo][asc] & [Mariana Abreu][ma]**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [db]: <https://app.seermedical.com/au/studies>
   [asc]: <https://github.com/anascacais>
   [ma]: <https://github.com/MarianaAbreu>
