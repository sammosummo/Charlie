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
import charlie.tools.visual as visual
import charlie.tools.events as events


test_name = 'corsi'
output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trial_type', str),
                 ('phase', str),
                 ('trialn', str),
                 ('positions', str),
                 ('nsymbols', int),
                 ('symbols', str),
                 ('correct', int),
                 ('rt', int),
                 ('responses', str)]
trial_types = ['forward', 'reverse', 'sequence']
phases = ['practice', 'test']
nsymbols = {
    'forward': {
        'practice': [2, 3, 4],
        'test': [x for x in xrange(2, 10) for i in xrange(3)]
    },
    'reverse': {
        'practice': [2, 3, 4],
        'test': [x for x in xrange(2, 10) for i in xrange(3)]
    },
    'sequence': {
        'practice': [2, 2, 3, 3],
        'test': [x for x in xrange(2, 10) for i in xrange(3)]
    },
}
symbols = {
    'practice': ['cx', 'xc', 'cxc', 'xxc'],
    'test': [
        'xc',        'xc',        'cx',
        'xcc',       'xcx',       'cxc',
        'xcxc',      'cxcx',      'xxcc',
        'ccxxc',     'cxcxx',     'xxccc',
        'ccxxxc',    'xxcxcc',    'cxcxcx',
        'xxcxccc',   'cxxxccx',   'xcxxccc',
        'cxxcxccx',  'cccxxxxc',  'cxxcxcxc',
        'ccccxxxcx', 'cxxxxxccc', 'xxxcxcccc'
    ]
}
positions = {
    'forward': {
        'test': [
            [(-82, -27), (103, 219), (-32, 113), (61, -86), (-290, -119), (-225, 211), (268, -239), (-90, -177), (92, 84)],
            [(213, -268), (-259, -197), (140, -11), (-203, 271), (-98, 225), (-147, -34), (-264, -88), (-222, 86), (168, 151)],
            [(-277, -69), (286, 118), (277, -130), (162, 115), (66, 297), (153, -124), (-46, 231), (-107, -2), (-150, -205)],
            [(68, 45), (-191, -41), (270, 183), (186, -219), (-295, 222), (224, -2), (169, -110), (-271, -260), (-294, 66)],
            [(-153, -79), (2, 218), (-268, -43), (-12, -40), (214, 115), (-187, -247), (223, -19), (58, 81), (-111, 133)],
            [(129, -77), (82, 56), (-58, -159), (-178, 56), (-70, -32), (177, -234), (272, 151), (65, 224), (-255, -46)],
            [(164, -273), (-88, 194), (-210, -89), (180, -170), (222, 148), (-193, 151), (126, -42), (-31, -197), (-219, -239)],
            [(201, 159), (-278, 14), (30, -230), (66, -34), (281, -275), (-200, -131), (252, 34), (-220, -278), (-81, -88)],
            [(-110, 150), (286, 190), (-26, -291), (-68, 9), (-83, 292), (-265, -30), (112, 215), (-298, 296), (137, -298)],
            [(-216, 240), (295, -82), (-78, 163), (-118, -235), (106, 123), (272, 183), (-105, 37), (14, -246), (-12, -73)],
            [(124, 85), (297, 24), (197, -79), (-194, 120), (49, -29), (126, 214), (114, -247), (-31, -223), (-190, -113)],
            [(231, 133), (-35, -272), (-130, 260), (47, 200), (-295, 173), (-147, -135), (142, -219), (168, -111), (-34, -157)],
            [(-93, 263), (232, 184), (-17, -157), (-143, -18), (-286, -43), (216, -40), (-169, 118), (-224, -168), (197, -173)],
            [(-46, -140), (132, -118), (54, -264), (-176, 80), (-130, -279), (220, 263), (-53, 6), (-228, 248), (112, 205)],
            [(-257, 250), (146, -300), (297, 110), (132, 126), (290, 223), (81, 3), (292, -60), (-140, -90), (-131, -255)],
            [(-161, 280), (62, -33), (-18, 248), (-270, 116), (274, -112), (146, 156), (-7, -257), (141, -171), (24, -147)],
            [(75, 7), (-33, -9), (-12, 127), (-78, 243), (-224, 209), (282, -237), (-269, -148), (-18, -253), (-127, -295)],
            [(64, 140), (71, 291), (-248, -173), (241, -258), (-26, -298), (37, -55), (-264, -41), (-36, 96), (163, -19)],
            [(-262, 295), (10, 295), (85, -172), (163, 28), (59, 188), (-247, -143), (-137, -296), (-269, 154), (227, -255)],
            [(200, 265), (224, 83), (198, -106), (-226, 270), (62, -76), (-253, 69), (-208, -106), (-189, -262), (-34, 174)],
            [(-8, -256), (-120, 278), (-61, -63), (-212, -109), (59, 291), (214, 121), (116, -222), (28, 59), (-171, 46)],
            [(296, -164), (-111, -89), (73, -32), (206, -274), (234, 31), (-10, 249), (-143, 217), (24, -269), (-156, 78)],
            [(59, 219), (63, 65), (-147, -37), (-134, 81), (-34, -262), (-204, 286), (-166, -300), (-12, -162), (250, -162)],
            [(180, 155), (-87, -138), (58, 149), (93, -139), (-251, -222), (135, -265), (-205, -57), (-130, -259), (-283, 45)],
            [(-277, 215), (112, -79), (-92, 194), (122, -224), (-136, -119), (293, 94), (-107, 18), (0, -201), (-4, -37)],
            [(-127, 294), (-133, -86), (97, 173), (203, -271), (177, -131), (26, -33), (-290, -58), (212, 292), (-136, -203)],
            [(140, 161), (-90, 283), (150, -6), (-155, -64), (24, 125), (-91, 161), (272, 123), (235, 298), (-170, -277)]
        ],
        'practice': [
            [(-21, 193), (-296, -119), (232, -75), (244, 208), (66, -273), (-268, 117), (140, 106), (230, -213), (-152, -20)],
            [(11, -16), (-165, -6), (104, 252), (242, 201), (-207, 274), (77, 97), (32, -277), (-294, 23), (263, -125)],
            [(-182, -54), (-191, -187), (-20, -35), (-138, -294), (93, 32), (234, -21), (244, -156), (191, 220), (138, -123)]
        ]},
    'reverse': {
        'test': [
            [(-143, 130), (-288, 220), (-265, -4), (208, -296), (-165, 8), (277, -86), (267, 176), (-298, -201), (62, -5)],
            [(134, -95), (91, 293), (-155, 178), (19, 139), (172, -247), (-285, -205), (295, 174), (-240, 29), (-277, 189)],
            [(-279, -6), (-5, 165), (251, 90), (299, -239), (71, 21), (146, -114), (162, -222), (270, -53), (-24, -126)],
            [(-135, -151), (143, 260), (92, 53), (254, 56), (2, -88), (-291, -277), (-271, -50), (242, -242), (-283, 151)],
            [(-261, -240), (-222, 238), (116, -265), (-240, -81), (23, 175), (-107, -228), (271, -76), (217, -191), (-84, -125)],
            [(-121, -1), (99, -267), (88, -145), (-168, -265), (72, 21), (-21, -178), (229, -285), (232, 181), (-210, 209)],
            [(-71, 192), (45, -76), (-298, 143), (255, 298), (-15, 24), (-103, -184), (125, 161), (-251, -191), (153, -33)],
            [(-149, -147), (-114, 100), (78, -263), (31, 177), (-50, -8), (114, -142), (-71, 219), (258, 295), (-260, 282)],
            [(-84, 291), (292, -294), (90, 116), (-141, -200), (118, 232), (24, -200), (-255, -52), (-185, 70), (-269, -245)],
            [(156, -190), (217, -85), (139, 218), (-200, 86), (-31, -93), (-279, 270), (-22, 200), (-165, 193), (-67, 41)],
            [(271, 156), (128, 142), (232, 6), (-206, -121), (267, 282), (-279, 9), (-142, 279), (-76, -300), (-13, 66)],
            [(-119, 73), (35, 258), (89, -221), (-95, 286), (144, -63), (253, 225), (141, 294), (57, 88), (-289, -102)],
            [(105, 274), (-262, 266), (296, 8), (-100, 158), (123, 112), (-38, -85), (-59, 23), (-217, -101), (167, -224)],
            [(-49, -17), (-97, -220), (206, 281), (57, 66), (192, 181), (-260, -114), (17, 248), (-227, 138), (-260, -259)],
            [(-75, 208), (60, -168), (-101, -196), (-19, -53), (293, 83), (167, -276), (219, -153), (209, 194), (-274, 18)],
            [(6, 205), (-144, 83), (250, -45), (-77, -78), (281, -216), (191, 252), (-201, -260), (128, 24), (83, -232)],
            [(186, 19), (-144, -239), (-7, 85), (-24, -156), (-174, 32), (240, -196), (-234, -94), (65, 199), (-189, 176)],
            [(252, 54), (-205, 8), (290, -66), (-187, 132), (140, -15), (-40, 64), (152, -196), (108, 233), (-196, 240)],
            [(36, 113), (-293, 124), (73, -37), (222, -194), (180, -51), (267, -295), (105, -262), (-208, -93), (-63, -23)],
            [(290, -244), (-289, 125), (-67, 175), (-167, -235), (168, -12), (157, -232), (-77, 35), (42, -143), (272, -55)],
            [(163, -245), (-268, 270), (273, 233), (-47, 71), (-278, 2), (-112, -122), (-42, -289), (-281, -119), (-51, 282)],
            [(-106, 198), (269, 188), (139, -158), (-93, -259), (26, -100), (-45, 67), (-234, 56), (-211, 161), (271, -233)],
            [(101, 131), (-162, -182), (-91, -49), (68, -277), (-75, 145), (240, 7), (287, -226), (43, -16), (263, 217)],
            [(-88, 202), (83, -103), (216, 255), (149, -232), (121, 75), (226, -97), (-274, 278), (-65, -215), (67, 279)],
            [(-171, -10), (20, -239), (-26, -54), (283, -13), (154, -249), (-199, -276), (-62, 150), (163, -100), (-237, 108)],
            [(-136, -97), (-264, 250), (35, 208), (-62, -249), (-13, -16), (-82, 276), (244, -213), (-141, 6), (-126, 155)],
            [(-95, 145), (298, -286), (193, -55), (-165, -287), (-248, 36), (-286, -127), (236, 48), (-186, 291), (27, 51)]],
        'practice': [
            [(127, -158), (-286, -152), (-51, -54), (252, 53), (-42, -183), (56, 104), (-48, 63), (-142, -263), (-242, 69)],
            [(-45, -128), (4, 280), (171, 75), (-91, -247), (282, 211), (-213, -189), (207, -288), (-275, 205), (-135, 198)],
            [(150, 155), (-50, 270), (-268, 126), (151, -277), (113, 255), (279, 260), (93, -77), (-8, -145), (-255, 254)]]},
    'sequence': {
        'test': [
            [(120, -258), (-280, 195), (-249, -101), (147, 236), (186, -146), (-138, 218), (-57, -228), (281, 119), (10, -33)],
            [(54, -153), (287, 269), (230, -130), (-241, -129), (216, -242), (69, 287), (-253, 70), (-7, -48), (-129, -130)],
            [(-13, 49), (-258, 232), (-297, 125), (-132, -21), (124, 111), (226, -238), (290, 285), (124, 244), (-122, -206)],
            [(195, 217), (-105, 211), (63, 260), (-258, 151), (-165, -50), (-264, -284), (256, -98), (144, -132), (-274, -17)],
            [(-271, 271), (79, -206), (263, -207), (268, -57), (33, 97), (-71, -88), (-127, 221), (35, 267), (-236, -123)],
            [(-300, -264), (251, -267), (262, -5), (160, 83), (-158, 162), (-136, -202), (-282, -131), (-44, 276), (288, 225)],
            [(-233, 5), (292, -286), (-37, 284), (-110, -160), (-243, 262), (39, 37), (-211, -220), (207, 293), (53, -298)],
            [(60, -87), (291, -164), (179, -63), (-110, -287), (78, 268), (155, 94), (71, -238), (-233, 61), (286, 273)],
            [(67, -191), (221, 190), (-279, 172), (-212, 57), (-78, -53), (95, 260), (-82, -263), (-140, 238), (246, 18)],
            [(-169, -117), (33, 139), (-255, 195), (138, -199), (291, 272), (-70, 257), (-232, 95), (-300, -144), (273, 76)],
            [(183, 194), (-17, -140), (71, -2), (-73, 111), (-122, -292), (-147, -66), (229, 48), (-156, 269), (177, -292)],
            [(-12, -281), (221, 99), (221, -63), (269, -178), (-202, -289), (-63, 155), (-168, -160), (24, 7), (251, 213)],
            [(34, 121), (185, 153), (221, -240), (-213, 284), (231, -127), (-209, 110), (-74, -288), (63, -27), (191, 287)],
            [(117, 69), (-42, 67), (139, 249), (-193, 248), (1, 204), (-44, -36), (-275, -212), (-21, -148), (-259, -21)],
            [(11, -150), (-227, 255), (-79, -6), (245, 49), (204, -62), (113, -183), (-84, -255), (214, -263), (51, 181)],
            [(152, -26), (-72, 266), (-74, 158), (101, 244), (253, -175), (-270, 253), (-4, -161), (-169, -190), (282, 215)],
            [(-241, -96), (244, -134), (-280, 264), (134, 239), (67, -95), (34, 228), (-115, -127), (-75, -1), (146, -276)],
            [(-195, -281), (287, -218), (-249, 65), (-69, -205), (145, -52), (81, -227), (-73, 49), (-3, 155), (-141, -58)],
            [(-214, -293), (69, -266), (101, 231), (-91, -92), (-138, 18), (-221, 286), (125, -154), (237, -155), (160, 114)],
            [(298, 51), (-199, 56), (-52, -252), (-110, 183), (-201, 290), (212, -96), (209, -231), (-150, -144), (42, -126)],
            [(-96, 162), (278, -186), (15, -4), (159, 287), (-286, 203), (159, -257), (130, -80), (-127, 286), (6, 147)],
            [(-199, 272), (125, 30), (-21, -98), (-187, -152), (199, 290), (-2, -261), (-266, 53), (-69, 232), (-18, 80)],
            [(291, -139), (-73, 61), (185, -171), (-151, -149), (155, -6), (-95, 190), (-290, -60), (13, -223), (88, 176)],
            [(-84, 34), (109, 255), (-175, -235), (-273, -25), (249, -294), (94, 132), (6, -80), (-260, 255), (-193, 111)],
            [(-157, -224), (-34, -49), (114, -15), (118, 288), (-274, 174), (-19, -194), (-251, -34), (-285, -268), (-113, 81)],
            [(-30, 233), (-51, -248), (283, 238), (51, -239), (198, 23), (-169, 245), (-128, 18), (-293, -69), (81, 102)],
            [(-144, 267), (-263, -44), (-11, 155), (280, -209), (159, 149), (-80, -10), (86, 30), (-131, -194), (190, -40)]],
        'practice': [
            [(220, -110), (131, 184), (-164, -258), (114, -11), (-282, 61), (17, -249), (-115, -81), (-20, 46), (251, -262)],
            [(-166, -218), (49, -24), (-98, 267), (-274, -282), (-199, -43), (86, -177), (-32, 101), (116, 282), (263, 205)],
            [(163, -21), (132, -258), (-37, -232), (287, -35), (289, 234), (177, 275), (-174, -3), (-185, -277), (-145, 294)],
            [(-216, -20), (278, -67), (-8, 298), (-78, 143), (-258, -122), (-148, -142), (-275, -243), (281, 37), (-3, -67)]
        ]
    }
}
study_duration = 2
wipe_period = 0.5
update_duration = 0.5
timeout = 120

""" STIMULUS GENERATION: DO NOT UNCOMMENT -------------------------------------

import numpy as np
from pygame import Rect

def make_configuration():
    ok = False
    while not ok:
        ok = True
        rects = []
        for i in xrange(9):
            a, b = np.random.randint(-300, 300, 2)
            rect = Rect(a, b, 100, 100)
            if rect.collidelist(rects) != -1:
                ok = False
            rects.append(rect)
    return [(r.left, r.top) for r in rects]

positions = {}
for dic in nsquares:
    positions[dic] = {}
    for ddic in nsquares[dic]:
        positions[dic][ddic] = \
            [make_configuration() for i in xrange(len(nsquares[dic][ddic]))]
print positions

----------------------------------------------------------------------------"""


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, this is a list of tuples in
    the format (proband_id, test_name, trial_type, phase, trialn, positions,
    nsquares).
    """
    control = []
    for trial_type in trial_types:
        for phase in phases:
            ns = nsymbols[trial_type][phase]
            trialns = len(ns)
            poss = positions[trial_type][phase]
            if trial_type == 'sequence':
                symbs = symbols[phase]
            else:
                symbs = ['c' * n for n in ns]
            for trialn in xrange(trialns):
                # print symbs
                trial_info = (
                    proband_id,
                    test_name,
                    trial_type,
                    phase,
                    trialn,
                    repr(poss[trialn]),
                    ns[trialn],
                    symbs[trialn]
                )
                control.append(trial_info)
    for c in control:
        print c
    print '-------'
    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    _, _, trial_type, phase, trialn, pos, n, sym = trial_info

    # figure out what the correct responses should be
    if trial_type == 'foward':
        correct_order = xrange(n)
    elif trial_type == 'reverse':
        correct_order = reversed(xrange(n))
    else:


    # show initial instructions
    if trialn == 0:
        idx = trial_types.index(trial_type)
        if phase == 'practice':
            keydown = screen.splash(instructions[idx * 2], mouse=True)
        else:
            keydown = screen.splash(instructions[idx * 2 + 1], mouse=True)
        if keydown == 'EXIT':
            return 'EXIT'

    # wipe screen
    screen.wipe(force_hide_mouse=True)

    # display squares
    s = 100
    pos = eval(pos)
    squares = [visual.Rect(x + screen.x0, y + screen.y0, s, s) for x, y in pos]
    [screen.blit_rectangle(rect) for rect in squares]
    screen.update()
    events.wait(study_duration)

    # play sequence
    fdic = {
        'c': data.pj(data.VISUAL_PATH, test_name, 'c.png'),
        'x': data.pj(data.VISUAL_PATH, test_name, 'x.png')
    }

    for i in correct_order:
        square = squares[i]
        f = fdic[sym[i]]
        x, y = (square.left + s/5, square.top + s/5)
        _, r = screen.blit_image(f, (x, y), update=False, prc=False)
        screen.update()
        events.wait(update_duration)
        screen.wipe(r, force_hide_mouse=True, update=False, prc=False)
        screen.update()
        events.wait(wipe_period)

    # set up response part of trial
    screen.reset_zones()
    screen.create_rect_zones(squares)
    screen.reset_mouse_pos()
    trial_clock = events.Clock()
    trial_clock.tick_busy_loop()
    responses = []
    i = None

    # wait for a responses
    for i in xrange(n):
        mouse_click = events.wait_for_valid_mouse_click(screen, 1)
        if mouse_click == 'EXIT':
            return 'EXIT'
        j, rt = mouse_click
        print i, j, rt
        responses.append((j, rt))

        # correct response
        if i == j:
            if phase == 'practice':
                screen.blit_rectangle(screen.zones[j], visual.GREEN, alpha=100)
                screen.update()
                audio.play_feedback(True)
            else:
                screen.blit_rectangle(screen.zones[j], visual.BLUE, alpha=100)
                screen.update()
            corr = 1

        # incorrect response
        else:
            if phase == 'practice':
                screen.blit_rectangle(screen.zones[j], visual.RED, alpha=100)
                screen.update()
                audio.play_feedback(False)
            else:
                screen.blit_rectangle(screen.zones[j], visual.BLUE, alpha=100)
                screen.update()
            corr = 0
            break

    # end of trial
    trial_info = tuple(
        list(trial_info) + [
            corr, trial_clock.tick_busy_loop(), str(responses)
        ]
    )
    if phase == 'practice':
        events.wait(study_duration)
    print len(output_format), len(trial_info)
    return trial_info


def stopping_rule(data):
    """
    Returns True if all three of the trials of a given moves length were
    incorrect.
    """
    print ''
    df = data.to_df()
    df = df[df.phase == 'test']
    if len(df) > 0:
        df = df.set_index('trialn', drop=False)
        last = df.ix[len(df) - 1].nsymbols
        df = df[df.nsymbols == last]
        if len(df) == 3:
            print 'checking ...'
            print df.correct
            print df[df.correct == 1]
            if len(df[df.correct == 1]) == 0:
                return True


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '', ans_col='endpoint')

    df = summaries.make_df(stats)
    # print '---Here are the summary stats:'
    # print df.T

    return df

if __name__ == '__main__':
    batch.run_single_test(test_name)