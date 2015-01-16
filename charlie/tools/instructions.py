#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 17:42:52 2014

@author: smathias
"""


from os.path import join as pj
from charlie.tools.data import INSTRUCTIONS_PATH

def read_instructions(*args):
    """
    Returns written instructions for a given test and language, if they are
    present in the battery.
    """
    txt = open(pj(INSTRUCTIONS_PATH, '%s_%s.txt' % args), 'rb').read()
    return [s.strip('\n') for s in txt.split('---')]


if __name__ == '__main__':
    pass