#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 10:18:27 2015

@author: smathias
"""

from platform import system
from getpass import getuser
from socket import gethostname
import numpy as np
from scipy.stats import norm


def sdt_yesno(N, S, H, F):
    """
    Calculates d', c, k and beta using maximum likelihood for th equal-variance
    Gaussian SDT model.
    """
    if N < 10 or S < 10:
        print '---SDT warning: This does not look right:', (N, S, H, F)
    if F == 0 or F == N:
        F += 0.5
        N += 1
        print '---SDT warning: correction applied'
    if H == S or H == 0:
        H += 0.5
        S += 1
        print '---SDT warning: correction applied'
    d = norm.ppf(H / float(S)) - norm.ppf(F / float(N))
    c = -0.5 * (norm.ppf(H / float(S)) + norm.ppf(F / float(N)))
    k = - norm.ppf(F / float(N))
    beta = np.exp(d * c)
    return d, c


def rau(x, n):
    """
    Performs the rationalised arcsine transform on count x and total
    observations n.
    """
    t = np.arcsin(np.sqrt(float(x) / float(n + 1))) +\
        np.arcsin(np.sqrt(float(x + 1) / float(n + 1)))
    return (46.47324337 * t - 23) / 100.


def k_cowan(nitems, N, S, H, F):
    """
    Calculates working-memory capacity according to Cowan's formula.
    """
    h = H / float(S)
    f = F / float(N)
    return nitems * (h - f)


def get_universal_entries(data_obj):
    """
    Generates a set of values that will always be the first columns in every
    summary data frame.

    Parameters
    ----------

    data_obj : instance of the charlie.tools.data.Data class

    Returns
    -------

    cols : column names

    entries : column values

    """
    test_name = data_obj.test_name
    proband_id = data_obj.proband_id
    initialised = data_obj.initialised
    date_done = data_obj.date_done
    user_id = data_obj.user_id
    proj_id = data_obj.proj_id
    lang = data_obj.lang

    cols = ['test_name', 'proband_id', 'date_started', 'date_completed',
            'time_taken', 'computer_os', 'computer_name', 'computer_user',
            'user_id', 'proj_id', 'lang']
    entries = [test_name, proband_id, str(initialised)[:19],
               str(date_done)[:19], str(date_done - initialised), system(),
               gethostname(), getuser(), user_id, proj_id, lang]

    return cols, entries


def get_rt(df, prefix=''):
    """
    Generates response-time statistics: the mean RT, the mean RT with all
    values >= 3 standard deviations removed, number of outliers removed.

    Parameters
    ----------

    df : pandas DataFrame containing a column called 'rt'

    prefix : a str to prefix the variable names

    Returns
    -------

    cols : column names

    entries : column values

    """
    x = df.rt
    a = x.mean()
    y = x[np.abs(x - a) <= (3 * x.std())]
    b = y.mean()
    c = len(x)-len(y)
    cols = ['rt_mean', 'rt_mean_outrmvd', 'n_outrmvd']
    if prefix:
        cols = ['%s_%s' % (prefix, col) for col in cols]
    entries = [a, b, c]
    return cols, entries


def get_accuracy(df, prefix='', ans_col='ans'):
    """
    Generates accuracy statistics: number of trials, number of correct trials,
    proportion of correct trials, rau-transformed proportion correct.

    Parameters
    ----------

    df : pandas DataFrame containing a column called 'rt'

    prefix : a str to prefix the variable names

    ans_col : (optional) name of the DataFrame column containing the answers;
        default is 'ans'

    Returns
    -------

    cols : column names

    entries : column values

    """
    ntrials = len(df)
    corrects = df[df[ans_col] == df.rsp]
    ncorrect = len(corrects)
    if ntrials == 0:
        pcorrect = None
        r = None
    else:
        pcorrect = ncorrect / float(ntrials)
        r = rau(ncorrect, ntrials)
    cols = ['ntrials', 'ncorrect', 'pcorrect', 'rau(pcorrect)']
    if prefix:
        cols = ['%s_%s' % (prefix, col) for col in cols]
    entries = [ntrials, ncorrect, pcorrect, r]
    return cols, entries


# TODO: add more SDT statistics here!
def get_recognition_memory(df, prefix='', choices=('Yes', 'No'),
                           ans_col='ans'):
    """
    Generates recognition-memory statistics. This can be used for any test
    that uses the basic yes-no paradigm from signal detection theory. Returns
    d' and c. The first element in 'choices' is always considered the 'signal'
    and the second is always considered the 'noise'.
    """
    df.ans = df[ans_col]
    yes, no = choices

    N = len(df[df.ans == no])
    S = len(df[df.ans == yes])
    H = len(df[(df.ans == yes) & (df.rsp == yes)])
    F = len(df[(df.ans == no) & (df.rsp == yes)])

    cols = ['d', 'c']
    entries = list(sdt_yesno(N, S, H, F))

    if prefix:
        cols = ['%s_%s' % (prefix, col) for col in cols]

    return cols, entries


def get_2alt(df, prefix='', choices=('Yes', 'No'), ans_col='ans'):
    """
    Convenience function around get_recognition_memory(), get_accuracy() and
    get_rt(); suitable for any test that uses the basic yes-no paradigm.
    """
    print '--doing this.'
    df.ans = df[ans_col]
    yes, no = choices
    a, b = get_accuracy(df, prefix, ans_col)
    c, d = get_rt(df[df.ans == df.rsp], prefix)
    f, g = get_recognition_memory(df, prefix, choices, ans_col)
    return a + c + f, b + d + g


def get_gonogo(df, prefix='', choices=('Yes', 'No'), ans_col='ans'):
    """
    Convenience function around get_recognition_memory(), get_accuracy() and
    get_rt(); suitable for any test that uses the go-no-go paradigm.
    """
    df.ans = df[ans_col]
    yes, no = choices
    a, b = get_accuracy(df, prefix, ans_col)
    c, d = get_rt(df[(df.ans == yes) & (df.rsp == yes)], prefix)
    f, g = get_recognition_memory(df, prefix, choices, ans_col)
    return a + c + f, b + d + g


def get_all_combinations_2alt(df, condition_set, choices=('Yes', 'No'),
                              ans_col='ans'):
    """
    Generates all possible combinations of the conditions and generates
    summary stats for all of them. Suitable for any test that uses the basic
    yes-no paradigm.
    """
    print '--Getting all combinations.'
    all_conditions = cartesian([c[1] for c in condition_set])
    condition_names = [c[0] for c in condition_set]
    cols, entries = [], []

    for conditions in all_conditions:
        print '--Getting all values.'
        df2 = df.copy(True)
        for name, val in zip(condition_names, conditions):
            if val != 'all':
                try:
                    df2 = df2[df2[name] == val]
                except TypeError:
                    df2 = df2[df2[name] == int(val)]

        prefix = '_'.join(str(c).lower() for c in conditions)
        a, b = get_2alt(df2, prefix, choices, ans_col)
        cols += a
        entries += b

    return cols, entries


def get_all_combinations_malt(df, condition_set, choices=('Yes', 'No'),
                              ans_col='ans'):
    """
    Generates all possible combinations of the conditions and generates
    summary stats for all of them.
    """
    all_conditions = cartesian([c[1] for c in condition_set])
    condition_names = [c[0] for c in condition_set]
    cols, entries = [], []

    for conditions in all_conditions:

        df2 = df.copy(True)
        for name, val in zip(condition_names, conditions):
            if val != 'all':
                df2 = df2[df2[name] == val]

        prefix = '_'.join(str(c).lower() for c in conditions)
        a, b = get_accuracy(df2, prefix, ans_col)
        c, d = get_rt(df2[df2[ans_col] == df2.rsp], prefix)
        cols = cols + a + c
        entries = entries + b + d

    return cols, entries


def differences(dfsum, lvl0, lvl1, dvs):
    """
    Calculates differences between the two levels of the given IV.
    """
    cols, entries = [], []
    for dv in dvs:

        x = '%s_%s' % (lvl0, dv)
        y = '%s_%s' % (lvl1, dv)
        cols.append('%s_minus_%s' %(x, y))
        entries.append(float(dfsum[x].ix[0]) - float(dfsum[y].ix[0]))

    return cols, entries


def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out


def get_generic_summary(df):
    """
    Computes generic summary statistics when nothing special needs to be
    reported. These are number of triaks, number of correct trials, and mean
    response time. Detects the 'phase' column in the DataFrame and summarises
    only 'test' trials if found.
    """
    if 'phase' in df.columns:
        df = df[df.phase == 'test']
    a, b = get_accuracy(df)
    c, d = get_rt(df[df.ans == df.rsp])
    cols = a + c
    entries = b + d
    return cols, entries

