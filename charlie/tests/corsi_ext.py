"""
Extended version of the Corsi test of spatial memory span. The goal is to (a)
find variants of the paradigm that yield interesting results, and (b) pick
trials that don't yield ceiling or floor effects, and (c) asses test-retest
reliabilities.

If the results are interesting enough, I may be able to spin this into a
small psych paper.

The conditions in the test are as follows:

forward_a: Vanilla Corsi test.
forward_b: As above, except the number of squares is always double the number
of circles.
reverse_a : Same as forward_a, except subjects must report the sequence in
reverse order.
reverse_b: B version of reverse.
sequence_a : Subjects respond with the circles, then Xs.
sequence_b: B version of sequence.
simultaneous_a : Circles all appear simulateously.
simultaneous_b : Cricles and squares appear.

"""
__version__ = 1.0
__author__ = 'smathias'


from itertools import repeat
import random
import numpy as np
import pandas
from pygame import Rect
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
import charlie.tools.audio as audio
import charlie.tools.visual as visual
import charlie.tools.events as events

np.random.seed(2)
test_name = 'corsi_ext'
output_format = [('proband_id', str),
                 ('test_name', str),
                 ('condition', str),
                 ('blockn', str),
                 ('trialn', str),
                 ('n', int),
                 ('positions', str),
                 ('symbols', str),
                 ('correct', int),
                 ('pcorrect', float),
                 ('rt', int),
                 ('responses', str)]
conditions = [
    #'forward_a', 'reverse_a', 'sequence_a',
    'simultaneous_a',
    'simultaneous_b',
    'forward_b',
    'reverse_b',
    'sequence_b',
]
ns = range(2, 10)

def gen_symbols(n):
    s = 'x' * (n/2)
    s += 'c' * (n/2)
    s = ''.join(random.sample(s,len(s)))
    if len(s) == n - 1:
        s += 'xc'[np.random.randint(0, 2)]
    elif len(s) == n + 1:
        s = s[:-1]
    return s

def gen_positions(n):
    ok = False
    while not ok:
        ok = True
        rects = []
        for i in xrange(n):
            a, b = np.random.randint(-350, 350, 2)
            rect = Rect(a, b, 70, 70)
            if rect.collidelist(rects) != -1:
                ok = False
            rects.append(rect)
    return [(r.left, r.top) for r in rects]

pre_trial_dur = 2
study_dur = 0.5
wipe_dur = 0.5
timeout = 120
trials_per_n = 10
blocks = 5


def control_method(proband_id, instructions):
    """
    Generates a control iterable.
    """
    control = []
    for blockn in xrange(blocks):
        for condition in conditions:
            for n in ns:
                for trialn in xrange(trials_per_n):
                    if condition in ['forward_a', 'reverse_a', 'sequence_a']:
                        m = n
                    else:
                        m = 2 * n
                    positions = gen_positions(m)
                    if condition in ['sequence_a',
                                     'sequence_b',
                                     'simultaneous_b']:
                        symbols = gen_symbols(n)
                    else:
                        symbols = 'c' * n
                    trial_info = (
                        proband_id,
                        test_name,
                        condition,
                        blockn,
                        trialn,
                        n,
                        repr(positions),
                        symbols
                    )
                    control.append(trial_info)
    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    _, _, condition, _, trialn, n, positions, symbols = trial_info

    # figure out what the correct responses should be
    if condition in ['forward_a', 'forward_b']:
        correct_order = range(n)
    elif condition in ['reverse_a', 'reverse_b']:
        correct_order = [r for r in reversed(range(n))]
    elif condition in ['sequence_a', 'sequence_b']:
        correct_order = [i for i, v in enumerate(symbols) if v == 'c'] + \
        [i for i, v in enumerate(symbols) if v == 'x']
    else:
        correct_order = None

    if trialn == 0 and n == 2:
        idx = conditions.index(condition)
        keydown = screen.splash(instructions[idx], mouse=True)
        if keydown == 'EXIT':
            return 'EXIT'

    # wipe screen
    screen.wipe(force_hide_mouse=True)

    # display squares
    s = 70
    pos = eval(positions)
    squares = [visual.Rect(x + screen.x0, y + screen.y0, s, s) for x, y in pos]
    [screen.blit_rectangle(rect) for rect in squares]
    screen.update()
    events.wait(pre_trial_dur)

    # play study sequence
    fdic = {
        'c': data.pj(data.VISUAL_PATH, test_name, 'c.png'),
        'x': data.pj(data.VISUAL_PATH, test_name, 'x.png')
    }
    if condition in ['forward_a', 'reverse_a', 'sequence_a']:
        m = n
    else:
        m = 2 * n
    for i in xrange(m):
        square = squares[i]
        if i < n:
            f = fdic[symbols[i]]
            x, y = (square.left + s/9, square.top + s/9)
            _, r = screen.blit_image(f, (x, y), update=False, prc=False)
            if 'simultaneous' not in condition:
                screen.update()
                events.wait(study_dur)
                screen.wipe(r, force_hide_mouse=True, update=False, prc=False)
                screen.update()
                events.wait(wipe_dur)
    if 'simultaneous' in condition:
        screen.update()
        events.wait(pre_trial_dur)
        screen.wipe()
        [screen.blit_rectangle(rect) for rect in squares]
        screen.update()

    # set up response part of trial
    screen.reset_zones()
    screen.create_rect_zones(squares)
    screen.reset_mouse_pos()
    trial_clock = events.Clock()
    trial_clock.tick_busy_loop()
    responses = []
    corcount = 0

    # wait for a responses
    for i in xrange(n):

        # should a circle or an X appear in the clicked square?
        if condition not in ['sequence_a', 'sequence_b', 'simultaneous_b']:
            y = 1
        else:
            y = None

        # record response
        mouse_click = events.wait_for_valid_mouse_click(screen, y)
        if mouse_click == 'EXIT':
            return 'EXIT'
        if condition not in ['sequence_a', 'sequence_b', 'simultaneous_b']:
            j, rt = mouse_click
            button = 1
        else:
            j, rt, button = mouse_click
        keys = {1: 'c', 3: 'x'}
        responses.append((j, rt, keys[button]))

        # check if response is correct
        corr = 0  # assume it's wrong; cuts down the code
        if 'forward' in condition or 'reverse' in condition or 'sequence' in condition:
            if correct_order[i] == j:
                corr = 1
        elif condition == 'simultaneous_a':
            if j in range(n) and j not in [rsp[0] for rsp in responses[:-1]]:
                corr = 1
        else:
            if j in range(n) and j not in [rsp[0] for rsp in responses[:-1]] and symbols[j] == keys[button]:
                corr = 1
                if 'sequence' not in condition:
                    corr = 1
        # correct response
        if corr == 1:
            corcount += 1
            square = squares[j]
            screen.blit_rectangle(square, visual.BLUE, alpha=100)
            screen.update()
            events.wait(0.1)
            screen.wipe(square, update=False, prc=False)
            screen.blit_rectangle(square)
            screen.update()


        # incorrect response
        else:
            break

    # end of trial
    trial_info = tuple(
        list(trial_info) + [
            corr, corcount / float(n), trial_clock.tick_busy_loop(),
            repr(responses)
        ]
    )
    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    dic = {}
    for condition in conditions:
        for n in ns:
            a = '%s_%i' % (condition, n)
            _df = df[(df.condition == condition) & (df.n == n)]
            dic[a + '_ntrials'] = len(_df)
            dic[a + '_ncorrect'] = len(_df[_df.correct == 1])
            dic[a + '_pcorrect'] = len(_df[_df.correct == 1]) - len(_df)
            dic[a + '_pcorrect2'] = _df.pcorrect.mean()
            dic[a + '_rtmean'] = _df[_df.correct == 1].rt.mean()
    stats = summaries.get_universal_stats(data_obj)
    stats += [it for it in dic.iteritems()]
    df = summaries.make_df(stats)
    print '---Here are the summary stats:'
    print df.T

    return df

if __name__ == '__main__':
    batch.run_single_test(test_name)