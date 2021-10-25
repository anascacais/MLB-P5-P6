

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

patient_id = '01828'
file_path = 'MLB-Seer'

pat = pickle.load(open(os.path.join(file_path, 'Patients-Info', patient_id), 'rb'))

pat.get_baseline_data(saving_directory=None, file_path = file_path)

eda = pickle.load(open(os.path.join(file_path, patient_id, 'baseline_data_Empatica-EDA'), 'rb'))

import matplotlib.pyplot as plt

plt.plot(eda)
plt.show()