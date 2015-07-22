__author__ = 'smathias'


import cPickle
import importlib
import os
import pandas
import numpy as np
import charlie.tools.instructions as instructions
import matplotlib.pyplot as plt
import seaborn
import dredge_raw as d


objs = d.grab_all()
demographics = pandas.read_csv('demo.csv', index_col=0)
group = demographics.group
dfs = []

for test_name in ['ctrails', 'trails']:

    test_objs = [o for o in objs if o.test_name == test_name]
    _, df_summaries = zip(*[d.apply_summary(o) for o in test_objs])
    df = pandas.concat(df_summaries)
    df.set_index('proband_id', inplace=True)
    df.drop(d.UNWANTED_COLS, axis=1, inplace=True)
    df = df.astype(float)
    df = pandas.concat([df, group], axis=1)
    dfs.append(df)

df1 = dfs[0][['group', 'number_time', 'letter_time', 'number-letter_time']]
df2 = dfs[1][['number_rt', 'letter_rt', 'number-letter_rt']]
df = pandas.concat([df1, df2], axis=1)
df.columns = ['group', 'ctrails_number', 'ctrails_letter', 'ctrails_number-letter', 'trails_number', 'trails_letter', 'trails_number-letter']
df = df.dropna().drop(['group'], axis=1).drop(['4413', '4368'])
df.corr(method='spearman').to_csv('trials_corr.csv')
print df.ctrails_number
seaborn.pairplot(df, kind="reg")
plt.savefig('trails.png')