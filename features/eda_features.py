# third-party
import numpy as np
from biosppy import eda

# local
from features import eda, statistic_features, temporal_features


from biosppy import utils
from biosppy.signals import tools as st

def eda_features(signal=None, sampling_rate=1000.):
    """Compute EDA characteristic metrics describing the signal.

    Parameters
    ----------
    signal : array
        Input signal.
    sampling_rate : float
        Sampling frequency.
    Returns
    -------
    onsets : list
        Signal EDR events onsets.

    pks : list
        Signal EDR events peaks.

    amps : list
        Signal EDR events Amplitudes.

    phasic_rate : list
        Signal EDR events rate in 60s.

    rise_ts : list
        Rise times, i.e. onset-peak time difference.

    half_rise : list
        Half Rise times, i.e. time between onset and 50% amplitude.

    half_rec : list
        Half Recovery times, i.e. time between peak and 63% amplitude.

    six_rise : list
        63 % rise times, i.e. time between onset and 63% amplitude.

    six_rec : list
        63 % recovery times, i.e. time between peak and 50% amplitude.

    """
    # ensure numpy
    signal = np.array(signal)
    args, names = [], []

    # get EDR signal
    try:
        scr = eda.get_scr(signal, sampling_rate)
    except:
        scr = []

    # onsets, pks, amps
    onsets, pks, amps = eda.get_eda_param(signal)

    # phasic_rate
    phasic_rate = sampling_rate * (60. / np.diff(pks))
    
    rise_ts = (np.array(pks - onsets))/sampling_rate

    # half, six, half_rise, half_rec, six_rec
    if pks != [] and onsets != []:
        half_rec, six_rec = eda.edr_times(signal, onsets, pks)
    else:
        # print('This window is too short to get onsets')
        half_rise, half_rec, six_rise, six_rec = [], [], [], []

    # names = ['onsets', 'pks', 'phasic_rate', 'rise_ts', 'half_rise', 'half_rec', 'six_rise', 'six_rec']

    count_pks = len(pks)
    count_onsets = len(onsets)
    phasic_stats = statistic_features.signal_stats(phasic_rate)
    amps_stats = statistic_features.signal_stats(amps)
    
    count_half = len(half_rec)
    
    #return np.array(onsets), np.array(pks), np.array(phasic_rate), np.array(rise_ts), np.array(half_rise), np.array(six_rise)

    return np.hstack((count_onsets, count_pks, count_half, phasic_stats, amps_stats))