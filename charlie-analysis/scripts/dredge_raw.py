"""
Dredge the charlie-analysis data directory, removing all duplicates and fixing
known errors (e.g., misnamed probands).
"""

__author__ = 'Sam'


import cPickle
import filecmp
import importlib
import os
from os.path import dirname as pd
from os.path import join as pj
import pandas
import numpy as np
import charlie.tools.instructions as instructions


PACKAGE_DIR = os.path.abspath(pd(pd(__file__)))
DATA_PATH = pj(PACKAGE_DIR, 'data')


def rename_proband(data_obj, new_id):
    """
    Renames a proband ID and returns a new raw object.
    """
    data_obj.proband_id = new_id
    new_data = []
    for trial in data_obj.data:
        new_trial = list(trial)
        new_trial[0] = new_id
        new_data.append(new_data)
    data_obj.data = new_data
    return data_obj


def gather_raw_data():
    """
    Recursively extract the raw data files.
    """
    all_data = []
    files_done = {}
    for path, dirs, files in os.walk(DATA_PATH):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext == '.data':
                fname = pj(path, f)
                if f not in files_done:
                    files_done[f] = fname
                    data_obj = cPickle.load(open(fname, 'rU'))
                else:
                    if not filecmp.cmp(fname, files_done[f], shallow=False):
                        data_obj = cPickle.load(open(fname, 'rU'))
                        if data_obj.proband_id == '4397':
                            data_obj = rename_proband(data_obj, '4398')
                all_data.append(data_obj)
                print data_obj.test_done
    return all_data


def apply_summary(data_obj):
    """
    Apply summary method for a given data object.
    """
    names, dtypes = zip(*data_obj.output_format)
    df1 = pandas.DataFrame(np.array(data_obj.data).T, names).transpose()
    for name, dtype in data_obj.output_format:
        df1[name] = df1[name].astype(dtype)

    mod = importlib.import_module('charlie.tests.' + data_obj.test_name)
    summary_method = getattr(mod, 'summary_method')
    instr = instructions.read_instructions(data_obj.test_name, data_obj.lang)

    df2 = summary_method(data_obj, instr)

    return df1, df2


def summarise_data():
    """
    Create two master data frames.
    """
    data_objs = gather_raw_data()
    trial_dfs = {}
    summary_dfs = {}

    for data_obj in data_objs:

        test_name = data_obj.test_name
        a, b = apply_summary(data_obj)
        if test_name not in trial_dfs:
            trial_dfs[test_name] = [a]
        else:
            trial_dfs[test_name].append(a)
        if test_name not in trial_dfs:
            summary_dfs[test_name] = [b]
        else:
            summary_dfs[test_name].append(b)

    trial_df =


# import os
# import sqlite3
# import zipfile
# import pandas
#
#

#
#
# def _unzip_all():
#     """
#     Unzips all zip files within the data directory.
#     """
#     for dir, subdirs, files in os.walk(DATA_PATH):
#         for f in files:
#             if f == '_data.zip':
#                 path = pj(dir, f)
#                 with zipfile.ZipFile(path, 'r') as z:
#                     z.extractall(dir)
#
#
# def _find_files():
#     """
#     Within the data directory, returns lists containing paths to all sql, csv,
#     and raw data files.
#     """
#     sql = []
#     csv = []
#     raw = []
#     for dir, subdirs, files in os.walk(DATA_PATH):
#         for f in files:
#             path = pj(dir, f)
#             if f == 'localdb.sqlite':
#                 sql.append(path)
#             elif f[-3:] == 'csv':
#                 csv.append(path)
#             elif  f[-3:] == 'raw':
#                 raw.append(path)
#     return sql, csv, raw
#
#
# def _read_database(filename):
#     """
#     Reads the contents of an sql database file and returns the contents in a
#     dictionary. Table names are saved as keys and tables are saved as pandas
#     DataFrames.
#     """
#     con = sqlite3.connect(filename)
#     df1 = pandas.read_sql(
#         "SELECT * FROM sqlite_master WHERE type='table'", con
#     )
#     tables = df1['name'].tolist()
#     dfs = {}
#     for table in tables:
#         df = pandas.read_sql('SELECT * from %s' % table, con)
#         dfs[table] = df
#     return dfs
#
#
# def _combine_database_data(databases):
#     """
#     Makes a single dictionary of database tables out of many.
#     """
#     dfs = {}
#     for database in databases:
#         for table in database:
#             if table not in dfs:
#                 dfs[table] = database[table]
#             else:
#                 df = pandas.concat([dfs[table], database[table]])
#                 dfs[table] = df.drop_duplicates()
#     return dfs
#
#
# def _get_all_database_data():
#     """
#     Grabs all the data from all the database files and returns a dictionary
#     containing DataFrame objects.
#     """
#     sql, csv, raw = _find_files()
#     databases = [_read_database(f) for f in sql]
#     return _combine_database_data(databases)
#
#
# def _check_for_missing_summaries(dfs):
#     """
#     Returns a list of proband IDs for whom there are entries in the _trials
#     table

# def read_csvs(files):
#     """
#     Makes a dictionary of dataframes containing all the data from all the csvs.
#     """
#     dfs = {}
#     for fname in files:
#         if 'debug' not in fname:
#             _, f = os.path.split(fname)
#             f, _ = os.path.splitext(f)
#             table = '_'.join(f.split('_')[1:]) + '_trials'
#             df = pandas.read_csv(fname)
#             if table not in dfs:
#                 dfs[table] = df
#             else:
#                 _df = pandas.concat([dfs[table], df])
#                 dfs[table] = _df.drop_duplicates()
#     return dfs
#
#
# def combine_db_and_csv(db, csv):
#     """
#     Make one dictionary of data frames from the csv and db data, excluding
#     duplicates.
#     """
#     dfs = {}
#     tables = set([t for t in db] + [t for t in csv])
#     for table in tables:
#         if table in db:
#             df1 = db[table]
#         else:
#             df1 = None
#         if table in csv:
#             df2 = csv[table]
#         else:
#             df2 = None
#         df = pandas.concat([df1, df2]).drop_duplicates()
#         dfs[table] = df
#     return dfs
#
#
# if __name__ == '__main__':
#
#     sql, csv, raw = find_files()
#     databases = [read_database(f) for f in sql]
#     dfs1 = combine_database_data(databases)
#     # dfs2 = read_csvs(csv)
#     # dfs = combine_db_and_csv(dfs1, dfs2)
#     # just_trials = {table: dfs[table] for table in dfs if '_trials' in table}
#     # print just_trials['switching_trials'].proband_id.unique()