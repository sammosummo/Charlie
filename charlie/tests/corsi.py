"""
corsi: Corsi test.

This is a computerised and slightly modified version of the classic test of
spatial-memory span by Corsi [1]. On each trial, the subject sees 9 empty
squares ('blocks'). These blocks illuminate in a sequence that the proband
reproduces by clicking on the squares. Blocks are illuminated for 0.5 s each.
In the first trial, only two blocks illuminate during the study period, and the
number of illuminating blocks increases by one every three trials. If the
proband makes two errors with the same number of illuminating blocks, the test
is terminated early.

Previous works suggest that the order in which subjects recall the sequence
(forwards or in reverse) does not have much of an effect on performance [2, 3],
so only the forwards version is included here.

Time taken:

Version history:


"""
__version__ = 1.0
__author__ = 'smathias'


from itertools import repeat
import pandas
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
import charlie.tools.audio as audio


test_name = 'corsi'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('phase', str),
                 ('trialn', str),
                 ('positions', str),
                 ('n', int),
                 ('order', int),
                 ('rsp', str),
                 ('ncorr', str),
                 ('rt', int)]

ns = [2, 3, 4] + sorted(range(2, 10) * 3)
positions = [
    [(256, 69), (190, -358), (-345, -352), (-31, -99), (-193, 30), (-272, 183),
     (289, 228), (334, 35), (356, -194)],
    [(149, -57), (-235, 125), (-140, -11), (-70, 65), (238, 23), (-153, -347),
     (-248, 179), (-64, -239), (235, 200)],
    [(-316, -231), (195, 211), (197, -291), (-150, -12), (-51, 241),
     (315, -271), (-246, -107), (267, -178), (-226, -162)],
    [(-62, -269), (68, 61), (-246, -14), (-209, 321), (-165, -299), (295, 321),
     (102, 12), (-123, 7), (-327, 327)],
    [(-302, -157), (261, 162), (-287, 7), (-333, 328), (271, 208), (-79, 311),
     (-201, -87), (217, -11), (-13, 15)],
    [(270, -103), (118, -126), (-142, 146), (-332, 286), (-205, 325),
     (-327, -66), (130, 30), (-152, -3), (268, 199)],
    [(-267, -234), (52, 331), (-251, -185), (240, 13), (-304, 200),
     (-288, -91), (-39, 203), (-100, 222), (351, -253)],
    [(-127, -119), (146, 228), (127, -109), (152, -4), (221, 196), (197, 141),
     (-80, -22), (338, -174), (189, -172)],
    [(-115, 273), (170, 118), (-307, 356), (59, 7), (142, 30), (-20, -5),
     (225, -230), (-185, 344), (-154, 157)],
    [(231, 291), (-220, 201), (127, 143), (-98, -145), (301, 37),
     (-96, 189), (-252, 11), (1, -321), (190, -117)],
    [(-284, -261), (26, -40), (-118, -82), (147, -187), (107, 161), (-76, 84),
     (105, -97), (292, 198), (-196, 115)],
    [(170, -160), (-245, -164), (317, -220), (9, -161), (-323, 215), (76, 208),
     (123, -281), (223, -270), (341, -297)],
    [(-302, 39), (358, 32), (-212, 229), (-341, -343), (-98, -74), (-14, -271),
     (-131, 107), (53, 60), (-356, 158)],
    [(73, 222), (159, -262), (255, 290), (352, -287), (-216, -165), (-99, -8),
     (264, 34), (-143, 23), (-15, -191)],
    [(-192, -68), (316, 175), (-148, -354), (-131, -297), (50, 151),
     (-130, 83), (287, -245), (-330, 165), (92, 174)],
    [(140, -156), (-131, -33), (140, 87), (-146, 200), (122, -316),
     (-338, 159), (-299, 14), (312, -115), (330, 164)],
    [(-157, 243), (167, 311), (-250, -61), (-108, -287), (122, 301),
     (-324, -355), (299, 204), (-357, -299), (-163, -101)],
    [(-154, 196), (91, 336), (168, -294), (-193, -144), (-336, 355),
     (300, -283), (-149, -150), (142, -109), (-26, -185)],
    [(-182, 291), (-269, -224), (297, 264), (353, 43), (-129, -300),
     (276, -92), (-60, 99), (94, 195), (-192, -91)],
    [(88, 325), (273, -260), (-89, 152), (334, -7), (119, -357),
     (-101, 197), (267, 111), (359, -219), (199, -146)],
    [(-248, -314), (355, -43), (94, 33), (47, -268), (92, 98), (244, -21),
     (-28, -177), (111, 283), (-100, -185)],
    [(188, -134), (247, -235), (-349, 18), (302, -210), (-138, 99),
     (-305, -269), (258, 162), (331, -49), (-176, -251)],
    [(-350, 114), (-275, -92), (249, 148), (-191, -304), (239, -264),
     (65, -302), (110, -69), (345, -30), (-313, 162)],
    [(102, -87), (-350, 350), (302, -137), (-172, 75), (15, -289), (-340, 73),
     (45, -129), (-59, -163), (244, 89)],
    [(148, -195), (253, 82), (135, -67), (256, 10), (-294, 270), (80, 230),
     (164, 285), (-92, 137), (189, 111)],
    [(52, -120), (-135, 334), (-307, 43), (57, -172), (-305, 84), (-133, 82),
     (-23, 180), (120, -1), (316, -73)],
    [(74, 276), (-215, -177), (-266, 76), (-221, -60), (-43, -265),
     (-324, -206), (87, -268), (175, 342), (-254, -283)]
]
orders = [str(range(n)).strip('[]').replace(', ', '') for n in ns]

""" STIMULUS GENERATION: DO NOT UNCOMMENT -------------------------------------

import numpy as np
from pygame import Rect

def make_configuration():
    ok = False
    while not ok:
        ok = True
        rects = []
        for i in xrange(9):
            a, b = np.random.randint(-360, 360, 2)
            rect = Rect(a, b, 40, 40)
            if rect.collidelist(rects) != -1:
                ok = False
            rects.append(rect)
    return [(r.left, r.top) for r in rects]

positions = [ make_configuration() for n in ns]

----------------------------------------------------------------------------"""


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, this is a list of tuples in
    the format (proband_id, test_name, phase, trialn, pos0 ... pos8, n, order).
    """
    control = []
    for x in zip(xrange(len(ns)), ns, positions, orders):
        trialn, n, pos, order = x
        if x[0] > 2:
            trialn -= 3
            phase = 'test'
        else:
            phase = 'practice'
        y = (proband_id, test_name, phase, trialn, positions, n, order)
        control.append(y)
    return control

print control_method(None, None)