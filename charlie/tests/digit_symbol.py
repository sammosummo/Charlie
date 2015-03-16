# -*- coding: utf-8 -*-
"""
digit_symbol: Digit-symbol substitution test.

This test was originally designed by D. Glahn for an earlier computerised
test battery called STAN [1]. Although it shares its name with a pen-and-paper
test found in the WAIS-III [2], it is not known how performance on the two
tests is related.

On each trial, the proband sees a key of digits and symbols at the top of the
screen, as well as a single digit and a single symbol in the centre of the
screen. The proband indicates whether the target symbol matches the target
digit according to the key by responding either 'yes' or 'no'. During the test
phase, the proband completes as many trials as they can within 90 seconds. The
symbols currently the same as those in the STAN.

Summary statistics:

    ntrials : number of trials completed
    ncorrect : number of trials correct
    dprime : sensitivity
    criterion : response bias
    rt_mean : mean response time on correct trials in milliseconds.
    rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    rt_outrmvd : number of outlier trials.

References:

[1] Glahn, D.C., Almasy, L., Blangero, J., Burk, G.M., Estrada, J., Peralta, J.
M., et al. (2007). Adjudicating neurocognitive endophenotypes for
schizophrenia. Am. J. Med. Genet. B. Neuropsychiatr. Genet., 44B(2):242-249.

[2] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual.
San Antonio, TX: The Psychological Corporation.

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

test_name = 'digit_symbol'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('digit', int),
    ('symbol', int),
    ('ans', str),
    ('f', str),
    ('rsp', str),
    ('rt', int)
]
max_time = 90
practice_order = [(2,2), (6,6),
                  (8,4), (4,4),
                  (7,7), (6,5),
                  (2,8), (9,2),
                  (3,7), (5,6)]
test_order = [(8,8), (1,4), (2,8), (6,2), (4,4), (9,5), (5,6), (3,3), (4,4),
              (9,9), (6,6), (1,1), (2,2), (7,7), (3,3), (8,8), (7,7), (5,3),
              (1,5), (4,4), (7,8), (4,4), (8,8), (3,3), (5,5), (3,1), (6,9),
              (2,2), (8,8), (9,2), (1,6), (5,4), (6,6), (2,2), (9,9), (7,7),
              (3,3), (1,8), (6,6), (7,7), (9,5), (7,9), (5,7), (2,2), (1,1),
              (6,4), (8,3), (2,2), (4,4), (9,1), (4,4), (5,5), (3,3), (8,8),
              (9,9), (7,7), (3,1), (9,7), (1,8), (8,9), (4,2), (2,6), (5,5),
              (2,2), (8,8), (5,5), (4,3), (6,6), (1,1), (7,7), (3,3), (6,4),
              (3,3), (5,5), (6,8), (9,1), (1,5), (2,2), (3,3), (7,7), (2,2),
              (8,4), (7,7), (8,2), (5,5), (4,9), (6,6), (4,3), (1,1), (9,9),
              (6,6), (2,2), (1,8), (5,5), (5,5), (8,8), (3,3), (6,6), (8,9),
              (2,2), (1,1), (5,5), (6,4), (5,5), (5,6), (4,4), (9,2), (7,9),
              (9,1), (1,8), (9,9), (7,7), (4,2), (2,2), (6,6), (3,3), (4,3)]


def control_method(proband_id, instructions):
    """
    Generate a control iterable. For this test, each item represents a trial
    in the format: (proband_id, test_name, phase, trialn, digit, symbol, ans,
    f).

    Note that there is only one 'test' trial; this was done because the testing
    phase ends after a certain time has elapsed rather than a number of trials,
    and it was sensible to code this way.
    """

    # find the paths to the stimuli
    p = data.pj(data.VISUAL_PATH, test_name)
    stim = lambda x: data.pj(p, 'sym%i.bmp' %x)
    
    labels = instructions[-2:]

    # practice trials
    trialns = range(len(practice_order))
    digits = [a for a, b in practice_order]
    symbols = [b for a, b in practice_order]
    answers = [labels[a!=b] for a, b in practice_order]
    trials = zip(trialns, digits, symbols, answers)
    control = [(proband_id, test_name, 'practice', trialn, digit, symbol, ans,
                stim(symbol)) for trialn, digit, symbol, ans in trials]
    control += [(proband_id, test_name, 'test', None, None, None, None, None)]

    return control


def trial_method(screen, instructions, trial_info):
    """
    Run a single trial of the test. Not that there is only one trial in the
    'test' phase.
    """
    proband_id, test_name, phase, trialn, digit, symbol, ans, f = trial_info
    labels = instructions[-2:]
    if not screen.wordzones:
        screen.load_keyboard_keys()
        screen.create_keyboard_key_zones(('l', 'r'), 200, 250)
        images = sorted(f for f in screen.images if 'sym' in f)
        screen.create_image_zones(sorted(images), 100, -300)
        screen.create_word_zones(list('123456789'), 100, -200)
        screen.create_word_zones(labels, 200, 350)
    
    if phase == 'practice':
        
        # show instructions if first trial
        if not trialn:
            rsp = screen.splash(instructions[0], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
    
        # set up trial
        screen.update_image_zones()
        img = screen.images[f]
        p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
        screen.change_word_colour(*p)
        screen.change_key_colour(('l','r'), ('',''))
        screen.change_word_colour(list('123456789'),
                                  [visual.DEFAULT_TEXT_COLOUR] * 9)
        screen.blit_image(img, (0, 0))
        q, r = screen.blit_text(str(digit), (0, 100), update=False,
                                font=screen.font2)
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
        corr = rsp == ans
        if corr:
            screen.change_word_colour(rsp, visual.GREEN)
            screen.change_key_colour(rspk, 'g', update=True)
        else:
            screen.change_word_colour(rsp, visual.RED)
            screen.change_key_colour(rspk, 'r', update=True)
        audio.play_feedback(corr)
        events.wait(events.DEFAULT_ITI_FEEDBACK)
        screen.wipe(img.get_rect(center=(0,0)), update=False)
        screen.wipe(r)
    
        # return trial outcome
        trial_info = tuple(list(trial_info) + [rsp, rt])
        return trial_info

    else:

        #create a new control iterable
        p = data.pj(data.VISUAL_PATH, test_name)
        stim = lambda x: data.pj(p, 'sym%i.bmp' %x)
        trialns = range(len(test_order))
        digits = [a for a, b in test_order]
        symbols = [b for a, b in test_order]
        answers = [labels[a!=b] for a, b in test_order]
        trials = zip(trialns, digits, symbols, answers)
        control = [(proband_id, test_name, 'test', i, d, s, a, stim(s)) for (i,
                   d, s, a) in trials]
        _data = []
    
        if not trialn:
            rsp = screen.splash(instructions[1], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
            
            screen.countdown_splash(5, instructions[2])
    
        # set up trials
        screen.wipe()
        events.clear()
        current_time = 0
        new_trial = True
        keys = [276, 275]
        clock = events.Clock()
        while current_time < max_time:
    
            current_time += (clock.tick_busy_loop()/1000.)
    
            if new_trial:
    
                new_trial = False
                trial_clock = events.Clock()
                _, _, phase, trialn, digit, symbol, ans, f = control.pop(0)
                screen.update_image_zones()
                img = screen.images[f]
                p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
                screen.change_word_colour(*p)
                screen.change_key_colour(('l','r'), ('',''))
                screen.change_word_colour(list('123456789'),
                                        [visual.DEFAULT_TEXT_COLOUR] * 9)
                screen.blit_image(img, (0, 0))
                q, r = screen.blit_text(str(digit), (0,100), update=False,
                                        font=screen.font2)
                screen.update()
    
            k = events.poll_for_valid_keydown(keys, 'key')
    
            if k == 'EXIT':
                return 'EXIT'
            
            elif k:
                rt = trial_clock.tick_busy_loop()
                new_trial = True
                rsp = dict(zip(keys,labels))[k]
                rspk = dict(zip(keys,('l', 'r')))[k]
                screen.change_word_colour(rsp, visual.BLUE)
                screen.change_key_colour(rspk, 'b', update=False)
                screen.update()
                # screen.wipe(img.get_rect(center=(0,0)), update=False)
                # screen.wipe(r)
                trial_info = (proband_id, test_name, phase, trialn, digit,
                              symbol, ans, f, rsp, rt)
                _data.append(trial_info)
    
            events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    
        return _data


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']
    labels = instructions[-2:]
    signal, noise = labels

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
    stats += summaries.get_rt_stats(df, '')
    stats += summaries.get_sdt_stats(df, noise, signal, '')
    df = summaries.make_df(stats)
    print '---Here are the summary stats:'
    print df.T

    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)