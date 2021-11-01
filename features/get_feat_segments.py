# built-in
import time

# third-party
import numpy as np
import pandas as pd
#import pandas_profiling
from sklearn.model_selection import cross_val_score

# local
from features import eda, bvp_features, eda_features, hrv_features, spectral_features, statistic_features, temporal_features
from biosppy import signals


def signal_features(signal, sig_lab, sampling_rate):

    stats_names = ['mean', 'median', 'var', 'std', 'abs_dev', 'kurtosis', 'skewness', 'iqr', 'rms']
    feats_names = []
    feats = np.array([])
    
    if 'EDA' in sig_lab.upper():
        eda_auxs, eda_names = eda_features.eda_features(signal, sampling_rate)
        for a, aux in enumerate(eda_auxs):
            feats_names += [sig_lab + '_'+ eda_names[a] + '_' + feat for feat in stats_names]
            feats = np.hstack((feats, statistic_features.signal_stats(aux)))
        return feats, feats_names

    elif 'BVP' in sig_lab.upper():
        return bvp_features.bvp_features(signal, sampling_rate)
    elif 'HR' in sig_lab.upper():
        return hrv_features.hrv_features(signal, sampling_rate)
    else:
        return None

def get_feat(signal, sig_lab, sampling_rate=1000., feat_type = ['stat'], windows_len=5, segment=True, save=False):

    print('here')
    feats = np.array([])
    feats_names = []

    if 'stat' in feat_type:
        stats_names = ['mean', 'median', 'var', 'std', 'abs_dev', 'kurtosis', 'skewness', 'iqr', 'rms']
        feats_names += [sig_lab + '_' + feat for feat in stats_names]
        feats = np.hstack((feats, statistic_features.signal_stats(signal)))
        assert(len(feats_names) == len(feats))

    if 'temp' in feat_type:
        temp_names = ['maxAmp', 'minAmp', 'max', 'min', 'dist', 'autocorr', 'zero_cross', 'meanadiff', 'medadiff', 'mindiff', 'maxdiff', 'sadiff', 'meandiff', 'meddiff', 'total_energy', 'minpeaks', 'maxpeaks', 'temp_dev']

        feats_names += [sig_lab + '_' + feat for feat in temp_names]
        feats = np.hstack((feats, temporal_features.signal_temp(signal, sampling_rate)))
        assert(len(feats_names) == len(feats))

    if 'signal' in feat_type:
        sig_feats, sig_names = signal_features(signal, sig_lab, sampling_rate)
        assert(len(sig_feats) == len(sig_names))
        feats_names += sig_names
        feats = np.hstack((feats, sig_feats))

    return feats



def get_feat_(signal, sig_lab, sampling_rate=1000., windows_len=5, segment=True, save=False):
    """ Returns a feature vector describing the signal.

    Parameters
    ----------
    signal : array
        Input signal.

    sig_lab : string
        Signal label.

    sampling_rate : float
        Sampling frequency.

    windows_len : int
        Windows size in seconds.

    segment : bool
        True: the data is segmented into windows of size windows_len seconds; False: No segmentation.

    save : bool
        If True a the feature vector is stored in a .csv file.

    Returns
    -------
    df : dataframe
        Feature vetor in dataframe format, each column is a feature.

    signal : array
        Segmented data.
    """
    labels_name, segdata, feat_val, row_feat = [], [], None, np.array([])
    sig_lab += '_'
    window_size = int(windows_len*sampling_rate)
    if segment:
        signal = [signal[i:i + window_size] for i in range(0, len(signal), window_size)]
        if len(signal) > 1:
            signal = signal[:-1]
    print("<START Feature Extraction>")
    t0 = time.time()
    for wind_idx, wind_sig in enumerate(signal):
        # Statistical Features
        _values, _names = statistic_features.signal_stats(wind_sig)
        labels_name += [str(sig_lab + i) for i in _names]
        row_feat = np.hstack((row_feat, _values))
        # Temporal Features
        _values, _names = temporal_features.signal_temp(wind_sig, sampling_rate)
        labels_name += [str(sig_lab + i) for i in _names]
        row_feat = np.hstack((row_feat, _values))
        # Spectral Features
        _values, _names = spectral_features.signal_spectral(wind_sig, sampling_rate)
        labels_name += [str(sig_lab + i) for i in _names]
        row_feat = np.hstack((row_feat, _values))

        # Sensor Specific Features
        if 'EDA' in sig_lab:
            scr = eda.get_scr(wind_sig, sampling_rate)
            # Statistical Features
            _values, _names = statistic_features.signal_stats(scr)
            labels_name += [str(sig_lab + '_EDR_' + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))
            # Temporal Features
            _values, _names = temporal_features.signal_temp(scr, sampling_rate)
            labels_name += [str(sig_lab + '_EDR_' + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))
            # Spectral Features
            _values, _names = spectral_features.signal_spectral(scr, sampling_rate)
            labels_name += [str(sig_lab + '_EDR_' + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))

            # Features on EDR Spectrum
            f, spectrum = signals.tools.power_spectrum(scr, sampling_rate=sampling_rate)
            # Statistical Features
            _values, _names = statistic_features.signal_stats(spectrum)
            labels_name += [str(sig_lab + '_on_spectrum_' + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))
            # Temporal Features
            _values, _names = temporal_features.signal_temp(spectrum, sampling_rate)
            labels_name += [str(sig_lab + '_on_spectrum_' + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))

            # On SCR Signal
            eda_f = eda_features.eda_features(wind_sig, sampling_rate)
            for item in eda_names:
                _values, _names = statistic_features.signal_stats(eda_f[item], hist=False)
                labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                row_feat = np.hstack((row_feat, _values))

                _values, _names = temporal_features.signal_temp(eda_f[item], sampling_rate)
                labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                row_feat = np.hstack((row_feat, _values))

            # Non-liner and geometric features
            onsets = eda.get_eda_param(wind_sig, sampling_rate)[0]
            _values, _names = nonlinear_geo_features.nonlinear_geo_features(onsets, wind_sig)
            labels_name += [str(sig_lab + i) for i in _names]
            row_feat = np.hstack((row_feat, _values))
            
        elif 'BVP' in sig_lab:
            if wind_sig is not []:
                bvp_f = bvp_features.bvp_features(wind_sig, sampling_rate)
                for item in bvp_names:
                    _values, _names = statistic_features.signal_stats(bvp_f[item], hist=False)
                    labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                    row_feat = np.hstack((row_feat, _values))

                    _values, _names = temporal_features.signal_temp(bvp_f[item], sampling_rate)
                    labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                    row_feat = np.hstack((row_feat, _values))
                ons = signals.bvp.find_onsets(wind_sig, sampling_rate)['onsets']
                _values, _names = nonlinear_geo_features.nonlinear_geo_features(ons, wind_sig)
                labels_name += [str(sig_lab + i) for i in _names]
                row_feat = np.hstack((row_feat, _values))

        if 'Resp' in sig_lab:
            if wind_sig is not []:
                resp_f = resp_features.resp_features(wind_sig, sampling_rate)
                for item in resp_names:
                    _values, _names = statistic_features.signal_stats(resp_f[item], hist=False)
                    labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                    row_feat = np.hstack((row_feat, _values))

                    _values, _names = temporal_features.signal_temp(resp_f[item], sampling_rate)
                    labels_name += [str(sig_lab + item + '_' + i) for i in _names]
                    row_feat = np.hstack((row_feat, _values))

                zeros, = signals.tools.zero_cross(signal=signal, detrend=True)
                _values, _names = nonlinear_geo_features.nonlinear_geo_features(zeros, signal)
                labels_name += [str(sig_lab + i) for i in _names]
                row_feat = np.hstack((row_feat, _values))

        if not wind_idx:
            segdata = wind_sig
            feat_val = np.nan_to_num(row_feat).reshape(1, -1)
        else:
            segdata = np.vstack((segdata, wind_sig))
            feat_val = np.vstack((feat_val, np.nan_to_num(row_feat).reshape(1, -1)))
    
    print("<END Feature Extraction>")
    print('Time: ', time.time()-t0, ' seconds')
    d = {str(lab): feat_val[:, idx] for idx, lab in enumerate(labels_name)}
    df = pd.DataFrame(data=d, columns=labels_name, dtype='float')
    
    df = df.replace([np.NaN, None], 0.0) ##########

    if save:
        df.to_csv('Features.csv', sep=',', encoding='utf-8', index_label="Sample")
    return df, segdata


def remove_correlatedFeatures(df, threshold=0.85):
    """ Removes highly correlated features.
    Parameters
    ----------
    df : dataframe
        Feature vector.
    threshold : float
        Threshold for correlation.

    Returns
    -------
    df : dataframe
        Feature dataframe without high correlated features.

    """
    df = df.replace([np.inf, -np.inf, np.nan, None], 0.0)
    profile = pandas_profiling.ProfileReport(df)
    reject = profile.get_rejected_variables(threshold=threshold)
    for rej in reject:
        print('Removing ' + str(rej))
        df = df.drop(rej, axis=1)

    return df


def FSE(X_train, y_train, features_descrition, classifier, CV=10):
    """ Performs a sequential forward feature selection.
    Parameters
    ----------
    X_train : array
        Training set feature-vector.

    y_train : array
        Training set class-labels groundtruth.

    features_descrition : array
        Features labels.

    classifier : object
        Classifier.

    Returns
    -------
    FS_idx : array
        Selected set of best features indexes.

    FS_lab : array
        Label of the selected best set of features.

    FS_X_train : array
        Transformed feature-vector with the best feature set.

    References
    ----------
    TSFEL library: https://github.com/fraunhoferportugal/tsfel
    """
    total_acc, FS_lab, acc_list, FS_idx = [], [], [], []
    X_train = np.array(X_train)

    print("*** Feature selection started ***")
    for feat_idx, feat_name in enumerate(features_descrition):
        acc_list.append(np.mean(cross_val_score(classifier, X_train[:, feat_idx].reshape(-1,1), y_train, cv=CV)))

    curr_acc_idx = np.argmax(acc_list)
    FS_lab.append(features_descrition[curr_acc_idx])
    last_acc = acc_list[curr_acc_idx]
    FS_X_train = X_train[:, curr_acc_idx]
    total_acc.append(last_acc)
    FS_idx.append(curr_acc_idx)
    while 1:
        acc_list = []
        for feat_idx, feat_name in enumerate(features_descrition):
            if feat_name not in FS_lab:
                curr_train = np.column_stack((FS_X_train, X_train[:, feat_idx]))
                acc_list.append(np.mean(cross_val_score(classifier, curr_train, y_train, cv=CV)*100))
            else:
                acc_list.append(0)
        curr_acc_idx = np.argmax(acc_list)
        if last_acc < acc_list[curr_acc_idx]:
            FS_lab.append(features_descrition[curr_acc_idx])
            last_acc = acc_list[curr_acc_idx]
            total_acc.append(last_acc)
            FS_idx.append(curr_acc_idx)
            FS_X_train = np.column_stack((FS_X_train, X_train[:, curr_acc_idx]))
        else:
            print("FINAL Features: " + str(FS_lab))
            print("Number of selected features", len(FS_lab))
            print("Features idx: ", FS_idx)
            print("Acc: ", str(total_acc))
            print("From ", str(X_train.shape[1]), " features to ", str(len(FS_lab)))
            break
    print("*** Feature selection finished ***")

    return np.array(FS_idx), np.array(FS_lab), FS_X_train


