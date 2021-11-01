
import time
import pandas as pd
import numpy as np

from numba import jit

import math

from scipy.signal import welch

@jit
def pointecare_feats(nn):
    x1 = np.asarray(nn[:-1])
    x2 = np.asarray(nn[1:])

    # SD1 & SD2 Computation
    sd1 = np.std(np.subtract(x1, x2) / np.sqrt(2))
    sd2 = np.std(np.add(x1, x2) / np.sqrt(2))

    csi = sd2/sd1

    csv = math.log10(sd1*sd2)

    return sd1, sd2, csi, csv
    
@jit
def katz_fractal_dim(nn):
    """
    http://tux.uis.edu.co/geofractales/articulosinteres/PDF/waveform.pdf
    :param nn:
    :return:
    """

    d_kfd = np.max([((1-j)**2+(nn[1]-nn[j])**2)**0.5 for j in range(len(nn))])
    l_kfd = np.sum([(1+(nn[i]-nn[i+1])**2)**0.5 for i in range(len(nn)-1)])

    return math.log10(l_kfd)/math.log10(d_kfd)

def diag_det_lmax(rr):
    """
    :param rr:
    :return:
    """
    dim = len(rr)
    assert dim == len(rr[0])
    return_grid = [[] for total in range(2 * len(rr) - 1)]
    for row in range(len(rr)):
        for col in range(len(rr[row])):
            return_grid[row + col].append(rr[col][row])
    diags = [i for i in return_grid if 0.0 not in i and len(i) > 2]
    if len(diags) >= 1:
        diag_points = np.sum(np.hstack(diags))

        long_diag = np.max([len(diag) for diag in diags])
    else:
        diag_points = 0
        long_diag = 0

    return diag_points/(np.sum(rr)), long_diag

def lam_calc(rr):
    dim = len(rr)
    assert dim == len(rr[0])
    return_grid = [[] for total in range(2 * len(rr) - 1)]
    for row in range(len(rr.T)):
        idx_v = np.argwhere(np.diff(rr.T[row]) == -1).reshape(-1)
        print(idx_v)
    aaa

    return lam
@jit
def rqa(nni):
    """
    Recurrent Quantification Analysis
    :param nni:
    :return:
    """

    rr = np.zeros((len(nni), len(nni)))

    for i in range(len(nni)):
        for j in range(len(nni)):
            rr[i,j] = abs(nni[j]-nni[i])
    rr = np.heaviside((rr.mean()-rr), 0.5)

    rec =  rr.sum()/(len(nni)**2)

    det, lmax = diag_det_lmax(rr)


    return rec, det, lmax


@jit
def time_domain(nni, sampling_rate=4):

    nn50 = len(np.argwhere(abs(np.diff(nni))>0.05*sampling_rate))
    pnn50 = nn50 / len(nni)
    sdnn = nni.std()
    rmssd = ((np.diff(nni) ** 2).mean()) ** 0.5

    return rmssd, sdnn, nn50, pnn50

@jit
def spectral(nni, sampling_rate=4):

    frequencies, powers = welch(nni, fs=sampling_rate, scaling='density')
    low_freq_band =  np.argwhere(frequencies< 0.15).reshape(-1)
    high_freq_band =  np.argwhere(frequencies> 0.4).reshape(-1)

    total_pwr = np.sum(powers)

    lf_pwr = np.sum(powers[low_freq_band])/total_pwr
    hf_pwr = np.sum(powers[high_freq_band])/total_pwr

    return lf_pwr, hf_pwr, lf_pwr/hf_pwr


@jit
def get_diff(sig, window):

    diff_sig = sig.diff().abs().diff().abs()

    window_time = pd.date_range(sig.index[0], sig.index[-1], freq=str(window) + 'S')

    new_diff = pd.DataFrame([diff_sig.between_time(window_time[i].time(),
                                                   window_time[i + 1].time()).mean()
                             for i in range(len(window_time) - 1)], index=window_time[1:])

    return new_diff

@jit
def hrv_features(nni, sampling_rate=4, time_=True, pointecare_=True, diff=True):
    """
    names = ['rms_sd', 'sd_nn', 'mean_nn', 'nn50', 'pnn50', 'var', 'sd1',
             'sd2', 'csi', 'csv', 'rec', 'det', 'lmax']
    :param nni:
    :param time_:
    :param spectral_:
    :return:
    """

    if time_:
        # extract rmssd, sdnn, nn50, pnn50, var
        rmssd, sdnn, nn50, pnn50 = time_domain(nni, sampling_rate)
        mean_nn = nni.mean()
        var = nni.var()

    if pointecare_:
        sd1, sd2, csi, csv = pointecare_feats(nni)

    lf_pwr, hf_pwr, lf_hf = spectral(nni)
    kfd = katz_fractal_dim(nni)
    rec, det, lmax = rqa(nni)

    feats = np.hstack((rmssd, sdnn, mean_nn, nn50, pnn50, var, lf_pwr, hf_pwr, lf_hf,
                       sd1, sd2, csi, csv, kfd, rec, det, lmax))
    return feats