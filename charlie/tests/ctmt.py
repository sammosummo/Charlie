# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

cTrails: Computerised comprehensive trail-making test.

This is a computerised version of Reynold's comprehensive trail-making test
[1, 2], which is itself an extension of the popular trail-making test [3]. On
each trial, the proband must click on circles drawn on the screen in a
specified order, making a 'trail' between them. There are a total of 10 trials
in the test, with one practice and one test trial of each kind. Each practice
trial contains 8 circles and each test trial contains 25 circles. In order to
provide better backwards compatibility between the original trail-making test,
the final trial of the comprehensive test has been modified so that it contains
no distracter circles.

The traditional tests are done with pen and paper and require an experienced
experimenter to administer them. The current version should be more convenient
than the traditional tests, but it is unknown to what extent performance on
this test correlates with the originals.

The original trail-making test (the one with parts A and B) is a subset of the
trials used here. Summary stats for those are provided for convenience.
Moreover, the differences between parts A and B, which have been found to be
useful predictors as well [4], are also provided.


Summary statistics:

    trial_X_time : total time in ms taken to complete trial X.
    trial_x_errors : number of incorrect clicks on trial X.
    total_time : summed time in ms of all trials.
    total_errors : errors over all trials.
    part_Y_time : total time in ms taken to complete either part A or B.
    part_Y_errors : number of incorrect clicks on either part A or B.
    diff_time : part B minus part A.
    diff_errors : part B minus part A.

References:

[1] Reynolds, C. (2002). Comprehensive trail making test (CTMT). PRO-ED, Inc.,
Austin, TX.

[2] Armstrong, C.M., Allen, D.N., Donohue, B., & Mayfield, J. (2008)
Sensitivity of the comprehensive trail making test to traumatic brain injury in
adolescents, Arch. Clin. Neuropsych., 23(3):351-358.

[3] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept. Mot. Skills., 8:271-276.

[4] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and
B of the Trail Making Test. J. Clin. Psychol., 43(4):402–409.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries


test_name = 'ctmt'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('trialn', int),
    ('phase', str),
    ('ntargets', int),
    ('n', int),
    ('rsp', str),
    ('corr', str),
    ('rt', int),
    ('total_time', int)
]
circle_labels = [
    range(1, 9),
    range(1, 26),
    range(1, 9) + [None] * 8,
    range(1, 26) + [None] * 29,
    range(1, 9) + [None] * 4 + ['!', '@', '#', '$'],
    range(1, 26) + [None] * 13 + ['!', '@', '#', '$', '%', '^', '&', '*', '(',
                                  ')', '-', '_', '+', '=', '`', '~', ':', ';',
                                  '?', '/'],
    [1, 'two', 3, 4, 'five', 6, 7, 8],
    [1, 2, 3, 'four', 'five', 6, 'seven', 8, 9, 'ten', 11, 'twelve', 13,
     'fourteen', 15, 'sixteen', 17, 'eighteen', 'nineteen', 20],
    list('1a2b3c4d'),
    [1, 'a', 2, 'b', 3, 'c', 4, 'd', 5, 'e', 6, 'f', 7, 'g', 8, 'h', 9, 'i',
     10, 'j', 11, 'k', 12, 'l', 13]

]
phases = ['practice', 'test'] * 5
ntargets = [8, 25, 8, 25, 8, 25, 8, 20, 8, 25]
target_labels = [[circle_labels[j] for j in xrange(ntargets[i])] for i in xrange(10)]


print target_labels

#
#
# circle_positions = [
#     [
#         (-238, -111), (387, 60), (347, -269), (135, -157),
#         (34, -360),  (-227, 17),  (130, 122),  (400, 320)
#     ],
#     [
#         (-264, -59),    (257, 205),  (-156, 238),  (90, -144), (370, -146),
#         (205, -348),  (-209, -253), (-358, -211),  (-43, -37), (122, -264),
#         (-176, -359), (-139, -185),    (170, 12),    (400, 0),   (396, 88),
#         (347, 316),      (-5, 172),   (138, -67), (-11, -165), (211, -216),
#         (400, -300),    (250, -46),  (-200, 101),  (237, 103),   (35, 329),
#         (300, -329)
#     ],
#     [
#         (-285, -22), (-44, 131), (-291, 138), (26, -219),
#         (261, 41), (-324, -200), (258, -342), (191, 353)
#     ]
#     [
#         (344, 272),  (-58, 254), (-353, -329),  (243, -172),  (150, -400),
#         (300, -309), (380, -18),  (-387, -47), (-186, -385), (-189, -153),
#         (361, 125), (-311, 104),  (-231, 247),  (-71, -192),   (92, -310),
#         (298, -88),   (-77, 36),     (98, 73),   (244, 187),    (33, 169),
#         (146, 341), (-136, 336),  (-147, 201), (-294, -102),  (-33, -313),
#         (80, -113)
#     ]
#     [
#         (337, 13),    (-345, -3),  (396, 280),  (-365, 118),
#         (86, -231), (-306, -275), (366, -125), (-165, -131)
#     ],
#     [
#         (-316, -140), (-385, 6), (-387, -346), (296, -328),   (303, -57),
#         (308, 252),   (361, 23),    (127, 30), (-266, -64),  (-166, -64),
#         (193, -217), (-88, 123),   (178, 213), (353, -240),  (-27, -399),
#         (-65, -228), (-248, 58),   (-33, 270), (-371, 180), (-205, -274),
#         (60, -276),  (-132, 28),    (76, 101),   (91, 346),  (-126, 345),
#         (-400, 366)
#     ]
# ]  # TODO: 6 more trials.
#
#
# sequences = {
# 'number': {'practice': _d[:8], 'test': _d},
# 'letter': {'practice': list(_l[:8]), 'test': list(_l)},
# 'number-letter': {
#     'practice': [i for l in zip(_d, _l)[:4] for i in l],
#     'test': [i for l in zip(_d, _l)[:13] for i in l]
#     }
# }
#
#
# def control_method(proband_id, instructions):
#     """Generates a control iterable. For this test, this is a list of tuples in
#     the format (proband_id, test_name, phase, trial_type)."""
#     return [(proband_id, test_name, p, t) for p in phases for t in trial_types]
#
#
# def trial_method(screen, instructions, trial_info):
#     """Runs a single trial of the test."""
#     _, _, phase, trial_type = trial_info
#
#     # gather correct instructions from the instructions list
#     ix = phases.index(phase)
#     instructions = instructions[ix * 3 : ix * 3 + 3]
#     if trial_type == 'test':
#         _ = instructions.pop(0)
#     del _
#
#     # show initial instructions
#     keydown = screen.splash(instructions.pop(0), mouse=True)
#     if keydown == 'EXIT':
#         return 'EXIT'
#     screen.wipe()
#
#     # set up countdown
#     if trial_type == 'test':
#         screen.countdown_splash(5, instructions.pop(0))
#
#     # set up trial
#     trial_clock = events.Clock()
#     trial_clock.tick_busy_loop()
#     path = data.pj(data.VISUAL_PATH, test_name)
#     filename = lambda x: data.pj(path, 'a_%s.png' % str(x))
#     pos = positions[phase][trial_type]
#     sequence = sequences[phase][trial_type]
#     screen.wipe(update=False)
#     screen.reset_zones()
#     zones = []
#     for item, position in zip(sequence, pos):
#         image, r = screen.blit_image(filename(item), position, update=False)
#         zones.append(r)
#     screen.create_rect_zones(zones)
#     screen.flip()
#     all_responses = []
#     all_rts = []
#     remaining_responses = list(sequence)
#     clicked_zones = []
#
#     # trial loop
#     while remaining_responses:
#
#         mouse_click = events.wait_for_valid_mouse_click(screen, 1)
#
#         if mouse_click == 'EXIT':
#             return 'EXIT'
#         else:
#             r, rt = mouse_click
#
#         response = sequence[r]
#
#         if response is remaining_responses[0]:
#             remaining_responses.pop(0)
#             clicked_zones.append(zones[r])
#
#             if len(clicked_zones) > 1:
#
#                 # draw a trail
#                 screen.blit_line(clicked_zones[-2], clicked_zones[-1], 10)
#
#             else:
#                 # draw a tick
#                 x1, y1 = clicked_zones[-1].center
#                 x0, y0 = x1 - 10, y1 - 20
#                 x2, y2 = x1 + 20, y1 - 50
#                 screen.blit_line((x0, y0), (x1, y1), 10, prc=False)
#                 screen.blit_line((x1, y1), (x2, y2), 10, prc=False)
#
#             screen.update()
#
#         # record response
#         response = sequence[r]
#         all_responses.append(response)
#         all_rts.append(rt)
#
#     # trial over; consolidate data
#     total_time = trial_clock.tick_busy_loop()
#     data_from_this_trial = []
#     remaining_responses = list(sequence)
#
#     for i, response, rt in zip(xrange(len(all_rts)), all_responses, all_rts):
#
#         t = list(trial_info) + [i, response]
#         if response is remaining_responses[0]:
#             t.append('Correct')
#             remaining_responses.pop(0)
#         else:
#             t.append('Incorrect')
#         t += [rt, total_time]
#         t = tuple(t)
#
#         data_from_this_trial.append(t)
#
#     return data_from_this_trial
#
#
# def summary_method(data, instructions):
#     """Computes summary stats for the trails task."""
#     df = data.to_df()
#     cols, entries = summaries.get_universal_entries(data)
#
#     df = df[df.trial_type == 'test']
#
#     for phase in df.phase.unique():
#         cols += ['%s_nerrors' % phase, '%s_total_time' % phase]
#         subdf = df[df.phase == phase]
#         entries.append(len(subdf) - len(subdf[subdf['corr'] == 'Correct']))
#         entries.append(list(subdf['total_time'])[0])
#
#     cols += ['letter_minus_number_time',
#              'number-letter_minus_number_time',
#              'number-letter_minus_letter_time']
#     a = list(df[df.phase == 'number']['total_time'])[0]
#     b = list(df[df.phase == 'letter']['total_time'])[0]
#     c = list(df[df.phase == 'number-letter']['total_time'])[0]
#     entries += [b - a, c - a, c - b]
#
#     dfsum = pandas.DataFrame(entries, cols).T
#     return dfsum
#
#
# #def main():
# #    """Command-line executor."""
# #    params = (test_name,
# #              control_method,
# #              trial_method,
# #              output_format,
# #              summary_method)
# #    batch.run_single_test(*params)
#
#
# if __name__ == '__main__':
#     main()