# built-in
import json
import os

# third-party
import numpy as np

# local
from biosppy import utils
from biosppy import bvp
from biosppy import tools as st


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
    dict = json.load(open(os.path.join(os.path.abspath('.'), 'features', 'bvp_features_log.json')))
    args, names = [], []

    if dict['ons']['use'] == 'yes':
        # onsets
        try:
            ons = bvp.find_onsets(signal, sampling_rate)['onsets']
        except:
            ons = None
        args += [ons]
        names += ['onsets']

    if dict['hr']['use'] == 'yes':
        # heart rate
        try:
            _, hr = st.get_heart_rate(beats=ons, sampling_rate=sampling_rate, smooth=True, size=3)
        except:
            hr = None
        args += [hr]
        names += ['hr']

    return utils.ReturnTuple(tuple(args), tuple(names))
