# built-in
import json
import os

# third-party
import numpy as np

# local
from biosppy import utils
from biosppy import ppg
from biosppy import tools as st

from . import statistic_features, hrv_features


def bvp_features(signal=None, sampling_rate=1000.):
    """ Compute BVP characteristic metrics describing the signal.

    Parameters
    ----------
    signal : array
        Input signal.
    sampling_rate : float
        Sampling frequency.
    Returns
    -------
    ons : list
        Signal onsets.

    hr: list
        Bvp heart rate.
    """

    # ensure numpy array
    signal = np.array(signal)

    args, names = [], []

    ons = ppg.find_onsets_elgendi2013(signal, sampling_rate)['onsets']
    _, hr = st.get_heart_rate(beats=ons, sampling_rate=sampling_rate, smooth=True, size=3)   

    hr_stats = statistic_features.signal_stats(hr)
    hr_ppg_ft = hrv_features.hrv_features(np.diff(ons))

    return utils.ReturnTuple(tuple(args), tuple(names))
