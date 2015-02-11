# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 15:12:07 2014

ipcpts: The identical pairs continuous performance test, three-symbol version

This test is based on the original continuous performance test introduced by
Rosvold et al. [1] and the subsequent identical-pairs modification [2]. On each
trial, the proband sees a three-item symbol array, and presses the space bar
each time the current array matches the array from the previous trial
(effectively a 1-back task). Trials have a duration of 1.5 seconds. There
are 200 trials in the test phase. The symbols were originally designed by D.
Glahn for STAN. The task is identical to the STAN version.

Summary statistics:

    ntrials : number of trials completed
    ncorrect : number of trials correct
    dprime : sensitivity
    criterion : response bias
    rt_mean : mean response time on correct trials in milliseconds.
    rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    rt_outrmvd : number of outlier trials.

References:

[1] Rosvold, H.E., Mirsky, A.F., Sarason, I., Bransome, E.D. Jr., & Beck, L.H.
(1956). A continuous performance test of brain damage. J. Consult. Clin.
Psychol., 20:343-350.

[2] Cornblatt, B.A., Risch, N.J., Faris, G., Friedman, D., &
Erlenmeyer-Kimling, L. (1988). The continuous performance test, identical pairs
version (CPT-IP): I. New findings about sustained attention in normal families.
Psychiatr. Res., 26(2):223–38.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.audio as audio
import charlie.tools.batch as batch


test_name = 'ipcpts'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('matches', int),
    ('ans', str),
    ('symbol1', str),
    ('symbol2', str),
    ('symbol3', str),
    ('rsp', str),
    ('rt', int)
]
presentation_time = 1
wait_time = .5

practice_matches = [0, 0, 0, 3, 0, 3, 0]
practice_symbols = [(0, 1, 2), (1, 2, 6), (3, 4, 7), (3, 4, 7), (4, 7, 3),
                    (4, 7, 3), (7, 1, 0)]
matches = [0,
           0, 3, 3, 0, 3, 0, 1, 3, 1, 3, 2, 2, 2, 0, 0, 3, 0, 3, 0, 3, 0, 2, 3,
           2, 3, 1, 2, 1, 0, 2, 0, 1, 0, 3, 0, 2, 3, 1, 0, 0, 2, 3, 1, 3, 3, 0,
           0, 0, 3, 3, 3, 0, 3, 3, 0, 0, 3, 3, 0, 3, 0, 1, 2, 3, 2, 2, 0, 0, 1,
           2, 1, 3, 0, 2, 2, 1, 0, 2, 1, 0, 3, 0, 3, 3, 3, 1, 0, 3, 0, 0, 0, 3,
           3, 0, 3, 0, 1, 2, 0, 2, 1, 0, 3, 2, 1, 0, 3, 0, 1, 0, 0, 3, 0, 0, 3,
           3, 0, 0, 2, 0, 3, 0, 1, 3, 3, 3, 3, 3, 2, 3, 0, 0, 1, 0, 3, 0, 0, 3,
           0, 0, 1, 2, 0, 3, 0, 1, 3, 0, 0, 2, 3, 1, 0, 3, 3, 0, 3, 0, 3, 3, 3,
           2, 0, 2, 3, 0, 0, 3, 1, 0, 3, 0, 3, 2, 3, 0, 3, 3, 3, 2, 2, 0, 3, 1,
           1, 3, 1, 3, 3, 1, 1, 1, 2, 0, 0, 3, 3, 1, 0, 2]
symbols = [(0, 1, 2), (6, 9, 0), (6, 9, 0), (6, 9, 0), (3, 5, 8), (3, 5, 8),
           (9, 3, 0), (2, 4, 0), (2, 4, 0), (4, 5, 0), (4, 5, 0), (8, 5, 0),
           (8, 5, 4), (8, 3, 4), (1, 7, 9), (9, 5, 2), (9, 5, 2), (6, 2, 9),
           (6, 2, 9), (8, 5, 2), (8, 5, 2), (0, 7, 5), (0, 1, 5), (0, 1, 5),
           (0, 8, 5), (0, 8, 5), (0, 3, 2), (5, 3, 2), (0, 3, 5), (3, 8, 9),
           (2, 8, 9), (5, 6, 2), (1, 9, 2), (0, 5, 7), (0, 5, 7), (3, 6, 0),
           (2, 6, 0), (2, 6, 0), (2, 8, 3), (8, 2, 0), (5, 7, 9), (5, 7, 2),
           (5, 7, 2), (9, 0, 2), (9, 0, 2), (9, 0, 2), (7, 3, 6), (4, 2, 7),
           (6, 3, 1), (6, 3, 1), (6, 3, 1), (6, 3, 1), (1, 0, 8), (1, 0, 8),
           (1, 0, 8), (4, 8, 3), (3, 1, 2), (3, 1, 2), (3, 1, 2), (7, 5, 8),
           (7, 5, 8), (1, 9, 3), (0, 9, 6), (0, 2, 6), (0, 2, 6), (0, 2, 9),
           (0, 2, 5), (1, 7, 0), (3, 1, 2), (0, 1, 7), (9, 1, 7), (9,  3, 5),
           (9, 3, 5), (8, 4, 9), (8, 0, 9), (8, 1, 9), (9, 1, 6), (7, 3, 0),
           (7, 3, 1), (0, 4, 1), (3, 2, 6), (3, 2, 6), (6, 0, 7), (6, 0, 7),
           (6, 0, 7), (6, 0, 7), (1, 6, 7), (9, 1, 3), (9, 1, 3), (0, 4, 8),
           (1, 0, 3), (5, 9, 6), (5, 9, 6), (5, 9, 6), (6, 7, 3), (6, 7, 3),
           (4, 9, 0), (5, 3, 0), (8, 3, 0), (7, 9, 2), (7, 3, 2), (7, 4, 1),
           (8, 0, 7), (8, 0, 7), (8, 0, 1), (8, 4, 7), (1, 3, 6), (1, 3, 6),
           (5, 1, 0), (8, 1, 2), (0, 4, 5), (4, 5, 7), (4, 5, 7), (6, 7, 0),
           (5, 2, 1), (5, 2, 1), (5, 2, 1), (7, 4, 5), (9, 8, 0), (9, 8, 6),
           (6, 3, 2), (6, 3, 2), (4, 5, 7), (7, 5, 0), (7, 5, 0), (7, 5, 0),
           (7, 5, 0), (7, 5, 0), (7, 5, 0), (7, 1, 0), (7, 1, 0), (4, 9, 5),
           (5, 0, 7), (5, 7, 0), (1, 3, 6), (1, 3, 6), (7, 4, 8), (8, 0, 5),
           (8, 0, 5), (4, 1, 6), (9, 8, 4), (1, 8, 0), (3, 8, 0), (2, 6, 7),
           (2, 6, 7), (5, 0, 9), (5, 8, 4), (5, 8, 4), (6, 2, 1), (2, 1, 6),
           (3, 1, 6), (3, 1, 6), (0, 1, 7), (5, 6, 9), (5, 6, 9), (5, 6, 9),
           (7, 0, 8), (7, 0, 8), (5, 1, 9), (5, 1, 9), (5, 1, 9), (5, 1, 9),
           (0, 1, 9), (8, 0, 4), (8, 0, 6), (8, 0, 6), (6, 3, 8), (8, 4, 7),
           (8, 4, 7), (7, 4, 8), (6, 8, 4), (6, 8, 4), (9, 2, 7), (9, 2, 7),
           (1, 2, 7), (1, 2, 7), (4, 8, 6), (4, 8, 6), (4, 8, 6), (4, 8, 6),
           (0, 8, 6), (9, 8, 6), (7, 3, 2), (7, 3, 2), (9, 6, 2), (4, 0, 2),
           (4, 0, 2), (4, 8, 3), (4, 8, 3), (4, 8, 3), (9, 4, 3), (6, 9, 3),
           (1, 9, 0), (1, 9, 7), (7, 8, 4), (0, 2, 1), (0, 2, 1), (0, 2, 1),
           (0, 3, 4), (9, 8, 1), (3, 8, 1)]


def control_method(proband_id, instructions):
    """
    Generates a control iterable. Both phases of the task are time-limited.
    Therefofe, the control object contains only two items.
    """
    return [(proband_id, test_name, phase) for phase in ('practice', 'test')]


def trial_method(screen, instructions, trial_info):
    """
    Run all the trials. It was much easier to write one function to do all
    trials than a function that is called per trial.
    """
    proband_id, test_name, phase = trial_info
    p = data.pj(data.VISUAL_PATH, test_name)
    screen.load_keyboard_keys()
    yes, no = instructions[-2:]
    
    p = data.pj(data.VISUAL_PATH, test_name)
    stim = lambda x: data.pj(p, 'sym%i.bmp' % x)
    if phase == 'practice':
        T = zip(range(len(practice_matches)),
                practice_matches,
                practice_symbols)
        msg = instructions[0]
    else:
        T = zip(range(len(matches)), matches, symbols)
        msg = instructions[1]
    control = [(proband_id, test_name, phase, i, m, ['No', 'Yes'][m == 3],
                stim(s[0]), stim(s[1]), stim(s[2])) for (i, m, s) in T]

    # instructions
    rsp = screen.splash(msg, mouse=False)
    if rsp == 'EXIT':
        return 'EXIT'
    screen.wipe()
    screen.countdown_splash(5, instructions[2])
    screen.wipe()


    # set up trials
    keys = [32]  # the space bar
    if phase == 'practice':
        pt = presentation_time * 2000
        wt = wait_time * 2000
    else:
        pt = presentation_time * 1000
        wt = wait_time * 1000
    clock = events.Clock()

    # run trials
    _data = []
    screen.update()

    while control:
        trial_info = control.pop(0)
        events.clear()
        current_time = 0
        symbols_on = False
        rsp = no
        rt = 0
        screen.reset_zones()

        while current_time < pt + wt:

            current_time += clock.tick_busy_loop()

            if current_time < pt and not symbols_on:

                images = [screen.images[a] for a in trial_info[-3:]]
                screen.create_image_zones(images, 150, -50)
                screen.create_keyboard_key_zones(['s'], 0, 250)
                screen.update_image_zones(update=False)
                screen.change_key_colour('s', '', update=False)
                screen.update()
                symbols_on = True

            elif current_time > pt and symbols_on:

                screen.wipe([t[1] for t in screen.imagezones.values()],
                            prc=False)
                symbols_on = False

            k = events.poll_for_valid_keydown(keys, 'key')
    
            if k == 'EXIT':
                return 'EXIT'
            
            elif k and rsp == 'No':

                rsp = yes
                rt = current_time
                if trial_info[2] == 'practice':
                    if trial_info[4] == 3:
                        screen.change_key_colour('s', 'g', update=False)
                        screen.update()
                        audio.play_feedback(True)
                    else:
                        screen.change_key_colour('s', 'r', update=False)
                        screen.update()
                        audio.play_feedback(False)
                else:
                    screen.change_key_colour('s', 'b', update=False)
                    screen.update()
                screen.update_image_zones()
                events.wait(events.DEFAULT_ITI_NOFEEDBACK)
                screen.change_key_colour('s', '', update=False)
                screen.update()

        trial_info = tuple(list(trial_info) + [rsp, rt])
        print trial_info
        _data.append(trial_info)
    return _data


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
    stats += summaries.get_rt_stats(df, '')
    stats += summaries.get_sdt_stats(df, 'No', 'Yes', '')
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