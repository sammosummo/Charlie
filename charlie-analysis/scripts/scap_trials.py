"""
Investigate trial-by-trial effects in the SCAP data.
"""

__author__ = 'smathias'


import numpy as np
import matplotlib.pyplot as plt
import pandas
import dredge_raw as dr


data = [dr.apply_summary(obj)[0] for obj in dr.grab_all() if obj.test_name == 'scap']
df = pandas.concat(data)
df = df[df.phase == 'test']
results = [[np.nan], [np.nan], [np.nan]]
for idx, group in df.groupby(['load', 'trialn']):
    load, trialn = idx
    corr = len(group[group.ans == group.rsp])
    results[load - 3].append(corr)
print results

"""
problematic trials:

load   number

3      2
4      11
4      13
"""