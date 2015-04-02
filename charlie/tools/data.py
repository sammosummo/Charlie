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
QUESTIONNAIRE_DATA_PATH = pj(DATA_PATH, 'questionnaire_data')
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
QUESTIONNAIRE_TEMPLATES_PATH = pj(PACKAGE_DIR, 'questionnaire_templates')
QUESTIONNAIRES_PATH = pj(PACKAGE_DIR, 'questionnaire_lists')


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
        STIM_PATH, VISUAL_PATH, AUDIO_PATH, DB_PATH, INSPECTION_DATA_PATH,
        QUESTIONNAIRE_DATA_PATH
    ]
    [os.makedirs(p) for p in to_create if not os.path.exists(p)]


def create_db():
    """
    Initialises the local database, if it does not already exist.
    """
    if not os.path.exists(LOCAL_DB_F):
        con = sqlite3.connect(LOCAL_DB_F)

        cols = [
            'proband_id', 'user_id', 'proj_id', 'sex', 'age', 'tests_compl'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('probands', con, index=False)

        cols = [
            'proband_id', 'user_id', 'proj_id', 'test_name', 'date_note_added',
            'note', 'include_data'
        ]
        df = pandas.DataFrame(columns=cols)
        df.to_sql('notes', con, index=False)
        con.close()


def populate_demographics():
    """
    Populates the 'probands' table in the local database based on information
    contained within the other tables. This is useful because running the test
    battery from the command line will not update the probands table by itself.
    Also returns the data frame.
    """
    create_paths()
    create_db()
    print '---Populating the probands sql table'
    con = sqlite3.connect(LOCAL_DB_F)
    try:
        df = pandas.read_sql('SELECT * from probands', con)
    except:
        cols = [
            'proband_id', 'user_id', 'proj_id', 'sex', 'age', 'tests_compl'
        ]
        df = pandas.DataFrame(columns=cols)
    df1 = pandas.read_sql(
        "SELECT * FROM sqlite_master WHERE type='table'", con
    )
    tables = df1['name'].tolist()
    if 'probands' in tables:
        tables.remove('probands')
    if 'notes' in tables:
        tables.remove('notes')
    tables = [t for t in tables if '_trials' not in t]
    _probands = {}
    for test_name in sorted(tables):
        try:
            df2 = pandas.read_sql('SELECT * from %s' % test_name, con)
            df2 = df2[['proband_id', 'user_id', 'proj_id']]
            df = pandas.concat([df, df2])
            _probands[test_name] = df2.proband_id.tolist()
        except KeyError:
            continue
    df.drop_duplicates(subset=['proband_id'], inplace=True)
    df.set_index('proband_id', drop=False, inplace=True)
    for i, row in df.iterrows():
        x = ''
        for test_name in _probands:
            if row.proband_id in _probands[test_name]:
                x += '%s ' % test_name
        df.ix[i, 'tests_compl'] = x
    df.replace('', np.nan, inplace=True)
    df.to_sql('probands', con, index=False, if_exists='replace')
    con.close()
    return df


def replace_demographics(df):
    """
    Repalces the contents of the 'probands' table in the local database with
    the contents of the data frame.
    """
    print '---Replacing contents of probands sql table'
    con = sqlite3.connect(LOCAL_DB_F)
    df.replace('', np.nan, inplace=True)
    df.to_sql('probands', con, index=False, if_exists='replace')
    con.close()


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
        calculated and added to the local db.
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
            print '---Here are the summary stats:'
            print df2.T
            df2.to_sql(self.test_name, con, index=False, if_exists='append')
            self.to_log('summary stats added to localdb')
        con.close()


if __name__ == '__main__':
    pass
