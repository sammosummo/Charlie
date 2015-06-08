# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

scap: Spatial capacity delayed-response test.

This is an extended version of the SCAP [1]. On each trial, the proband sees a
study array comprising three to five yellow circles in random positions on the
screen. The study array is removed and, after a delay, is replaced by a single
green circle (the probe). The proband indicates whether the probe has the same
spatial location as one of the original circles. In this version of the SCAP,
there are 14 three-, 14 four- and 14 five-item trials.

Summary statistics:

    overall*
    [load]* : number of items in the study array (3, 4 or 5).

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *pcorrect : proportion of trials correct.
    *dprime : index of sensitivity.
    *criterion : index of bias.
    *rt_mean : mean response time on correct trials in milliseconds.
    *rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    *rt_outrmvd : number of outlier trials.

    k : Cowan's K (estimate of capacity).
    g : Cowan's G (estimate of response bias).

References:

[1] Glahn, D.C., Therman, S., Manninen, M., Huttunen, M., Kaprio, J.,
Lönnqvist, J., & Cannon T. D. (2003). Spatial working memory as an
endophenotype for schizophrenia. Biol. Psychiatry, 53(7):624-626.

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


test_name = 'scap'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('load', int),
    ('trialn', int),
    ('ans', str),
    ('array_f', str),
    ('probe_f', str),
    ('rsp', str),
    ('rt', int)
]
array_duration = 2
retention_interval = 4
prac_answers = [1, 0, 1]
prac_loads = [3, 4, 5]
answers = {3: (1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0),
           4: (0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0),
           5: (1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0)}
img_pos = (0, -100)
retention_image = data.pj(data.VISUAL_PATH, test_name, 'fix.BMP')
black_bg = True


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, load, trialn, ans, array_f,
    probe_f).
    """
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
    """
    Runs a single trial of the test.
    """
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


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']
    labels = instructions[-2:]
    signal, noise = labels
    print labels

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, 'overall')
    stats += summaries.get_rt_stats(df, 'overall')
    stats += summaries.get_sdt_stats(df, noise, signal, 'overall')

    for load in df['load'].unique():
        prefix = 'load_%i' % load
        df1 = df[df['load'] == load]
        stats += summaries.get_accuracy_stats(df1, prefix)
        stats += summaries.get_rt_stats(df1, prefix)
        stats += summaries.get_sdt_stats(df1, noise, signal, prefix)

    stats += summaries.get_cowan_stats(df, noise, signal, '')

    df = summaries.make_df(stats)
    # print '---Here are the summary stats:'
    # print df.T

    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)