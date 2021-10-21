import pyedflib as pyedf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pickle
import os

directory = '/Users/preepiseizures/Documents/MLB-Seer/'
patient_id = '01828'

with open(os.path.join(directory, os.path.join('Patients-Info', patient_id)), 'rb') as inp:
    patient = pickle.load(inp)

# choosing BVP for sake of the demonstration 
file = list(patient.seizures.keys())[2]
file_path = os.path.join(os.path.join(directory, patient_id), file)

edf = pyedf.EdfReader(file_path)

channels = edf.getSignalLabels()
print(f'    channels: {channels}')

signal = edf.readSignal(0)
fs = edf.getSampleFrequency(0)
print(f'    sampling frequency: {fs}')

start_time = datetime.timestamp(edf.getStartdatetime())
end_time = start_time + edf.getFileDuration()

edf.close()

ts = np.linspace(start_time, end_time, len(signal))
t = [datetime.fromtimestamp(t) for t in ts]

plt.figure()
plt.plot(t, signal)
plt.vlines(t[patient.seizures[file]['sz_start']], min(signal), max(signal), colors='r')
plt.vlines(t[patient.seizures[file]['sz_end']], min(signal), max(signal), colors='r')
plt.gcf().autofmt_xdate()
plt.show()