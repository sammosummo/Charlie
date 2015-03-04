"""
Inspect the data collected from all the tests. The purpose of this script is to
check the following things:

1. That the trial-by-trial data are being recorded and the stats are being
computed.

2. That subjects are performing the tasks in a timely manner.

3. That the data being collected look sensible.
"""
__author__ = 'smathias'

import datetime
import os
import sqlite3
import pandas
import numpy
import matplotlib.pyplot as plt
import charlie.tools.data as data
import charlie.tools.plots as plots


def load_localdb(table_names=None):
    """
    Return the data from the local db.
    :param table_names: Individual table names. All are returned by default.
    :return: A dict where each key represents a table and each entry is a
    pandas.DataFrame object.
    """
    con = sqlite3.connect(data.LOCAL_DB_F)
    if table_names is None:
        s = "SELECT * FROM sqlite_master WHERE type='table'"
        df = pandas.read_sql(s, con)
        table_names = df.tbl_name.tolist()
    stuff = {}
    for table in table_names:
        s = 'SELECT * from %s' % table
        df = pandas.read_sql(s, con)
        stuff[table] = df
    return stuff


def load_summaries(tests=None):
    """
    Return the data from the summary tables as pandas.DataFrame objects.
    :param tests: Individual test names.
    :return: A dict where each key represents a table and each entry is a
    pandas.DataFrame object.
    """
    if tests is None:
        stuff = load_localdb()
        tables = set(stuff.keys())
        excl = [t for t in tables if '_trials' in t]
        excl += ['probands', 'projects', 'users']
        excl = set(excl)
        wanted = tables.difference(excl)
        stuff = {k: stuff[k] for k in wanted}
    else:
        stuff = load_localdb(tests)
    return stuff


def create_master_summary_df():
    """
    Create a master pandas.DataFrame object that contains all of the summary
    stats from all of the tests.
    """
    stuff = load_summaries()
    exclude_these = ['test_name']

    for test_name, df in stuff.iteritems():

        df.drop(exclude_these, axis=1, inplace=True)
        df.set_index('proband_id', inplace=True)
        new_col = lambda s: '%s.%s' % (test_name, s)
        new_cols = [new_col(s) for s in df.columns]
        df.columns = new_cols
        stuff[test_name] = df

    #TODO: trails is broken!!!!
    stuff.pop('trails', 0)

    df = pandas.concat(stuff.values(), axis=1)
    return df


def inspect_times():
    """
    Inspects the times taken to complete each task. Creates a summary figure
    and a report.
    :return:
    """
    path = os.path.join(data.INSPECTION_DATA_PATH, 'times')
    if not os.path.exists(path):
        os.makedirs(path)
    stuff = load_summaries()
    dfs = {}
    for test_name, df in stuff.iteritems():
        if 'time_taken' not in df.columns:
            print 'WARNING: %s has not time_taken column' % test_name
            continue
        df.set_index('proband_id', inplace=True)
        if 'sam' in df.index:
            df.drop('sam', inplace=True)
        if 'sam4' in df.index:
            df.drop('sam4', inplace=True)
        t = df.time_taken.apply(lambda s: '0' + s)
        t = pandas.to_timedelta(t)
        dfs[test_name] = t
    df = pandas.DataFrame(dfs)
    descr = df.describe().T
    descr.to_csv(os.path.join(path, 'times.csv'))







#
# def inspect_performance():
#     """
#     Generates a number of outputs to check performance in the tests.
#     :return:
#     """
#     dfs = {}
#     stuff = load_summaries()
#     test_names = stuff.keys()
#     stuff = load_localdb()
#
#     path = os.path.join(data.INSPECTION_DATA_PATH, 'performance')
#     if not os.path.exists(path):
#         os.makedirs(path)
#
#     for test_name in test_names:
#         path2 = os.path.join(path, test_name)
#         if not os.path.exists(path2):
#             os.makedirs(path2)
#         df1 = stuff[test_name]
#         df2 = stuff[test_name + '_trials']
#
#         if 'ncorrect' in df1.columns:
#
#             dfs[test_name + '_ncorrect'] = df1.ncorrect
#
#         if test_name == 'wtar':
#             words = df2.word.unique()
#             Ncorr = []
#             for word in words:
#                 df3 = df2[df2.word == word]
#                 n, ncorr = len(df3), len(df3[df3.rsp == 'True'])
#                 Ncorr.append(ncorr)
#             plots.bar_chart(
#                 words, Ncorr, 'Word', 'No. correct',
#                 'Item effects on the WTAR'
#             )
#             f = os.path.join(path2, 'item_effects.png')
#             plt.savefig(f)








if __name__ == '__main__':
    df = create_master_summary_df()
    df.to_csv(os.path.join(data.CSV_DATA_PATH, 'master.csv'))
