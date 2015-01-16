#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 10:09:59 2015

@author: smathias
"""

from os.path import join as pj
import pygame.mixer as mixer
from charlie.tools.data import AUDIO_PATH


def play_sound(f):
    """
    Plays the wav file specified by f.
    """
    if mixer.get_init() is None:
        print '---mixer intialised'
        mixer.init()
    
    mixer.Sound(f).play()


def play_feedback(corr):
    """
    Plays audio feedback. corr is a bool where False means incorrect and True
    means correct.
    """
    if mixer.get_init() is None:
        print '---mixer intialised'
        mixer.init()
    
    f = pj(AUDIO_PATH, ['Wrong.wav', 'Correct.wav'][corr])
    sound = mixer.Sound(f)
    sound.play()


def stop():
    """
    Checks if any sounds are playing from the mixer, and if so stops them.
    """
    if mixer.get_busy():
        mixer.stop()


if __name__ == '__main__':
    pass