# -*- coding: utf-8 -*-
"""
digit_symbol_delay: Delayed digit-symbol recognition test.

This is a very brief test designed to be administered immediately after the
digit_symbol. On each trial, the proband sees the digit array, but not the
symbol array, from the main test, and a symbol in the middle of the screen. The
proband must click on the digit corresponding to the symbol. This test was
originally part of STAN [1].

Preliminary work suggests that this test does not produce great data. It might
not be worth the ~1 minute it takes to complete.

Summary statistics:

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *pcorrect : proportion of trials correct.

References:

[1] Glahn, D.C., Almasy, L., Blangero, J., Burk, G.M., Estrada, J., Peralta, J.
M., et al. (2007). Adjudicating neurocognitive endophenotypes for
schizophrenia. Am. J. Med. Genet. B. Neuropsychiatr. Genet., 44B(2):242-249.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch


test_name = 'digit_symbol_delay'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('trialn', int),
    ('ans', str),
    ('f', str),
    ('rsp', str),
    ('rt', int)
]
symbols = [6, 7, 4, 8, 5, 1, 9, 2, 3]


def control_method(proband_id, instructions):
    """
    Generate a control iterable. For this test, each item represents a trial
    in the format: (proband_id, test_name, phase, trialn, digit, symbol, ans,
    f).
    """
    p = data.pj(data.VISUAL_PATH, test_name)
    y = lambda x: data.pj(p, 'sym%i.bmp' %x)
    return [(proband_id, test_name, i, s, y(s)) for i, s in enumerate(symbols)]


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    proband_id, test_name, trialn, digit, f = trial_info
    if not trialn:
        rsp = screen.splash(instructions[0], mouse=False)
        if rsp == 'EXIT':
            return 'EXIT'
        screen.wipe()
    if not screen.wordzones:
        screen.create_word_zones(list('123456789'), 100, -200)
    screen.change_word_colour(screen.wordzones.keys(),
                              [visual.DEFAULT_TEXT_COLOUR] * 9)
    spacing = 100
    x0 = - int(0.5 * spacing * (9 - 1))
    y = -300
    for i, word in enumerate(list('?????????')):
        x = x0 + spacing*i
        screen.blit_text(word, (x,y), visual.DEFAULT_TEXT_COLOUR)
    img = screen.images[f]
    screen.blit_image(img, (0, 0), update=False)
    screen.update()

    mouse_click = events.wait_for_valid_mouse_click(screen, 1)
    if mouse_click == 'EXIT':
        return 'EXIT'
    rsp, rt = mouse_click
    trial_info = tuple(list(trial_info) + [rsp + 1, rt])

    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
    df = summaries.make_df(stats)

    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)