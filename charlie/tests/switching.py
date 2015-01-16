# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

switching: Task-switching test

This task-switching test is based on the Cantab Attention-switching test and
on the work of Monsell and colleagues. On each trial, the proband sees a 2-by-2
grid on the screen. There is an arrow in one of the cells of the grid. If the
arrow is in either of the top two cells, the proband indicates its horizontal
position (left or right). If the arrow is in either of the bottom cells, the
proband responds with the direction it is facing (left or right). The arrows
are also coloured differently (blue for position, red for direction). The test
follows on from Rogers and Monsell's work suggesting that subjects may handle
predictable and unpredictable task switches differently, and improves on the
Cantab, by removing the reliance on on-screen written instructions.

There are two main phases to the test. In the 'predictable' phase, the task
switches every two trials. In the 'random' phase, task-switching is
unpredictable. There are 101 trials in each phase, plus eight trials in the
practice phase. Numerous summary statistics are recorded, including accuracy
and response times for predictable and random switch and non-swtich trials,
position and direction tasks, and congruent and incongruent trials (in terms of
position and direction of the arrow).

Reference:

Rogers, R. D., & Monsell, S. (1995). Costs of a predictible switch between
simple cognitive tasks. Journal of Experimental Psychology: General, 124(2):
207-231.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.audio as audio

test_name = 'switching'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('phase', str),
                 ('trialn', int),
                 ('task', str),
                 ('pos', str),
                 ('dir', str),
                 ('switch', str),
                 ('cong', str),
                 ('f', str),
                 ('ans', str),
                 ('rsp', str),
                 ('rt', int)]

answers = {
    'practice': (
        [0, 0, 1, 1, 0, 0, 1, 1, 0],  # task, 0=position
        [0, 0, 0, 1, 1, 1, 0, 1, 0],  # position, 0=left
        [1, 1, 1, 0, 1, 0, 0, 0, 0]  # direction, 0=left
        ),  
    'predictable': (
        [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1,
         1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0,
         1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0,
         0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1,
         0, 0, 1, 1, 0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1,
         1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1,
         1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0,
         1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0,
         0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0,
         0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0,
         0, 1, 0, 0, 0, 1, 0, 1, 0]
         ),
    'random': (
        [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0,
         1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,
         0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1,
         1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0,
         1, 0, 1, 1, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1,
         1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1,
         0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0,
         1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1,
         0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1,
         0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0,
         0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0,
         0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0,
         0, 1, 1, 0, 1, 0, 1, 0, 1])
    }
tasks = ['Position', 'Direction']
labels = ['Left', 'Right']
switches = ['Switch', 'Non-switch']


def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, task, pos, dir, switch,
    cong, f, ans)."""
    path = data.pj(data.VISUAL_PATH, test_name)
    control = []
    for phase in ['practice', 'predictable', 'random']:
        task, position, direction = answers[phase]
        for trialn in xrange(len(task)):
            t, p, d = task[trialn], position[trialn], direction[trialn]
            if trialn == 0:
                switch = 'n/a'
            else:
                switch = switches[t == task[trialn - 1]]
            cong = ['Incongruent', 'Congruent'][p == d]
            f = ('arrow_%s_%s.png' % (['blue', 'red'][t], labels[d])).lower()
            control.append((proband_id, test_name, phase, trialn, tasks[t], 
                           labels[p], labels[d], switch, cong, data.pj(path, f),
                           labels[[p, d][t]]))
    return control
    

def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""   
    _, _, phase, trialn, task, position, direction, _, _, f, ans = trial_info
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
            screen.wipe()
    
    # set up trial
    grid_rects = [visual.Rect(0, 0, 150, 150) for i in xrange(4)]
    grid_rects[0].bottomright = screen.x0, screen.y0 - 100
    grid_rects[1].bottomleft = screen.x0, screen.y0 - 100
    grid_rects[2].topright = screen.x0, screen.y0 - 100
    grid_rects[3].topleft = screen.x0, screen.y0 - 100
    [screen.blit_rectangle(rect) for rect in grid_rects]
    
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l', 'r'), ('', ''))
    
    img = screen.images[f]
    if task == 'Position' and position == 'Left':
        img_pos = (-75, -75 - 100)
    elif task == 'Position' and position == 'Right':
        img_pos = (75, -75 - 100)
    elif task == 'Direction' and position == 'Left':
        img_pos = (-75, 75 - 100)
    elif task == 'Direction' and position == 'Right':
        img_pos = (75, 75 - 100)
    
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
    if phase != 'practice':
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


def summary_method(data, instructions):
    """Computes summary stats for this task. Collects the trial-by-trial
    data by calling the to_df() method from the data object, filters out the
    practice trials, gets universal entries, generates a condition set, then
    summary stats are produced for each combination of levels from the
    condition set."""
    df = data.to_df()
    df = df[df.phase != 'practice']
    cols, entries = summaries.get_universal_entries(data)
    
    condition_set = (('phase', ['predictable', 'random', 'all']),
                     ('task', tasks + ['all']),
                     ('switch', switches + ['all']),
                     ('cong', ['Incongruent', 'Congruent', 'all']))
    
    a, b = summaries.get_all_combinations_2alt(df, condition_set, labels)
    cols += a
    entries += b
    dfsum = pandas.DataFrame(entries, cols).T
    
    dvs = ['pcorrect', 'rau(pcorrect)', 'd', 'rt_mean_outrmvd']
    a, b = summaries.differences(dfsum,
                                       'predictable_all_switch_all',
                                       'predictable_all_non-switch_all',
                                       dvs)
    cols += a
    entries += b
    a, b = summaries.differences(dfsum,
                                       'random_all_switch_all',
                                       'random_all_non-switch_all',
                                       dvs)
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