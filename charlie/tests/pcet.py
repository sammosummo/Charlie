# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

pcet: Penn conditional exclusion test

This test is based on form 1 of the original PCET [1]. On each trial, the
proband sees four symbols. Three of the symbols will have identical shapes,
three will have identical thicknesses, and will three have identical sizes. The
task is to click on the one that does not belong to the others according to an
unknown rule (either thickness, shape, or size). Feedback is given after each
trial, allowing the subject to learn the exclusion rule. The rule is constant
for 12 consecutive trials and then changes.

Summary statistics:

    ntrials : number of trials.
    ncorrect : number of trials correct.
    pcorrect : proportion of trials correct.
    persev : number of "perseverative" errors (errors after rule change that
             match the previous rule).
    nonpersev : number of non-perseverative errors.
    lapses : number of errors that do not match any rule.
    nlearned : number of rule sets with >= 50% correct.
    rt_mean : mean response time on correct trials in milliseconds.
    rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    rt_outrmvd : number of outlier trials.

References:

[1] Kurtz, M.M., Ragland, D.J., Moberg, P.J, & Gur, R.C. (2004). The Penn
Conditional Exclusion Test: A new measure of executive-function with alternate
forms for repeat administration. Arch. Clin. Neuropsych., 19: 191-201.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
import charlie.tools.audio as audio

test_name = 'pcet'
img_pos = (0, -150)
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('rule', str),
    ('ans', str),
    ('pers', str),
    ('other', str),
    ('lapse', str),
    ('f1', str),
    ('f2', str),
    ('f3', str),
    ('f4', str),
    ('rsp', str),
    ('rt', int)
]

details = [
    (0, 'thickness', 3, None, None, 1, '010.png', '000.png', '001.png', '100.png'),
    (1, 'thickness', 2, None, None, 0, '110.png', '111.png', '010.png', '100.png'),
    (2, 'thickness', 0, None, None, 3, '010.png', '111.png', '100.png', '110.png'),
    (3, 'thickness', 3, None, None, 1, '000.png', '010.png', '011.png', '110.png'),
    (4, 'thickness', 0, None, None, 3, '011.png', '110.png', '101.png', '111.png'),
    (5, 'thickness', 3, None, None, 1, '100.png', '101.png', '111.png', '001.png'),
    (6, 'thickness', 1, None, None, 3, '010.png', '100.png', '001.png', '000.png'),
    (7, 'thickness', 0, None, None, 1, '101.png', '001.png', '000.png', '011.png'),
    (8, 'thickness', 0, None, None, 1, '010.png', '110.png', '111.png', '100.png'),
    (9, 'thickness', 1, None, None, 3, '100.png', '010.png', '111.png', '110.png'),
    (10, 'thickness', 2, None, None, 0, '111.png', '101.png', '011.png', '110.png'),
    (11, 'thickness', 0, None, None, 1, '011.png', '111.png', '101.png', '110.png'),
    (12, 'shape', 0, 3, 2, 1, '110.png', '100.png', '101.png', '000.png'),
    (13, 'shape', 3, 2, 1, 0, '101.png', '100.png', '001.png', '111.png'),
    (14, 'shape', 3, 1, 0, 2, '101.png', '000.png', '100.png', '110.png'),
    (15, 'shape', 1, 3, 0, 2, '101.png', '110.png', '100.png', '000.png'),
    (16, 'shape', 1, 0, 3, 2, '111.png', '001.png', '011.png', '010.png'),
    (17, 'shape', 2, 1, 3, 0, '111.png', '011.png', '101.png', '110.png'),
    (18, 'shape', 3, 2, 1, 0, '010.png', '011.png', '110.png', '000.png'),
    (19, 'shape', 1, 0, 2, 3, '000.png', '110.png', '101.png', '100.png'),
    (20, 'shape', 3, 2, 1, 0, '101.png', '100.png', '001.png', '111.png'),
    (21, 'shape', 1, 0, 3, 2, '010.png', '100.png', '110.png', '111.png'),
    (22, 'shape', 2, 1, 0, 3, '000.png', '101.png', '011.png', '001.png'),
    (23, 'shape', 1, 0, 2, 3, '100.png', '010.png', '001.png', '000.png'),
    (24, 'size', 0, 2, 3, 1, '101.png', '100.png', '110.png', '000.png'),
    (25, 'size', 3, 2, 0, 1, '001.png', '101.png', '111.png', '100.png'),
    (26, 'size', 0, 3, 2, 1, '000.png', '001.png', '101.png', '011.png'),
    (27, 'size', 1, 2, 3, 0, '101.png', '100.png', '111.png', '001.png'),
    (28, 'size', 2, 3, 1, 0, '110.png', '010.png', '111.png', '100.png'),
    (29, 'size', 1, 0, 2, 3, '111.png', '100.png', '001.png', '101.png'),
    (30, 'size', 0, 1, 2, 3, '011.png', '000.png', '110.png', '010.png'),
    (31, 'size', 3, 1, 0, 2, '110.png', '000.png', '010.png', '011.png'),
    (32, 'size', 0, 2, 1, 3, '000.png', '101.png', '011.png', '001.png'),
    (33, 'size', 3, 1, 2, 0, '011.png', '001.png', '111.png', '010.png'),
    (34, 'size', 2, 3, 1, 0, '011.png', '111.png', '010.png', '001.png'),
    (35, 'size', 2, 0, 1, 3, '010.png', '100.png', '001.png', '000.png'),
    (36, 'thickness', 2, 3, 1, 0, '010.png', '000.png', '110.png', '011.png'),
    (37, 'thickness', 3, 2, 1, 0, '101.png', '111.png', '100.png', '001.png'),
    (38, 'thickness', 0, 3, 1, 2, '100.png', '010.png', '000.png', '001.png'),
    (39, 'thickness', 0, 3, 2, 1, '010.png', '110.png', '100.png', '111.png'),
    (40, 'thickness', 0, 1, 2, 3, '001.png', '100.png', '111.png', '101.png'),
    (41, 'thickness', 3, 0, 2, 1, '111.png', '110.png', '100.png', '010.png'),
    (42, 'thickness', 0, 3, 1, 2, '110.png', '000.png', '010.png', '011.png'),
    (43, 'thickness', 0, 3, 2, 1, '000.png', '100.png', '110.png', '101.png'),
    (44, 'thickness', 2, 1, 3, 0, '010.png', '011.png', '110.png', '000.png'),
    (45, 'thickness', 3, 0, 2, 1, '011.png', '010.png', '000.png', '110.png'),
    (46, 'thickness', 1, 3, 2, 0, '101.png', '001.png', '111.png', '100.png'),
    (47, 'thickness', 1, 3, 2, 0, '010.png', '110.png', '000.png', '011.png'),
    (48, 'shape', 3, 2, 1, 0, '110.png', '111.png', '010.png', '100.png'),
    (49, 'shape', 1, 0, 3, 2, '101.png', '011.png', '001.png', '000.png'),
    (50, 'shape', 2, 0, 3, 1, '101.png', '001.png', '011.png', '000.png'),
    (51, 'shape', 1, 3, 0, 2, '111.png', '100.png', '110.png', '010.png'),
    (52, 'shape', 1, 3, 2, 0, '100.png', '110.png', '101.png', '000.png'),
    (53, 'shape', 1, 2, 0, 3, '001.png', '010.png', '100.png', '000.png'),
    (54, 'shape', 3, 0, 1, 2, '010.png', '111.png', '110.png', '100.png'),
    (55, 'shape', 3, 0, 2, 1, '001.png', '101.png', '100.png', '111.png'),
    (56, 'shape', 2, 1, 3, 0, '001.png', '101.png', '011.png', '000.png'),
    (57, 'shape', 0, 2, 1, 3, '100.png', '111.png', '010.png', '110.png'),
    (58, 'shape', 2, 3, 1, 0, '001.png', '000.png', '011.png', '101.png'),
    (59, 'shape', 0, 1, 2, 3, '111.png', '001.png', '100.png', '101.png'),
    (60, 'size', 0, 2, 1, 3, '101.png', '000.png', '110.png', '100.png'),
    (61, 'size', 2, 3, 0, 1, '100.png', '000.png', '001.png', '010.png'),
    (62, 'size', 2, 0, 1, 3, '111.png', '001.png', '100.png', '101.png'),
    (63, 'size', 1, 0, 3, 2, '010.png', '001.png', '000.png', '100.png'),
    (64, 'size', 0, 2, 3, 1, '110.png', '111.png', '101.png', '011.png'),
    (65, 'size', 3, 1, 0, 2, '100.png', '010.png', '000.png', '001.png'),
    (66, 'size', 3, 1, 2, 0, '011.png', '001.png', '111.png', '010.png'),
    (67, 'size', 1, 2, 3, 0, '011.png', '010.png', '001.png', '111.png'),
    (68, 'size', 0, 2, 3, 1, '100.png', '101.png', '111.png', '001.png'),
    (69, 'size', 0, 1, 2, 3, '100.png', '111.png', '001.png', '101.png'),
    (70, 'size', 1, 0, 3, 2, '111.png', '100.png', '101.png', '001.png'),
    (71, 'size', 1, 2, 3, 0, '010.png', '011.png', '000.png', '110.png'),
]

# Used for generating the stimuli. Don't uncomment!---------------------------
# import numpy as np
# features = ['thickness', 'shape', 'size']
#
# X = np.tile(np.arange(4), 72).reshape(72, 4)
# map(np.random.shuffle, X)
# Y = np.random.randint(2, size=(72, 3))
# p = lambda x: ''.join(str(int(i)) for i in x) + '.png'
#
# Z = np.zeros((72, 4, 3))
# for i, x in enumerate(X):
#     # trial
#     y = Y[i] # standard vals
#     for j, m in enumerate(x):
#         # symbol
#         Z[i, j] = y
#         if m < 3:
#             if Z[i, j, m] == 1:
#                 Z[i, j, m] = 0
#             else:
#                 Z[i, j, m] = 1
#
# for i in xrange(72):
#     trialn = i
#     rule = rules[i]
#     ix = features.index(rule)
#     deviations = list(X[i])
#     ans = deviations.index(ix)
#     if i < 12:
#         prev_rule = None
#         pers = None
#         other = None
#     else:
#         prev_rule = features[ix-1]
#         ix = features.index(prev_rule)
#         pers = deviations.index(ix)
#         other_rule = features[ix-1]
#         ix = features.index(other_rule)
#         other = deviations.index(ix)
#     lapse = deviations.index(3)
#     x = [trialn, rule, ans, pers, other, lapse]
#     x += [p(Z[i, j]) for j in xrange(4)]
#     print tuple(x)
# ----------------------------------------------------------------------------


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, trialn, sex, emotion, salience, f).
    """
    s = lambda x: data.pj(data.VISUAL_PATH, test_name, x)
    control = [(proband_id, test_name, 'practice', 0, None, 2, 2, 2, 2,
               s('000.png'), s('000.png'), s('111.png'), s('000.png'))]
    for x in details:
        t = [proband_id, test_name, 'test'] + list(x)
        t[-3:] = [s(i) for i in t[-3:]]
        control.append(t)
    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    print 'heeo'
    _, _, phase, trialn, _, ans, _, _, _,f1, f2, f3, f4 = trial_info
    
    # show instructions if first trial
    if not trialn:
        if phase == 'practice':
            m = instructions[0]
        else:
            m = instructions[1]
        rsp = screen.splash(m, mouse=False)
        if rsp == 'EXIT':
            return 'EXIT'
        screen.wipe() # wait for a response
        if phase == 'test':
            screen.countdown_splash(5, instructions[2])
        screen.wipe()
    
    # set up trial
    screen.reset_zones()
    images = [f1, f2, f3, f4]
    screen.create_image_zones(images, 50, 0)
    screen.update()

    # wait for a response
    mouse_click = events.wait_for_valid_mouse_click(screen, 1)
    if mouse_click == 'EXIT':
        return 'EXIT'
    rsp, rspt = mouse_click

    # update screen
    if rsp == ans:
        corr = True
        suffix = 'g'
    else:
        corr = False
        suffix = 'f'
    images[rsp] = images[rsp].split('.png')[0] + '_%s.png' % suffix
    screen.create_image_zones(images, 50, 0)
    screen.update()
    audio.play_feedback(corr)
    events.wait(events.DEFAULT_ITI_FEEDBACK)

    trial_info = tuple(list(trial_info) + [rsp, rspt])
    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']
    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
    stats += summaries.get_rt_stats(df, '')

    x = 0
    dfs = df.groupby('rule')
    for df1 in dfs:
        for df2 in [df1.ix[:12], df1.ix[12:]]:
            if len(df2[df2.ans == df2.rsp]) >= 6:
                x += 1

    stats += [
        ('persev', len(df[df.rsp == df.pers])),
        ('nonpersev', len(df[df.rsp == df['other']])),
        ('lapse', len(df[df.rsp == df.lapse]))
        ('nlearned', x)
    ]
    df = summaries.make_df(stats)
    print '---Here are the summary stats:'
    print df.T
    return df


def main():
    """
    Run this test.
    """
    batch.run_a_test(test_name)


if __name__ == '__main__':
    main()