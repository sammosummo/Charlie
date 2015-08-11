"""
Dredge the charlie-analysis data directory for raw data files. Compute
summary stats for them.
"""

__author__ = 'Sam'


import cPickle
import importlib
import os
import pandas
import numpy as np
import charlie.tools.instructions as instructions
import charlie.tools.data as data
import matplotlib.pyplot as plt


PACKAGE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(PACKAGE_DIR, 'data')
UNWANTED_COLS = [
    'computer_os', 'computer_name', 'computer_user', 'user_id', 'proj_id',
    'test_name', 'lang', 'date_started', 'date_completed', 'time_taken'
]


def grab_all():
    """
    Returns all the data objects in the data directory.
    """
    files = [f for f in os.listdir(DATA_PATH) if '.data' in f]
    objs = []
    for f in files:
        print f
        data_obj = cPickle.load(open(os.path.join(DATA_PATH, f), 'rU'))
        objs.append(data_obj)
        print data_obj.test_name, data_obj.initialised, data_obj.date_done
    return objs


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


def summary(s, path):
    """
    Make a summary plot of a given series.
    """
    print s.name, path

    try:
        s = s.astype(float)

        if not os.path.exists(path):
            os.makedirs(path)

        demos = pandas.read_csv('demo.csv', index_col=0)
        df = pandas.concat([s, demos.group], axis=1).dropna()

        plt.clf()
        seaborn.violinplot(data=df, x='group', y=s.name, inner=None)
        seaborn.stripplot(data=df, x='group', y=s.name, jitter=True)
        plt.savefig(os.path.join(path, s.name + '.png'))
    except:
        return




if __name__ == '__main__':

    objs = grab_all()
    # tests = set(obj.test_name for obj in objs)
    #
    # demographics = pandas.read_csv('demo.csv', index_col=0)
    # group = demographics.group
    # print group
    #
    # for test_name in tests:
    #
    #     path = os.path.join('summaries', test_name)
    #     if not os.path.exists(path):
    #         os.makedirs(path)
    #
    #     test_objs = [o for o in objs if o.test_name == test_name]
    #     df_trials, df_summaries = zip(*[apply_summary(o) for o in test_objs])
    #
    #     df = pandas.concat(df_summaries)
    #     df.set_index('proband_id', inplace=True)
    #     df.drop(UNWANTED_COLS, axis=1, inplace=True)
    #     df = df.astype(float)
    #     df = pandas.concat([df, group], axis=1)
    #     grouped = df.groupby('group')
    #     f = os.path.join(path, test_name + '_summary_grouped.csv')
    #     grouped.describe().T.to_csv(f)
    #     f = os.path.join(path, test_name + '_summary.csv')
    #     df.to_csv(f)
    #
    #     [summary(s, path)for i, s in df.iteritems()]
    #
    #     df = pandas.concat(df_trials)
    #     f = os.path.join(path, test_name + '_trials.csv')
    #     df.to_csv(f)





#
#
# def rename_proband(data_obj, new_id):
#     """
#     Renames a proband ID and returns a new raw object.
#     """
#     data_obj.proband_id = new_id
#     new_data = []
#     for trial in data_obj.data:
#         new_trial = list(trial)
#         new_trial[0] = new_id
#         new_trial = tuple(new_trial)
#         new_data.append(new_trial)
#     data_obj.data = new_data
#     return data_obj
#
#
# def gather_raw_data():
#     """
#     Recursively extract the raw data files.
#     """
#     known_subjects = [
#         4307,
#         4346,
#         4368,
#         4369,
#         4370,
#         4371,
#         4372,
#         4373,
#         4374,
#         4375,
#         4376,
#         4377,
#         4378,
#         4379,
#         4380,
#         4381,
#         4382,
#         4383,
#         4384,
#         4385,
#         4386,
#         4387,
#         4388,
#         4389,
#         4391,
#         4392,
#         4393,
#         4394,
#         4395,
#         4396,
#         4397,
#         4398
#     ]
#     known_subjects = [str(i) for i in known_subjects]
#     all_data = []
#     files_done = {}
#     for path, dirs, files in os.walk(DATA_PATH):
#         for f in files:
#             name, ext = os.path.splitext(f)
#             if ext == '.data':
#                 fname = pj(path, f)
#                 if f not in files_done:
#                     files_done[f] = fname
#                     data_obj = cPickle.load(open(fname, 'rU'))
#                 else:
#                     if not filecmp.cmp(fname, files_done[f], shallow=False):
#                         data_obj = cPickle.load(open(fname, 'rU'))
#                         if data_obj.proband_id == '4397':
#                             data_obj = rename_proband(data_obj, '4398')
#                 all_data.append(data_obj)
#     return all_data
#
#
# def organise_by_task(all_data):
#     """
#     Returns the data objects organised into dictionaries depending on task.
#     """
#     unwanted_cols = [
#         'computer_os', 'computer_name', 'computer_user', 'user_id', 'proj_id',
#     'test_name', 'lang', 'date_started', 'date_completed', 'time_taken'
#     ]
#     data_dic = {}
#     for data_obj in all_data:
#         if data_obj.test_name in data_dic:
#             data_dic[data_obj.test_name].append(data_obj)
#         else:
#             data_dic[data_obj.test_name] = [data_obj]
#
#     all_summaries = []
#     for test_name, data_objs in data_dic.iteritems():
#         print test_name
#         trials = []
#         summaries = []
#         for data_obj in data_objs:
#             print data_obj.proband_id
#             df1, df2 = apply_summary(data_obj)
#             trials.append(df1)
#             summaries.append(df2)
#         print 'all collected for %s' % test_name
#
#         trials_df = pandas.concat(trials).drop_duplicates()
#         trials_df.to_csv('%s_trials.csv' % test_name)
#
#         summaries_df = pandas.concat(summaries).drop_duplicates()
#         summaries_df.to_csv('%s_summaries.csv' % test_name)
#
#         summaries_df.set_index('proband_id', inplace=True)
#         summaries_df.drop(unwanted_cols, axis=1, inplace=True)
#         summaries_df.columns = ['%s.%s' % (test_name, s) for s in summaries_df.columns]
#         all_summaries.append(summaries_df)
#
#     df = pandas.concat(all_summaries, axis=1)
#     df.to_csv('all_summaries.csv')
#
#
#
# def apply_summary(data_obj):
#     """
#     Apply summary method for a given data object.
#     """
#     names, dtypes = zip(*data_obj.output_format)
#     df1 = pandas.DataFrame(np.array(data_obj.data).T, names).transpose()
#     for name, dtype in data_obj.output_format:
#         df1[name] = df1[name].astype(dtype)
#     mod = importlib.import_module('charlie.tests.' + data_obj.test_name)
#     summary_method = getattr(mod, 'summary_method')
#     instr = instructions.read_instructions(data_obj.test_name, data_obj.lang)
#
#     df2 = summary_method(data_obj, instr)
#
#     return df1, df2
#
#
# data_objs = gather_raw_data()
# organise_by_task(data_objs)
# # [apply_summary(data_obj) for data_obj in data_objs]
#
# # def summarise_data():
# #     """
# #     Create two master data frames.
# #     """
# #     data_objs = gather_raw_data()
# #     trial_dfs = {}
# #     summary_dfs = {}
# #
# #     for data_obj in data_objs:
# #
# #         test_name = data_obj.test_name
# #         a, b = apply_summary(data_obj)
# #         if test_name not in trial_dfs:
# #             trial_dfs[test_name] = [a]
# #         else:
# #             trial_dfs[test_name].append(a)
# #         if test_name not in trial_dfs:
# #             summary_dfs[test_name] = [b]
# #         else:
# #             summary_dfs[test_name].append(b)
# #
# #     trial_df =
#
#
# # import os
# # import sqlite3
# # import zipfile
# # import pandas
# #
# #
#
# #
# #
# # def _unzip_all():
# #     """
# #     Unzips all zip files within the data directory.
# #     """
# #     for dir, subdirs, files in os.walk(DATA_PATH):
# #         for f in files:
# #             if f == '_data.zip':
# #                 path = pj(dir, f)
# #                 with zipfile.ZipFile(path, 'r') as z:
# #                     z.extractall(dir)
# #
# #
# # def _find_files():
# #     """
# #     Within the data directory, returns lists containing paths to all sql, csv,
# #     and raw data files.
# #     """
# #     sql = []
# #     csv = []
# #     raw = []
# #     for dir, subdirs, files in os.walk(DATA_PATH):
# #         for f in files:
# #             path = pj(dir, f)
# #             if f == 'localdb.sqlite':
# #                 sql.append(path)
# #             elif f[-3:] == 'csv':
# #                 csv.append(path)
# #             elif  f[-3:] == 'raw':
# #                 raw.append(path)
# #     return sql, csv, raw
# #
# #
# # def _read_database(filename):
# #     """
# #     Reads the contents of an sql database file and returns the contents in a
# #     dictionary. Table names are saved as keys and tables are saved as pandas
# #     DataFrames.
# #     """
# #     con = sqlite3.connect(filename)
# #     df1 = pandas.read_sql(
# #         "SELECT * FROM sqlite_master WHERE type='table'", con
# #     )
# #     tables = df1['name'].tolist()
# #     dfs = {}
# #     for table in tables:
# #         df = pandas.read_sql('SELECT * from %s' % table, con)
# #         dfs[table] = df
# #     return dfs
# #
# #
# # def _combine_database_data(databases):
# #     """
# #     Makes a single dictionary of database tables out of many.
# #     """
# #     dfs = {}
# #     for database in databases:
# #         for table in database:
# #             if table not in dfs:
# #                 dfs[table] = database[table]
# #             else:
# #                 df = pandas.concat([dfs[table], database[table]])
# #                 dfs[table] = df.drop_duplicates()
# #     return dfs
# #
# #
# # def _get_all_database_data():
# #     """
# #     Grabs all the data from all the database files and returns a dictionary
# #     containing DataFrame objects.
# #     """
# #     sql, csv, raw = _find_files()
# #     databases = [_read_database(f) for f in sql]
# #     return _combine_database_data(databases)
# #
# #
# # def _check_for_missing_summaries(dfs):
# #     """
# #     Returns a list of proband IDs for whom there are entries in the _trials
# #     table
#
# # def read_csvs(files):
# #     """
# #     Makes a dictionary of dataframes containing all the data from all the csvs.
# #     """
# #     dfs = {}
# #     for fname in files:
# #         if 'debug' not in fname:
# #             _, f = os.path.split(fname)
# #             f, _ = os.path.splitext(f)
# #             table = '_'.join(f.split('_')[1:]) + '_trials'
# #             df = pandas.read_csv(fname)
# #             if table not in dfs:
# #                 dfs[table] = df
# #             else:
# #                 _df = pandas.concat([dfs[table], df])
# #                 dfs[table] = _df.drop_duplicates()
# #     return dfs
# #
# #
# # def combine_db_and_csv(db, csv):
# #     """
# #     Make one dictionary of data frames from the csv and db data, excluding
# #     duplicates.
# #     """
# #     dfs = {}
# #     tables = set([t for t in db] + [t for t in csv])
# #     for table in tables:
# #         if table in db:
# #             df1 = db[table]
# #         else:
# #             df1 = None
# #         if table in csv:
# #             df2 = csv[table]
# #         else:
# #             df2 = None
# #         df = pandas.concat([df1, df2]).drop_duplicates()
# #         dfs[table] = df
# #     return dfs
# #
# #
# # if __name__ == '__main__':
# #
# #     sql, csv, raw = find_files()
# #     databases = [read_database(f) for f in sql]
# #     dfs1 = combine_database_data(databases)
# #     # dfs2 = read_csvs(csv)
# #     # dfs = combine_db_and_csv(dfs1, dfs2)
# #     # just_trials = {table: dfs[table] for table in dfs if '_trials' in table}
# #     # print just_trials['switching_trials'].proband_id.unique()