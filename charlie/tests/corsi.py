"""
corsi: Tests of spatial memory span.

This is test shares some similarities with the original Corsi test [1]. On each
trial, the proband sees several randomly distributed non-overlapping squares
for 2 seconds. During the study period, circles or crosses appear in the
squares, and during the test period, the proband clicks on the squares that
contained the circles. There are three portions to the test. During the
'simultaneous' portion, all circles appear in the sqaures at once, and the
proband must report all of them, in any order. During the 'forward' portion,
the circles appear one by one, and the proband must report them in the correct
order. During the 'sequence' portion, circles and crosses appear in the
squares, and the proband must report the circles in order, then the squares in
order. Each portion contains practice and test trials. The number of circles/
crosses per trial starts at 2, and increases by 1 every three trials, up to
a maximum of 9. There are always twice as many squares as circles/crosses in a
trial.

Previous work has generally concluded that the reverse-reporting version of the
Corsi produces the same results as the forward-reporting version [2]. I found
the same thing when conducting pilot testing here. The three versions included
in the present version produced very different scores, with simultaneous being
the easiest and seqeunce being the most difficult.

Summary statistics:

    [portion]_* : simulaneous, forward, or sequence

    *ntrials : number of trials.
    *ncorrect : number of correct trials.
    *k : trial with largest number of circles/crosses correctly reported.
    *rt_mean : mean response time on correct trials in milliseconds.
    *rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    *rt_outrmvd : number of outlier trials.

References:

[1] Corsi P.M. (1972). Human memory and the medial temporal region of the
brain. Dis Abstr Intl, 34, 891B.

[2] Berch D.B., Krikorian R., & Huha E.M. (1998). The Corsi block-tapping task:
Methodological and theoretical considerations. Brain Cogn, 38, 317–338.

"""
__version__ = 1.0
__author__ = 'smathias'


import pandas
from pygame import Rect
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
import charlie.tools.audio as audio
import charlie.tools.visual as visual
import charlie.tools.events as events


test_name = 'corsi'
output_format = [('proband_id', str),
                 ('test_name', str),
                 ('portion', str),
                 ('phase', str),
                 ('trialn', str),
                 ('n', int),
                 ('positions', str),
                 ('symbols', str),
                 ('correct', int),
                 ('rt', int),
                 ('responses', str)]
conditions = [
    'simultaneous',
    'forward',
    'sequence',
]
ns = range(2, 10)
pre_trial_dur = 2
study_dur = 0.5
wipe_dur = 0.5
timeout = 120
trials_per_n = 3


from itertools import repeat
import random
import numpy as np

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