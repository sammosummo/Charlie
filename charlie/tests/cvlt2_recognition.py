# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

cvlt2_recognition: Recognition portion of the computerised California verbal
learning test.

This is third and final part of the modified and abridged CVLT-II [1]. In this
test, the proband performs a yes-no recognition memory task. The 16 target
words from the CVLT serve as signal (or 'yes') trials, and there are 32 noise
(or 'no') words. Sixteen of the noise words come from one of the four semantic
categories as the targets ('prototypical' words), and 16 come from other
categories ('unrelated' words).

In the original CVLT, some of the noise words comprise list B. Since we don't
perform list B, we just count these as prototypical or unrelated.

Summary statistics:

    overall_*
    proto_*
    unrel_*

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *pcorrect : proportion of trials correct.
    *dprime : index of sensitivity.
    *criterion : index of bias.
    *rt_mean : mean response time on correct trials in milliseconds.
    *rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    *rt_outrmvd : number of outlier trials.

References:

[1] Delis, D.C., Kramer, J.H., Kaplan, E., & Ober, B.A. (2000). California
verbal learning test - second edition. Adult version. Manual. Psychological
Corporation, San Antonio, TX.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'


import charlie.tools.visual as visual
import charlie.tools.audio as audio
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch


test_name = 'cvlt2_recognition'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('trialn', int),
    ('f', str),
    ('word', str),
    ('type', str),
    ('ans', str),
    ('rsp', str),
    ('rt', int)
]
word_pos = (0,-100)
types = 'utuptputtupputupttpputpuptututpppuutpttpuutputpu'


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, trialn, f, word, type, ans).
    """
    path = lambda w: data.pj(data.AUDIO_PATH, 'cvlt2', w + '.wav')
    ans = lambda i: labels[types[i] == 't']
    instr = instructions
    instr, labels = instr, instr[2:4]
    words = instr[-1].split('\n')
    return [(proband_id, test_name, i, path(w), w, types[i], ans(i)) for i,
        w in enumerate(words)]


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    _, _, trialn, f, word, _, _ = trial_info
    instr = instructions
    instr, labels = instr, instr[2:4]
    if not screen.wordzones:
        screen.load_keyboard_keys()
        screen.create_keyboard_key_zones(('l', 'r'), 200, 250)
        screen.create_word_zones(labels, 200, 350)

    # show instructions if first trial
    if not trialn:
        rsp = screen.splash(instructions[0], mouse=False)
        if rsp == 'EXIT':
            return 'EXIT'
        screen.wipe()
        screen.countdown_splash(5, instructions[1])
        screen.wipe()

    # set up trial
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l', 'r'), ('', ''))
    q, r = screen.blit_text(word, word_pos, update=False, font=screen.font2)
    screen.update()
    audio.play_sound(f)

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
    screen.change_word_colour(rsp, visual.BLUE)
    screen.change_key_colour(rspk, 'b', update=False)
    screen.update()
    events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    screen.wipe(q.get_rect(center=word_pos))

    # return trial outcome
    trial_info = tuple(list(trial_info) + [rsp, rt])

    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    instr = instructions
    instr, labels = instr, instr[2:4]
    signal, noise = labels

    stats = summaries.get_universal_stats(data_obj)
    df1 = df
    prefix = 'overall'
    stats += summaries.get_accuracy_stats(df1, prefix)
    stats += summaries.get_rt_stats(df1, prefix)
    stats += summaries.get_sdt_stats(df1, noise, signal, prefix)
    df1 = df[(df['type'] == 'u') | (df['type'] == 't')]
    prefix = 'unrel'
    stats += summaries.get_accuracy_stats(df1, prefix)
    stats += summaries.get_rt_stats(df1, prefix)
    stats += summaries.get_sdt_stats(df1, noise, signal, prefix)
    df1 = df[(df['type'] == 'p') | (df['type'] == 't')]
    prefix = 'proto'
    stats += summaries.get_accuracy_stats(df1, prefix)
    stats += summaries.get_rt_stats(df1, prefix)
    stats += summaries.get_sdt_stats(df1, noise, signal, prefix)

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

# TODO: stimuli are currently missing!