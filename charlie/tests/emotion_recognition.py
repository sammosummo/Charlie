# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

emotion_recognition: The Penn emotion recognition test (ER-40).

This test was developed by Gur and colleagues [1]. On each trial, the proband
sees a colour image of a face expressing an emotion (happy, sad, fearful,
angry) or with a neutral expression. There are two levels of each emotion
(except neutral), two male faces per emotion per level, and two female faces
per emotion and level, resulting in 40 trials total. Probands make their
responses by clicking on the words printed to the screen. There is no feedback
and there are no practice trials.

Summary statistics:

    overall_*
    [emotion]_*
    [emotion]_[sex]_*
    [emotion]_[sex]_[salience]_*

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *pcorrect : proportion of trials correct.
    *rt_mean : mean response time on correct trials in milliseconds.
    *rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    *rt_outrmvd : number of outlier trials.

References:

[1] Gur, R.C., Sara, R., Hagendoorn, M., Marom, O., Hughett, P., Macy L., et
al. (2002). A method for obtaining 3-dimensional facial expressions and its
standardization for use in neurocognitive studies. J. Neurosci. Methods,
115:137–143.

"""
# TODO: Calculate d' for 4AFC?

__version__ = 1.0
__author__ = 'Sam Mathias'

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
from charlie.tools.instructions import quickfix as qf

test_name = 'emotion_recognition'
stim_order = [23, 9, 18, 12, 14, 5, 1, 35, 31, 13, 10, 0, 30, 38, 36, 6, 15,
              33, 32, 7, 26, 3, 21, 29, 39, 28, 37, 22, 8, 4, 2, 27, 11, 19,
              34, 25, 16, 17, 24, 20]
img_pos = (0, -150)
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('trialn', int),
    ('sex', str),
    ('emotion', str),
    ('salience', str),
    ('f', str),
    ('rsp', str),
    ('rt', int)
]
black_bg = True


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, trialn, sex, emotion, salience, f).
    """
    p = data.pj(data.VISUAL_PATH, test_name)
    stimuli = sorted(f for f in data.ld(p) if '.png' in f)
    stimuli = [j for _, j in sorted(zip(stim_order, stimuli))]
    emo_dict = {l.split('=')[0]: l.split('=')[1] for l in instructions[-5:]}
    control = []
    for trialn, imgf in enumerate(stimuli):
        print trialn, imgf, emo_dict
        control.append((proband_id, test_name, trialn,
                        {'M': 'Male', 'F': 'Female'}[imgf[0]],
                        emo_dict[imgf[1]],
                        {'X': 'Weak', 'Z': 'Strong', '_': 'N/A'}[imgf[2]],
                        data.pj(p, imgf)))
    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    _, _, trialn, _, _, _, imgf = trial_info
    labels = [l.split('=')[1] for l in instructions[-5:]]
    if not screen.wordzones:
        screen.create_word_zones(labels, 175, 250)
    
    # show instructions if first trial
    if not trialn:
        rsp = screen.splash(instructions[0], mouse=False)
        if rsp == 'EXIT':
            return 'EXIT'
        screen.wipe()# wait for a response
        screen.countdown_splash(5, instructions[1])
        screen.wipe()
    
    # set up trial
    img = screen.images[imgf]
    params = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*params)
    screen.blit_image(img, img_pos, update=False)
    screen.update()

    # wait for a response
    mouse_click = events.wait_for_valid_mouse_click(screen, 1)
    if mouse_click == 'EXIT':
        return 'EXIT'
    i, rspt = mouse_click

    # update screen
    screen.change_word_colour(labels[i], visual.BLUE, update=False)
    screen.update()
    events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    screen.wipe(img.get_rect(center=img_pos))

    trial_info = tuple(list(trial_info) + [labels[i], rspt])
    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    print 'did this'
    df = data_obj.to_df()
    stats = summaries.get_universal_stats(data_obj)
    prefix = 'overall'
    stats += summaries.get_accuracy_stats(df, prefix, ans_col='emotion')
    stats += summaries.get_rt_stats(df, prefix, ans_col='emotion')
    for emotion in df.emotion.unique():
        print emotion
        prefix = emotion.lower()
        df1 = df[df.emotion == emotion]
        stats += summaries.get_accuracy_stats(df1, prefix, ans_col='emotion')
        stats += summaries.get_rt_stats(df1, prefix, ans_col='emotion')
        for sex in df1.sex.unique():
            print sex
            prefix = emotion.lower() + '_' + sex.lower()
            df2 = df1[df1.sex == sex]
            stats += summaries.get_accuracy_stats(df2, prefix,
                                                  ans_col='emotion')
            stats += summaries.get_rt_stats(df2, prefix, ans_col='emotion')
            if len(df2.salience.unique()) == 2:
                for sal in df2.salience.unique():
                    print sal
                    prefix = emotion.lower() + '_' + sex.lower() + '_' + \
                             sal.lower()
                    df3 = df2[df2.salience == sal]
                    stats += summaries.get_accuracy_stats(df3, prefix,
                                                          ans_col='emotion')
                    stats += summaries.get_rt_stats(df3, prefix,
                                                    ans_col='emotion')
    df = summaries.make_df(stats)
    print '---Here are the summary stats:'
    print df.T
    # cols, entries = summaries.get_universal_entries(data)
    # emo_dict = {l.split('=')[1]: l.split('=')[0] for l in instructions[-5:]}
    # df = data.to_df()
    # a, b = summaries.get_accuracy(df, 'overall', 'emotion', True)
    # cols += a; entries += b
    # for emotion in df.emotion.unique():
    #     df1 = df[df.emotion == emotion]
    #     a, b = summaries.get_accuracy(df1, emotion.lower(), 'emotion', True)
    #     cols += a; entries += b
    #     for sex in df1.sex.unique():
    #         prefix = '%s_%s' %(emotion, sex)
    #         df2 = df1[df1.sex == sex]
    #         a, b = summaries.get_accuracy(df2, prefix.lower(), 'emotion', True)
    #         cols += a; entries += b
    #         for salience in df2.salience.unique():
    #             if salience != 'N/A':
    #                 prefix = '%s_%s_%s' %(emotion, sex, salience)
    #                 df3 = df2[df2.salience == salience]
    #                 a, b = summaries.get_accuracy(df2, prefix.lower(),
    #                                               'emotion', True)
    #                 cols += a; entries += b
    # dfsum = pandas.DataFrame(entries, cols).T
    # return dfsum

def main():
    """
    Run this test.
    """
    batch.run_a_test(test_name)


if __name__ == '__main__':
    main()