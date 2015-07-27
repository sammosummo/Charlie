# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

stroop: Familiar-size Stroop test

This version of the Stroop task was developed by Konkle and Oliva [1], and the
stimuli are taken directly from Konkle's website. On each trial, the proband
decides which of two images (left or right) is smaller. The images depict
real-world objects of different sizes. This design produces a reliable Stroop
effect. Deciding which image is the smallest - as opposed to deciding which
image is larger, or which object is smaller or larger - produces the strongest
Stroop effect, so only this version of the task is included here. The task also
has the advantage of not requiring verbal stimuli. There are 4 practice trials
and 112 test trials (56 congruent and 56 incongruent in terms of image size and
physical object size).

Summary statistics:

    overall*
    [congruent or incongruent]*

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *pcorrect : proportion of trials correct.
    *dprime : index of sensitivity.
    *criterion : index of bias.
    *rt_mean : mean response time on correct trials in milliseconds.
    *rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    *rt_outrmvd : number of outlier trials.

    stroop_ncorrect : incongruent minus congruent
    stroop_pcorrect
    stroop_dprime
    stroop_rt_mean_outrmvd


References:

[1] Konkle, T. & Oliva, A. (2012). A familiar-size Stroop effect: real-world
size is an automatic property of object representation. J Exp Psychol Human
Percept Performance, 38(3):561-569.

NOTE: This test was not producing clear Stroop effects in the first batch of 60
subjects and so was dropped from the Olin batch!

"""
__version__ = 1.0
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.visual as visual
import charlie.tools.audio as audio
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch

test_name = 'stroop'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('cong', str),
    ('f', str),
    ('ans', str),
    ('rsp', str),
    ('rt', int)
]
prac_answers = [1, 0, 1, 1]
stim_order = [98, 53, 9, 10, 103, 95, 31, 32, 46, 42, 40, 100, 84, 21, 68, 86,
              15, 30, 111, 91, 34, 102, 29, 80, 83, 56, 81, 78, 77, 104, 35, 3,
              69, 11, 89, 26, 85, 33, 90, 27, 54, 7, 39, 96, 2, 97, 1, 92, 8,
              6, 107, 58, 41, 61, 12, 55, 36, 22, 109, 17, 94, 79, 13, 57, 4,
              74, 63, 72, 47, 25, 88, 70, 14, 16, 20, 18, 93, 23, 5, 108, 37,
              76, 101, 24, 65, 71, 19, 62, 50, 51, 49, 87, 67, 110, 66, 99,
              106, 52, 44, 73, 60, 43, 75, 28, 64, 0, 105, 82, 45, 38, 59, 48]
    

def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, congruence, f, ans).
    """
    p = data.pj(data.VISUAL_PATH, test_name)
    prac_stimuli = sorted(f for f in data.ld(p) if 'png' in f and 'prac' in f)
    labels = instructions[-2:]
    control = []
    
    for trialn, s in enumerate(prac_stimuli):
        control.append((proband_id, test_name, 'practice', trialn, 'n/a',
                        data.pj(p, s), labels[prac_answers[trialn]]))
    
    test_stimuli = sorted(f for f in data.ld(p) if 'png' in f \
        and 'prac' not in f)
    test_stimuli = [j for i, j in sorted(zip(stim_order, test_stimuli))]
    
    for trialn, s in enumerate(test_stimuli):
        cong = ['Congruent', 'Incongruent']['In' in s]
        n = int(s.split('-')[0])
        if n <= 28:
            if cong == 'Congruent':
                ans = labels[1]
            else:
                ans = labels[0]
        else:
            if cong == 'Congruent':
                ans = labels[0]
            else:
                ans = labels[1]
        f = data.pj(p, s)
        control.append((proband_id, test_name, 'test', trialn, cong, f, ans))
    
    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    
    _, _, phase, trialn, _, f, ans = trial_info
    img_pos = (0, -100)
    labels = instructions[-2:]
    if not screen.wordzones:
        screen.load_keyboard_keys()
        screen.create_keyboard_key_zones(('l', 'r'), 200, 250)
        screen.create_word_zones(labels, 200, 350)

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
            
            screen.countdown_splash(5, instructions[2])
    
    # set up trial
    img = screen.images[f]
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l', 'r'), ('', ''))
    screen.blit_image(img, img_pos, update=False)
    screen.update()

    # wait for a response
    keys = [276, 275]
    keydown = events.wait_for_valid_keydown(keys, 'key')   
    if keydown == 'EXIT':
        return 'EXIT'
    else:
        k, rt = keydown
    rsp = dict(zip(keys, labels))[k]
    rspk = dict(zip(keys,('l', 'r')))[k]

    # update screen
    if phase == 'test':
        screen.change_word_colour(rsp, visual.BLUE)
        screen.change_key_colour(rspk, 'b', update=False)
        screen.update()
        events.wait(events.DEFAULT_ITI_NOFEEDBACK)
        screen.wipe(img.get_rect(center=img_pos))
    else:
        corr = rsp == ans
        if corr:
            screen.change_word_colour(rsp, visual.GREEN)
            screen.change_key_colour(rspk, 'g', update=True)
        else:
            screen.change_word_colour(rsp, visual.RED)
            screen.change_key_colour(rspk, 'r', update=True)
        audio.play_feedback(corr)
        events.wait(events.DEFAULT_ITI_FEEDBACK)
        screen.wipe(img.get_rect(center=img_pos))

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

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, 'overall')
    stats += summaries.get_rt_stats(df, 'overall')
    stats += summaries.get_sdt_stats(df, noise, signal, 'overall')

    for cong in df.cong.unique():
        prefix = '%s' % cong.lower()
        df1 = df[df.cong == cong]
        stats += summaries.get_accuracy_stats(df1, prefix)
        stats += summaries.get_rt_stats(df1, prefix)
        stats += summaries.get_sdt_stats(df1, noise, signal, prefix)

    df = summaries.make_df(stats)
    for dv in ['ncorrect', 'dprime', 'rt_mean_outrmvd']:
        x = 'stroop_%s' %dv
        y = float(df['congruent_%s' % dv] - df['incongruent_%s' % dv])
        stats.append((x, y))

    df = summaries.make_df(stats)
    # print '---Here are the summary stats:'
    # print df.T

    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)