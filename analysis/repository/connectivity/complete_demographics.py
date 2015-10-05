"""
Based on the data in the repository, complete the demographics csv.
"""

__author__ = 'smathias'


import os
from os import listdir as ld
from os.path import dirname as pd
from os.path import join as pj
from os.path import splitext as st
from itertools import product
import pandas
import numpy as np


REPOSITORY_DIR = os.path.abspath(pd(pd(__file__)))
DEMO_F = pj(REPOSITORY_DIR, 'demographics.csv')
RAW_DIR = pj(REPOSITORY_DIR, 'raw')


def complete_rows():
    """
    Find out if there are any subjects for whom there are data but are not
    currently in the demographics csv.
    """
    proband_ids = set(f.split('_')[0] for f in ld(RAW_DIR)
                       if st(f)[1] == '.data')
    df = pandas.read_csv(DEMO_F, index_col=0)
    df.to_csv(pj(REPOSITORY_DIR, 'demographics_backup.csv'))
    known_ids = set(df.index.astype(str).tolist())
    unknown_ids = proband_ids.difference(known_ids)
    print 'new probands:', unknown_ids
    for unknown_id in unknown_ids:
        print unknown_id
        df.loc[unknown_id] = [np.nan] * df.shape[1]
    df.to_csv(DEMO_F)


if __name__ == '__main__':
    complete_rows()