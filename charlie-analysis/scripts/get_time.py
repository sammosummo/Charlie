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
        data_obj = cPickle.load(open(os.path.join(DATA_PATH, f), 'rU'))
        print data_obj, data_obj.proband_id, data_obj.time_taken
        objs.append(data_obj)
    return objs

grab_all()