

#external packages
import datetime as datetime
import numpy as np
import os
from numpy.testing import assert_array_almost_equal
import pandas as pd
import pyedflib as pyedf


#database

import pickle



# get_baseline_data

patient_id = 'MSEL_01550'
file_path = 'MLB-Seer'

pat = pickle.load(open(os.path.join(file_path, 'Patients-Info', patient_id), 'rb'))

#pat.get_seizures_data(saving_directory=None, file_path = file_path)

seizures = pickle.load(open(os.path.join(file_path, patient_id, 'seizures_data'), 'rb'))

import matplotlib.pyplot as plt

for seizure in seizures.keys():
    plt.plot(seizures[seizure]['Empatica-ACC'])
plt.show()