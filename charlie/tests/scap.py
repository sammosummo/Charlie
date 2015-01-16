# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

scap: Spatial capacity delayed-response test.

On each trial, the proband sees a study array comprising three to five yellow
circles in random positions on the screen. The study array is removed and,
after a delay, is replaced by a single green circle (the probe). The proband
indicates whether the probe has the same spatial location as one of the
original circles. In this version of the SCAP, there are 14 three-, 14 four-
and 14 five-item trials.

Reference for the original SCAP:

Glahn, D.C., Therman, S., Manninen, M., Huttunen, M., Kaprio, J., Lönnqvist,
J., & Cannon T. D. (2003). Spatial working memory as an endophenotype for
schizophrenia. Biol Psychiatry, 53(7):624-626.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.audio as audio


test_name = 'scap'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('phase', str),
                 ('load', int),
                 ('trialn', int),
                 ('ans', str),
                 ('array_f', str),
                 ('probe_f', str),
                 ('rsp', str),
                 ('rt', int)]

array_duration = .2
retention_interval = 0
prac_answers = [1, 0, 1]
prac_loads = [1, 2, 3]
answers = {3: (1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0),
           4: (0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0),
           5: (1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0)}
img_pos = (0, -100)
retention_image = data.pj(data.VISUAL_PATH, test_name, 'fix.BMP')

visual.BG_COLOUR = visual.BLACK
visual.DEFAULT_TEXT_COLOUR = visual.WHITE


def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, load, trialn, ans, array_f,
    probe_f)."""
    
    def get_f(phase, stimtype, load, trialn):
        p = data.pj(data.VISUAL_PATH, test_name)
        if phase == 'practice':
            if stimtype == 'array':
                f = 'practice-%i.BMP' % xrange(1, 6, 2)[trialn]
            elif stimtype == 'probe':
                f = 'practice-%i.BMP' % xrange(2, 7, 2)[trialn]
        elif phase == 'test':
            if stimtype == 'array':
                f = 'load%i-%i.BMP' % (load, xrange(1, 28, 2)[trialn])
            elif stimtype == 'probe':
                f = 'load%i-%i.BMP' % (load, xrange(2, 29, 2)[trialn])
        return data.pj(p, f)
    
    labels = instructions[-2:]
    control = []
    for phase in ['practice', 'test']:
        if phase == 'practice':
            details = zip(range(3), prac_loads, prac_answers)
            for trialn, load, ans in details:
                array_f = get_f(phase, 'array', load, trialn)
                probe_f = get_f(phase, 'probe', load, trialn)
                control.append((proband_id, test_name, phase, load, trialn,
                                labels[::-1][ans], array_f, probe_f))
        elif phase == 'test':
            for load in sorted(answers.keys()):
                for trialn, ans in enumerate(answers[load]):
                    array_f = get_f(phase, 'array', load, trialn)
                    probe_f = get_f(phase, 'probe', load, trialn)
                    control.append((proband_id, test_name, phase, load, trialn,
                                    labels[::-1][ans], array_f, probe_f))
    return control


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""
    _, _, phase, load, trialn, ans, array_f, probe_f = trial_info
    labels = instructions[-2:]
    if not screen.wordzones:
        screen.load_keyboard_keys()
        screen.create_keyboard_key_zones(('l', 'r'), 200, 250)
        screen.create_word_zones(labels, 200, 350)
    
    # show instructions if first trial
    if not trialn and load == 3:
        if phase == 'test':
            rsp = screen.splash(instructions[1], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
            screen.countdown_splash(5, instructions[2])
            screen.wipe()
        else:
            rsp = screen.splash(instructions[0], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
            
    # set up trial
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l', 'r'), ('', ''))

    # show array
    array = screen.images[array_f]
    img, rect = screen.blit_image(array, img_pos, update=False)
    screen.update()

    # wait
    events.wait(array_duration)

    # remove array
    retention = screen.images[retention_image]
    img, rect = screen.blit_image(retention, img_pos, update=False)
    screen.update()
    events.wait(retention_interval)

    # show
    probe = screen.images[probe_f]
    img, rect = screen.blit_image(probe, img_pos, update=False)
    screen.update()

    # wait for a response
    keys = [276, 275]
    keydown = events.wait_for_valid_keydown(keys, 'key')   
    if keydown == 'EXIT':
        return 'EXIT'
    else:
        k, rt = keydown
    rsp = dict(zip(keys,labels))[k]
    rspk = dict(zip(keys,('l', 'r')))[k]

    # update screen
    corr = ans == rsp
    if phase == 'practice':
        colour = [visual.RED, visual.GREEN][corr]
        clr = ['r', 'g'][corr]
        audio.play_feedback(corr)
        screen.change_word_colour(rsp, colour)
        screen.change_key_colour(rspk, clr, update=False)
        screen.update()
        events.wait(events.DEFAULT_ITI_FEEDBACK)
    else:
        screen.change_word_colour(rsp, visual.BLUE)
        screen.change_key_colour(rspk, 'b', update=False)
        screen.update()
        events.wait(events.DEFAULT_ITI_NOFEEDBACK)

    # return trial outcome
    trial_info = tuple(list(trial_info) + [rsp, rt])

    return trial_info


def summary_method(data, instructions):
    """Computes summary stats for this task. Collects the trial-by-trial
    data by calling the to_df() method from the data object, filters out the
    practice trials, gets universal entries, generates a condition set, then
    summary stats are produced for each combination of levels from the
    condition set."""
    df = data.to_df()
    df = df[df.phase != 'practice']
    cols, entries = summaries.get_universal_entries(data)
    
    condition_set = [('load', [3, 4, 5, 'all'])]
    labels = instructions[-2:]
    a, b = summaries.get_all_combinations_2alt(df, condition_set, labels)
    cols += a
    entries += b
    dfsum = pandas.DataFrame(entries, cols).T

    return dfsum


def main():
    """Command-line executor."""
    params = (test_name,
              control_method,
              trial_method,
              output_format,
              summary_method)
    batch.run_single_test(*params)


if __name__ == '__main__':
    main()