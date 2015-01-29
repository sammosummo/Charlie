# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

emotion_recognition: ER40 emotion-recognition test.

In this test, the proband sees images of faces expressing an emotion, and is
required to click on the word that desribes that emotion. There are four
emotions (happy, sad, fearful, angry), and a neutral condition. There are two
levels of each emotion (except neutral), two male faces per emotion per level,
and two female faces per emotion and level, resulting in 40 trials total. There
is no feedback and there are no practice trials. This test is currently set to
have a black background and white text.

Reference:

Gur R.C., Ragland J.D., Moberg P.J., Turner T.H., Bilker W.B., Kohler C.,
Siegel S.J., Gur R.E. (2001). Computerized neurocognitive scanning: I.
Methodology and validation in healthy people. Neuropsychopharmacology,
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
import charlie.tools.batch as batch

test_name = 'emotion_recognition'

stim_order = [23, 9, 18, 12, 14, 5, 1, 35, 31, 13, 10, 0, 30, 38, 36, 6, 15,
              33, 32, 7, 26, 3, 21, 29, 39, 28, 37, 22, 8, 4, 2, 27, 11, 19,
              34, 25, 16, 17, 24, 20]
img_pos = (0, -150)
output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trialn', int),
                 ('sex', str),
                 ('emotion', str),
                 ('salience', str),
                 ('f', str),
                 ('rsp', str),
                 ('rt', int)]

# overwrite default colours
black_bg = True


def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, trialn, sex, emotion, salience, f)."""
    p = data.pj(data.VISUAL_PATH, test_name)
    stimuli = sorted(f for f in data.ld(p) if 'png' in f)
    stimuli = [j for _, j in sorted(zip(stim_order, stimuli))]
    labels = instructions[-5:]
    emotions_dict = {}
    for label in labels:
        code, name = label.split('=')
        emotions_dict[code] = name
    control = []
    for trialn, imgf in enumerate(stimuli):
        print trialn, imgf
        control.append((proband_id, test_name, trialn,
                        {'M': 'Male', 'F': 'Female'}[imgf[0]],
                        emotions_dict[imgf[1]],
                        {'X': 'Weak', 'Z': 'Strong', '_': 'N/A'}[imgf[2]],
                        data.pj(p, imgf)))
    return control


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""
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


def summary_method(data, instructions):
    """Computes summary stats for this task. Collects the trial-by-trial
    data by calling the to_df() method from the data object, filters out the
    practice trials, gets universal entries, generates a condition set, then
    summary stats are produced for each combination of levels from the
    condition set."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    
    condition_set = [('emotion', ['Angry', 'Afraid', 'Sad', 'Happy', 'Neutral',
                                  'all']),
                     ('salience', ['Weak', 'Strong', 'all']),
                     ('sex', ['Male', 'Female', 'all'])]
    
    a, b = summaries.get_all_combinations_malt(df, condition_set,
                                                     ans_col='emotion')
    cols += a
    entries += b
    dfsum = pandas.DataFrame(entries, cols).T
    return dfsum

def main():
    """
    Run this test.
    """
    batch.run_a_test(test_name)


if __name__ == '__main__':
    main()