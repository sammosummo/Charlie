#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 09:13:47 2015

@author: smathias
"""

import glob
from datetime import datetime
import cPickle
import os
from os.path import dirname as pd
from os.path import join as pj
#from os import listdir as ld
import sqlite3
import numpy as np
import pandas
import pandas.io.sql as sql


PACKAGE_DIR = os.path.abspath(pd(pd(__file__)))
DATA_PATH = pj(PACKAGE_DIR, 'data')
LOG_PATH = pj(PACKAGE_DIR, 'logs')
RAW_DATA_PATH = pj(DATA_PATH, 'raw')
BACKUP_DATA_PATH = pj(DATA_PATH, 'backups')
INSPECTION_DATA_PATH = pj(DATA_PATH, 'inspections')
CSV_DATA_PATH = pj(DATA_PATH, 'csv')
LOCAL_DB_F = pj(DATA_PATH, 'db', 'localdb.sqlite')
STIM_PATH = pj(PACKAGE_DIR, 'stimuli')
VISUAL_PATH = pj(STIM_PATH, 'visual')
AUDIO_PATH = pj(STIM_PATH, 'audio')
DB_PATH = pj(DATA_PATH, 'db')
INSTRUCTIONS_PATH = pj(PACKAGE_DIR, 'instructions')
FONTS_PATH = pj(PACKAGE_DIR, 'fonts')
TESTS_PATH = pj(PACKAGE_DIR, 'tests')
BATCHES_PATH = pj(PACKAGE_DIR, 'batch_lists')


def ld(path):
    """
    Wrapper around os.listdir(path), but excludes hidden files on unix-based
    systems.
    """
    return [l for l in os.listdir(path) if l[0] != '.']


def create_paths():
    """
    The directory structure should exist within the package, but if not, it is
    created by this function. This is useful because sometimes it is convenient
    to delete all the data files before debugging.
    """
    to_create = [
        DATA_PATH, LOG_PATH, RAW_DATA_PATH, BACKUP_DATA_PATH, CSV_DATA_PATH,
        STIM_PATH, VISUAL_PATH, AUDIO_PATH, DB_PATH, INSPECTION_DATA_PATH
    ]
    [os.makedirs(p) for p in to_create if not os.path.exists(p)]


def create_db():
    """
    Initialises the local database, if it does not already exist. Also adds
    blank probands and notes tables.
    """
    if not os.path.exists(LOCAL_DB_F):
        con = sqlite3.connect(LOCAL_DB_F)

        cols = [
            'proband_id', 'user_id', 'proj_id', 'sex', 'age', 'tests_compl'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('probands', con)

        cols = [
            'proband_id', 'user_id', 'proj_id', 'test_name', 'date_note_added',
            'note', 'include_data'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('notes', con)


def get_tests_with_summary_data():
    """
    Returns a list of tests with summary data stored within the db.
    """
    con = sqlite3.connect(LOCAL_DB_F)
    try:
        df1 = pandas.read_sql('SELECT * from probands', con, index_col='index')
    except pandas.io.sql.DatabaseError:
        cols = [
            'proband_id', 'user_id', 'proj_id', 'sex', 'age'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('probands', con)
        cols = [
            'proband_id', 'user_id', 'proj_id', 'test_name', 'date_note_added',
            'note', 'include_data'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('notes', con)
        df1 = pandas.read_sql('SELECT * from probands', con, index_col='index')

    df2 = pandas.read_sql("SELECT * FROM sqlite_master WHERE type='table'",
                          con)
    tests = df2['name'].tolist()
    if 'probands' in tests:
        tests.remove('probands')
    if 'notes' in tests:
        tests.remove('notes')
    return [t for t in tests if '_trials' not in t]


def populate_probands_table():
    """
    From the data within the db, generates a new DataFrame for the probands
    table, then merges the new df with the old one, and overwrites the old
    probands table. This is just to keep track of any probands that have not
    been added via the GUI.
    """
    con = sqlite3.connect(LOCAL_DB_F)
    tests = get_tests_with_summary_data()

    df = pandas.read_sql('SELECT * from probands', con)
    proband_list = df.proband_id.tolist()

    for test_name in tests:

        try:
            df1 = pandas.read_sql('SELECT * from %s' % test_name, con)
            df1 = df1[['proband_id', 'user_id', 'proj_id']]
            df1 = df1.loc[~(df1.proband_id.isin(proband_list))]
        except KeyError:
            continue  # trials doesn't work; see issues

        df = pandas.concat([df, df1])
        proband_list = df.proband_id.tolist()

    print df
    df.to_sql('probands', con, index=False, if_exists='replace')


def get_probands_table():
    """
    Read the contents of the local database and returns the probands and notes
    tables as pandas DataFrames.
    :return: df1
    """
    create_paths()
    create_db()
    con = sqlite3.connect(LOCAL_DB_F)
    df1 = pandas.read_sql('SELECT * from probands', con)
    return df1


def get_probands_users_projects():
    """
    Returns lists of unique probands, users, and projects from probands table
    in the database.
    :param df1:
    :return: probands, users, projects
    """
    df1 = get_probands_table()
    probands = df1.proband_id.unique().tolist()
    users = df1.user_id.unique().tolist()
    projects = df1.proj_id.unique().tolist()
    return probands, users, projects


def load_data(proband_id, lang, user_id, proj_id, test_name, output_format,
              create_if_not_found=True):
    """
    Returns the pickled instance of a data class corresponding to the specific
    proband and test, if it exists. By default, a new instance is returned if
    an existing one is not found.
    """
    create_paths()
    create_db()

    data_obj = Data(proband_id,
                    lang,
                    user_id,
                    proj_id,
                    test_name,
                    output_format)

    if os.path.exists(data_obj.abs_filename):

        old_data_obj = cPickle.load(open(data_obj.abs_filename, 'rb'))
        old_data_obj.last_opened = datetime.now()
        return old_data_obj

    else:

        if create_if_not_found:
            return data_obj


def save_data(data_obj):
    """
    Saves the raw data to the path specified within the data instance. If
    data_obj.proband_id is 'TEST', this function does nothing.
    """
    create_paths()
    create_db()
    if not os.path.exists(data_obj.directory):
        os.makedirs(data_obj.directory)
    if data_obj.proband_id != 'TEST':
        cPickle.dump(data_obj, open(data_obj.abs_filename, 'wb'))


# TODO: This currently doesn't work!
def delete_data(data_obj):
    """
    Deletes the data instance if found.
    """
    if os.path.exists(data_obj.abs_filename):
        os.remove(data_obj.abs_filename)
        
    data_obj.directory = pj(BACKUP_DATA_PATH, str(datetime.now()).split('.')[0])
    data_obj.abs_filename = pj(data_obj.directory, data_obj.filename)
    save_data(data_obj)
    
    


class Data:

    """
    This class contains attributes and methods necessary for recording a
    proband's progress in a given test. There must be one such instance per
    proband and per test, pickled within the RAW_DATA_PATH. If proband_id is
    'TEST', the instance is never pickled.
    """

    def __init__(self, proband_id, lang, user_id, proj_id, test_name,
                 output_format):
        """
        Initialise the instance.
        """
        self.proband_id = proband_id
        self.lang = lang
        self.user_id = user_id
        self.proj_id = proj_id
        self.test_name = test_name
        self.output_format = output_format
        self.directory = RAW_DATA_PATH
        self.filename = '%s_%s.data' % (proband_id, test_name)
        self.abs_filename = os.path.join(self.directory, self.filename)
        self.control = None
        self.data = None
        self.test_started = False
        self.date_started = None
        self.test_done = False
        self.date_done = None
        self.initialised = datetime.now()
        self.last_opened = datetime.now()
        self.last_udated = datetime.now()
        self.log = []
        self.to_log('instance created')

    def update(self):
        """
        Saves the Data instance in its current state. Assumes the test was
        actually started before this method was called.
        """
        self.last_updated = datetime.now()
        if not self.test_started:
            self.test_started = True
            self.date_started = datetime.now()
        save_data(self)
        self.to_log('instance updated')
        if self.test_done:
            self.date_done = datetime.now()

    def to_df(self):
        """
        Converts the raw data (currently stored in a list of tuples) to a
        pandas DataFrame.
        """
        names, dtypes = zip(*self.output_format)
        df = pandas.DataFrame(np.array(self.data).T, names).transpose()
        for name, dtype in self.output_format:
            df[name] = df[name].astype(dtype)
        self.to_log('pandas DataFrame of data created')
        return df

    def to_csv(self, f=None):
        """
        Exports the data to csv format. Requires an entry for this task in
        the DATA_FORMATS csv. If no argument is given, the data are put in
        the default folder.
        """
        df = self.to_df()
        if not f:
            f = self.filename.split('.')[0] + '.csv'
            f = pj(CSV_DATA_PATH, f)
        if not os.path.exists(CSV_DATA_PATH):
            os.makedirs(CSV_DATA_PATH)
        if self.proband_id != 'TEST':
            df.to_csv(f, index=False)
        self.to_log('data saved as csv to %s' % f)

    def to_log(self, s):
        """
        Adds the string s to the log.
        """
        entry = (str(datetime.now()), s)
        self.log.append(entry)

    def log2pandas(self):
        """
        Returns the log in a pandas DataFrame.
        """
        names = ('date', 'message')
        return pandas.DataFrame(np.array(self.log).T, names).transpose()


    def to_localdb(self, summary_method=None, instructions=None):
        """
        Sends data to the local sqlite database. If a 'summary_method'
        function is supplied, the summary statistics for the test are
        calculated and adde to the local db.
        """
        self.update()
        con = sqlite3.connect(LOCAL_DB_F)

        df1 = self.to_df()
        test_name = self.test_name + '_trials'
        if self.proband_id != 'TEST':
            df1.to_sql(test_name, con, index=False, if_exists='append')
        self.to_log('trial-by-trial data added to localdb')

        if summary_method is not None and self.proband_id != 'TEST':
            df2 = summary_method(self, instructions)
            df2.to_sql(self.test_name, con, index=False, if_exists='append')
            self.to_log('summary stats added to localdb')


if __name__ == '__main__':
    pass
