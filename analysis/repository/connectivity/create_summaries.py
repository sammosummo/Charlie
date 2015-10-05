"""
Iterate through each data file and create a master trial csv per test and a
master summary csv containing all summary stats.
"""

__author__ = 'smathias'


import cPickle
from os import listdir as ld
from os.path import join as pj, dirname as dn, abspath as ap
from importlib import import_module
import pandas as pd
import numpy as np
from charlie.tools.instructions import read_instructions as ri


repo_dir = ap(dn(__file__))
raw_dir = pj(repo_dir, 'raw')
raw_files = (f for f in ld(raw_dir) if '.data' in f)
dfs = {'trials': {}, 'summaries': {}}

print 'collecting data ...',
for f in raw_files:
    obj = cPickle.load(open(pj(raw_dir, f)))
    t = obj.test_name
    p = obj.proband_id
    if t not in dfs['trials']:
        dfs['trials'][t] = []
        dfs['summaries'][t] = []
    names, dtypes = zip(*obj.output_format)
    df1 = pd.DataFrame(np.array(obj.data).T, names).transpose()
    dfs['trials'][t].append(df1)
    m = import_module('charlie.tests.' + t)
    summary_method = getattr(m, 'summary_method')
    instr = ri(t, obj.lang)
    df2 = summary_method(obj, instr)
    dfs['summaries'][t].append(df2)
print 'done collecting'

print 'making trial csvs'
[pd.concat(_dfs).to_csv(t + '.csv', index=False) for t, _dfs in dfs['trials'].iteritems()]

summary_dfs = []
for t, _dfs in dfs['summaries'].iteritems():
    df = pd.concat(_dfs).set_index('proband_id')
    df.columns = [t + '_' + c for c in df.columns]
    summary_dfs.append(df)
df = pd.concat(summary_dfs, axis=1)
demo = pd.read_csv('demographics.csv')
demo.proband_id.astype(int, inplace=True)
df = pd.concat([demo, df], axis=1)
df.to_csv('summary.csv')


# import cPickle
# import importlib
# import os
# import pandas as pd
# import numpy as np
# import charlie.tools.instructions as instructions
# import charlie.tools.data as data
# import matplotlib.pyplot as plt
#
# from os import listdir as ld
# from os.path import dirname as pd
# from os.path import join as pj
# from os.path import splitext as st
#
#
# REPOSITORY_DIR = os.path.abspath(pd(pd(__file__)))
# DEMO_F = pj(REPOSITORY_DIR, 'demographics.csv')
# RAW_DIR = pj(REPOSITORY_DIR, 'raw')
#
#
# def apply_summary(data_obj):
#     """
#     Apply summary method for a given data object.
#     """
#     names, dtypes = zip(*data_obj.output_format)
#     df1 = pd.DataFrame(np.array(data_obj.data).T, names).transpose()
#     for name, dtype in data_obj.output_format:
#         df1[name] = df1[name].astype(dtype)
#     mod = importlib.import_module('charlie.tests.' + data_obj.test_name)
#     summary_method = getattr(mod, 'summary_method')
#     instr = instructions.read_instructions(data_obj.test_name, data_obj.lang)
#     df2 = summary_method(data_obj, instr)
#     return df1, df2
#
#
# for f in