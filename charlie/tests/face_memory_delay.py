# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

face_memory_delay: The Penn facial memory test, delayed condition

This is the second part of the facial memory test. This is the same as the
first part of the test, except that the distractor faces are different and
there is no learning phase.

Reference:

Gur R.C., Ragland J.D., Moberg P.J., Turner T.H., Bilker W.B.,
Kohler C., Siegel S.J., Gur R.E. (2001). Computerized neurocognitive scanning:
I. Methodology and validation in healthy people. Neuropsychopharmacology,
25(5):766-76.

@author: Sam Mathias
@status: completed
@version: 1.0
"""

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('phase', str),
                 ('trialn', int),
                 ('f', str),
                 ('ans', str),
                 ('rsp', str),
                 ('rt', int)]

test_name = 'face_memory_delay'

stim_order = [34, 12, 28, 37, 22, 17, 2, 13, 32, 23, 8, 20, 14, 38, 7, 31, 26,
              3, 5, 15, 10, 24, 36, 1, 9, 39, 18, 19, 33, 0, 35, 30, 6, 4, 27,
              11, 21, 16, 29, 25] #same order for every proband

# overwrite default colours
black_bg = True

def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, f, ans)."""
    p = data.pj(data.VISUAL_PATH, test_name)
    stimuli = sorted(f for f in data.ld(p) if 'bmp' in f)
    stimuli = sorted(f for f in data.ld(p) if 'bmp' in f)
    labels = instructions[-2:]

    targets = sorted(data.pj(p, f) for f in stimuli if 'tar' in f)
    distractors = sorted([data.pj(p, f) for f in stimuli if 'ddis' in f])
    stimuli = [j for i, j in sorted(zip(stim_order, targets + distractors))]
    control = [(proband_id, test_name, 'test', i, f,
                labels['tar' not in f]) for i, f in enumerate(stimuli)]

    return control


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""

    proband_id, test_name, phase, trialn, f, ans = trial_info
    img_pos = (0,-100)
    labels = instructions[-2:]
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
    img = screen.images[f]
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l','r'), ('',''))
    screen.blit_image(img, img_pos, update=False)
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
    screen.change_word_colour(rsp, visual.BLUE)
    screen.change_key_colour(rspk, 'b', update=False)
    screen.update()
    events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    screen.wipe(img.get_rect(center=img_pos))

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
    df = df[df.phase != 'learning']
    cols, entries = summaries.get_universal_entries(data)
    labels = instructions[-2:]
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