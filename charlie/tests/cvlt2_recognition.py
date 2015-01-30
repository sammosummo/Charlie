# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

cvlt2_recognition: Recognition portion of the computerised California verbal
learning test.

This is third and final part of the modified and abridged CVLT-II [1]. In this
test, the proband performs a yes-no recognition memory task. The 16 target
words from the CVLT serve as signal (or 'yes') trials, and there are 30 noise
(or 'no') words. Each noise word belongs to one of the same four semantic
clusters as the targets.


Summary statistics:

    valid : Number of valid responses on trial X.
    intrusions : Number of intrusions on trial X.
    repetitions : Number of repetitions on trial X.
    semantic : List-based semantic clustering index on trial X.
    serial : List-based serial recall index on trial X.
    dprime : Recall discriminability index.
    criterion : Recall bias.

References:

[1] Delis, D.C., Kramer, J.H., Kaplan, E., & Ober, B.A. (2000). California
verbal learning test - second edition. Adult version. Manual. Psychological
Corporation, San Antonio, TX.

"""
"""
Created on Fri Mar 14 16:52:26 2014

The California verbal learning test (CVLT), recognition portion.

This is the final portion of the CVLT. Here, the proband hears the 16 target
words plus 16 novel distractors in random order, and performs a standard yes/no
recognition-memory task using the left and right arrow keys. There is no
feedback and there are no practice trials. Accuracy and response times are
recorded. Target and distracter words are taken from the official CVLT. See
cvlt.py for more details.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
import charlie.tools.visual as visual
import charlie.tools.audio as audio
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries

test_name = 'cvlt2_recognition'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trialn', int),
                 ('f', str),
                 ('word', str),
                 ('ans', str),
                 ('rsp', str),
                 ('rt', int)]

word_pos = (0,-100)


def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, trialn, f, word, ans)."""

    # find the paths to the stimuli and put them in the correct order
    p = data.pj(data.AUDIO_PATH, test_name, 'EN')
    instr = instructions
    instr, labels = instr, instr[2:4]
    words = instr[-1].split('\n')
    stimuli = [w + '.wav' for w in words]

    # determine what was in the original word list
    p2 = data.pj(data.AUDIO_PATH, 'cvlt2', 'EN')
    control = [(proband_id, test_name, i, data.pj(p, f), words[i],
                labels[f not in data.ld(p2)]) for i, f in enumerate(stimuli)]
    return control


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""
    _, _, trialn, f, word, _ = trial_info
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


def summary_method(data, instructions):
    """Computes summary stats for this task. Collects the trial-by-trial
    data by calling the to_df() method from the data object, filters out the
    practice trials, gets universal entries, generates a condition set, then
    summary stats are produced for each combination of levels from the
    condition set."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    labels = instructions[2:4]
    a, b = summaries.get_2alt(df, choices=labels)
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