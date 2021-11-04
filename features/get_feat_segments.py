# built-in
import time

# third-party
import numpy as np
import pandas as pd
from biosppy import eda, signals
from sklearn.model_selection import cross_val_score

# local
from . import bvp_features, eda_features, hrv_features, statistic_features, temporal_features


def signal_features(signal, sig_lab, sampling_rate):

    feats = np.array([])
    
    if 'EDA' in sig_lab.upper():
        feats = eda_features.eda_features(signal, sampling_rate)
        return feats

    #elif 'BVP' in sig_lab.upper():
        #dd = bvp_features.bvp_features(signal, sampling_rate)
     #   return feats
    elif 'HR' in sig_lab.upper():
        return hrv_features.hrv_features(signal, sampling_rate)
    else:
        return None

def get_feat_names(sig_lab, feat_type):

    feats_names = []
    stats_names = ['mean', 'median', 'var', 'std', 'abs_dev', 'kurtosis', 'skewness', 'iqr', 'rms']
    if 'stat' in feat_type:
        feats_names += [sig_lab + '_' + feat for feat in stats_names]
    if 'temp' in feat_type:
        temp_names = ['maxAmp', 'minAmp', 'max', 'min', 'dist', 'autocorr', 'zero_cross', 'meanadiff', 'medadiff', 'mindiff', 'maxdiff', 'sadiff', 'meandiff', 'meddiff', 'total_energy', 'minpeaks', 'maxpeaks', 'temp_dev', 'counter']
        feats_names += [sig_lab + '_' + feat for feat in temp_names]
    if 'signal' in feat_type:
        if 'EDA' in sig_lab.upper():
            eda_names = ['phasic', 'amps']
            feats_names += ['count_onsets', 'count_pks', 'count_half_rec']
            feats_names += [sig_lab + '_'+ aux + '_' + feat for aux in eda_names for feat in stats_names]
        if 'HR' in sig_lab.upper():
            feats_names += [sig_lab + '_' + aux for aux in ['rms_sd', 'sd_nn', 'mean_nn', 'nn50', 'var', 'sd1', 'sd2', 'csi', 'csv']]

    return feats_names


def get_feat(signal, sig_lab, sampling_rate=1000., feat_type = ['stat']):

    feats = np.array([])
    if len(signal) < 1:
        print('HA')
 
    if 'stat' in feat_type:
        feats = np.hstack((feats, statistic_features.signal_stats(signal)))

    if 'temp' in feat_type:
        feats = np.hstack((feats, temporal_features.signal_temp(signal, sampling_rate)))

    if 'signal' in feat_type:
        sig_feats = signal_features(signal, sig_lab, sampling_rate)
        if sig_feats is not None:
            feats = np.hstack((feats, sig_feats))

    return feats


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


