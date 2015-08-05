__author__ = 'smathias'

import os
import numpy as np
import pandas
import matplotlib.pyplot as plt
import seaborn


p = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
f = os.path.join(p, 'data', 'sam_corsi_ext.csv')
df = pandas.read_csv(f)
pcorrect = []
for i, row in df.iterrows():
    if 'forward' in row.condition:
        correct_order = range(row.n)
    elif 'reverse' in row.condition:
        correct_order = [r for r in reversed(range(row.n))]
    elif 'sequence' in row.condition:
        correct_order = [i for i, v in enumerate(row.symbols) if v == 'c'] + \
        [i for i, v in enumerate(row.symbols) if v == 'x']
    else:
        correct_order = None
    keys = {1: 'c', 3: 'x'}
    corcount = 0
    for i, r in enumerate(eval(row.responses)):
        rsp, _, symbol = r
        corr = 0  # assume it's wrong; cuts down the code
        if 'forward' in row.condition or 'reverse' in row.condition or 'sequence' in row.condition:
            if correct_order[i] == rsp:
                corr = 1
        elif row.condition == 'simultaneous_a':
            if rsp in range(row.n):
                corr = 1
        else:
            if rsp in range(row.n):
                corr = 1
                if 'sequence' not in row.condition:
                    corr = 1
        if corr == 1:
            corcount += 1
    pcorrect.append(corcount)
df.pcorrect = pcorrect
group_1 = df.groupby('condition')

for condition, _df in group_1:
    group_2 = _df.groupby('n')
    # ncorrect
    plt.subplot(311)
    x = range(2, 10)
    y = []
    for n, __df in group_2:
        y.append(__df.correct.sum())
    plt.plot(x, y, 'o-', label=condition)
    plt.ylim(-.5, 10.5)
    plt.xlim(1.5, 9.5)
    plt.legend(lc=3)
    plt.ylabel('Total trials correct (out of 10)')
    # pcorrect
    plt.subplot(312)
    x = range(2, 10)
    y = []
    for n, __df in group_2:
        y.append(__df.pcorrect.mean()/float(n))
    plt.plot(x, y, 'o-', label=condition)
    plt.ylim(-0.1, 1.1)
    plt.xlim(1.5, 9.5)
    plt.ylabel('Mean prop. items recalled per trial')
    # rt
    plt.subplot(313)
    x = range(2, 10)
    y = []
    for n, __df in group_2:
        rts = __df[__df.correct == 1]
        y.append(rts.rt.mean()/1000.)
    plt.plot(x, y, 'o-', label=condition)
    # plt.ylim(-0.1, 1.1)
    plt.xlim(1.5, 9.5)
    plt.ylabel('Mean response time (seconds)')
    plt.xlabel('Memory load (n)')
plt.show()
