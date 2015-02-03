# -*- coding: utf-8 -*-
"""
Created on Wed Oct  1 12:08:08 2014

matrix_reasoning: Matrix reasoning test.

This is identical to the matrix reasoning test from the WAIS-III [1]. On each
trial, the proband sees a matrix with one missing item in the centre of the
screen, and an array of alternatives below. The task is to select the correct
element from the array by clicking within its area. There is one practice
trial, which will not progress until the correct answer is selected. The test
will terminate prematurely if four out of the last five trials were incorrect.
Probands can sometimes spend minutes on single trials of this test. To try to
prevent this, each trial has a time limit of two minutes. The stimuli are taken
direction from the WAIS-III.

Summary statistics:

    ntrials : number of trials completed
    ncorrect : number of trials correct

References:

[1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual.
San Antonio, TX: The Psychological Corporation.

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


test_name = 'matrix_reasoning'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('matrix', str),
    ('array', str),
    ('ans', int),
    ('rsp', int),
    ('rt', int)
]
answers = [1, 3, 1, 3, 2, 0, 0, 2, 4, 4, 4, 1, 2, 0, 1, 3, 2, 0, 0, 3, 4, 4, 1,
           1, 0, 4, 3, 2, 2, 3, 0, 3, 1, 2, 4]
timeout = 120


def stopping_rule(data):
    """
    Returns True if four out of the five previous responses are
    incorrect.
    """
    df = data.to_df()
    df = df[df.phase == 'test']
    trials, __ = df.shape
    if trials >= 5:
        corr = df.ix[trials-4 : trials].ans == df.ix[trials-4 : trials].rsp
        if len(corr[corr]) <= 1:
            return True


def control_method(proband_id, instructions):
    """
    Generate a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, matrix, array, ans).
    """

    # find the paths to the stimuli
    p = data.pj(data.VISUAL_PATH, test_name)
    prac_matrix = 'prac_MA.png'
    prac_array = 'prac_MAa.png'
    matrices = sorted([s for s in data.ld(p) if 'png' in s and 'a.png'
                       not in s])
    arrays = sorted([s for s in data.ld(p) if 'a.png' in s])

    # practice trial
    control = [(proband_id, test_name, 'practice', 0, data.pj(p, prac_matrix),
                data.pj(p, prac_array), 1)]

    # test trials
    trials = zip(range(len(matrices)), matrices, arrays, answers)
    while trials:
        trialn, matrix, array, ans = trials.pop(0)
        control += [(proband_id, test_name, 'test', trialn, data.pj(p, matrix),
                     data.pj(p, array), ans)]

    return control


def trial_method(screen, instructions, trial_info):
    """
    Run a single trial. Since the practice trial is very similar to the test
    trials, all are done within this script.
    """
    proband_id, test_name, phase, trialn, matrix, array, ans = trial_info

    # show instructions if first trial
    if phase == 'practice':
        if not trialn:
            rsp = screen.splash(instructions[0], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
            
    else:
        if not trialn:
            rsp = screen.splash(instructions[1], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()

    # show trial
    screen.wipe(update=False)
    screen.reset_zones()
    screen.blit_image(matrix, (0, -150), update=False)
    image, r = screen.blit_image(array, (0, 300), update=False)
    zones = [(r.x+r.w/5*i, r.y, r.w/5, r.h) for i in xrange(5)]
    screen.create_rect_zones(zones)
    [screen.blit_rectangle(rect) for rect in screen.zones]
    screen.flip()

    # set up timer
    clock = events.Clock()
    time_left = 120000
    
    while time_left > 0:
        
        mouse_click = events.poll_for_valid_mouse_click(screen, 1)
        
        if mouse_click == 'EXIT':
            return 'EXIT'
        
        elif mouse_click is None:
            pass
        
        else:
            rsp = mouse_click

            # if this is the practice trial, do some extra stuff
            if phase == 'practice':
                while rsp != ans:
                    audio.play_feedback(False)
                    screen.blit_rectangle(screen.zones[rsp], visual.RED,
                                          alpha=100)
                    screen.flip()
                    rsp, rt = events.wait_for_valid_mouse_click(screen,
                                                                      1)
                audio.play_feedback(True)
                screen.blit_rectangle(screen.zones[rsp], visual.GREEN,
                                      alpha=100)
                screen.flip()
                events.wait(events.DEFAULT_ITI_FEEDBACK)
        
            # if a regular trial
            else:
                screen.blit_rectangle(screen.zones[rsp], visual.BLUE,
                                      alpha=100,update=False)
                screen.update()
                events.wait(events.DEFAULT_ITI_NOFEEDBACK)
        
            return tuple(list(trial_info) + [rsp, 120000-time_left])
    
        time_left -= clock.tick_busy_loop()
    
    print 'time up'
    return tuple(list(trial_info) + [999, 999])


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
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