# -*- coding: utf-8 -*-
"""
switching: Task-switching test

This task-switching test is based on the Cantab attention-switching test [1]
and on the work by Monsell and colleagues [2, 3]. On each trial, the proband
sees a 2-by-2 grid on the screen. There is an arrow in one of the cells of the
grid. If the arrow is in either of the top two cells, the proband indicates its
horizontal position (left or right). If the arrow is in either of the bottom
cells, the proband indicates the direction it is facing (left or right).
The test follows on from Rogers and Monsell's work suggesting that subjects may
handle predictable and unpredictable task switches differently.

There are two main phases to the test. In the 'predictable' phase, the task
switches every two trials. In the 'random' phase, task-switching is
unpredictable. There are 101 trials in each phase, plus eight trials in the
practice phase.

Time taken: ~6 minutes.

Version history:

    1.1     Subjects found the switching colours confusing. Now all the arrows
            are black. 'Position' and 'Direction' are now also written above/
            below the grid.

Summary statistics:

    [switch]_[task]_[cong]_ncorrect : Number of correct trials.
    [switch]_[task]_[cong]_dprime : Sensitivity.
    [switch]_[task]_[cong]_criterion : Bias.
    [switch]_[task]_[cong]_rt_mean : Mean RT in ms.
    [switch]_[task]_[cong]_rt_outrmvd : As above, except any trials <> 3 s.d.
    of mean excluded.

References:

[1] Sahakian, B.J., Morris, R.G., Evenden, J.L., Heald, A., Levy, R., Philpot,
M., Robbins, T.W. (1988). A Comparative Study of Visuospatial Memory and
Learning in Alzheimer-Type Dementia and Parkinson's Disease. Brain, 111(3):
695-718.

[2] Rogers, R. D., & Monsell, S. (1995). Costs of a predictible switch between
simple cognitive tasks. Journal of Experimental Psychology: General, 124(2):
207-231.

[3] Monsell, S. (2003). Task switching. Trends Cogn. Sci., 7(3):134-140.


"""
__version__ = 1.1
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.audio as audio
import charlie.tools.batch as batch

test_name = 'switching'
output_format = [
    ('proband_id', str),
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
    ('rt', int)
]
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
         0, 1, 1, 0, 1, 0, 1, 0, 1]
    )
}
tasks = ['Position', 'Direction']
labels = ['Left', 'Right']
switches = ['Switch', 'Non-switch']


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, task, pos, dir, switch,
    cong, f, ans).
    """
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
            f = ('arrow_%s_%s.png' % (['black', 'black'][t], labels[d])).lower()
            control.append((proband_id, test_name, phase, trialn, tasks[t], 
                           labels[p], labels[d], switch, cong, data.pj(path, f),
                           labels[[p, d][t]]))
    return control
    

def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
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
            
    elif phase == 'predictable':
        if not trialn:
            rsp = screen.splash(instructions[1], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'
            screen.wipe()
            
            screen.countdown_splash(5, instructions[2])
            screen.wipe()

    else:
        if not trialn:
            rsp = screen.splash(instructions[3], mouse=False)
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
    screen.blit_text('Position', (0, -300))
    screen.blit_text('Direction', (0, 100))
    
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


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase != 'practice']
    labels = instructions[-2:]
    signal, noise = labels
    _stats = []

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, 'overall')
    stats += summaries.get_rt_stats(df, 'overall')
    stats += summaries.get_sdt_stats(df, noise, signal, 'overall')

    for phase in df.phase.unique():
        df1 = df[df.phase == phase]
        prefix = '%s' % phase.lower()
        stats += summaries.get_accuracy_stats(df1, prefix)
        stats += summaries.get_rt_stats(df1, prefix)
        stats += summaries.get_sdt_stats(df1, noise, signal, prefix)
        for switch in df['switch'].unique():
            if switch != 'n/a':
                df2 = df1[df['switch'] == switch]
                prefix = '%s_%s' % (phase.lower(), switch.lower())
                print prefix
                stats += summaries.get_accuracy_stats(df2, prefix)
                stats += summaries.get_rt_stats(df2, prefix)
                stats += summaries.get_sdt_stats(df2, noise, signal, prefix)

    for cong in df.cong.unique():
        prefix = '%s' % cong.lower()
        df1 = df[df.cong == cong]
        _stats += summaries.get_accuracy_stats(df1, prefix)
        _stats += summaries.get_rt_stats(df1, prefix)
        _stats += summaries.get_sdt_stats(df1, noise, signal, prefix)
    _df = summaries.make_df(_stats)
    for dv in ['ncorrect', 'dprime', 'rt_mean_outrmvd']:
        x = 'stroop_%s' %dv
        y = float(_df['congruent_%s' % dv] - _df['incongruent_%s' % dv])
        stats.append((x, y))

    _df = summaries.make_df(stats)
    for phase in df.phase.unique():
        if phase != 'practice':
            for dv in ['ncorrect', 'dprime', 'rt_mean_outrmvd']:
                x = 'cost_%s_%s' %(phase, dv)
                y = float(_df['%s_switch_%s' % (phase, dv)] - _df[
                    '%s_non-switch_%s' % (phase, dv)])
                stats.append((x, y))

    df = summaries.make_df(stats)
    # print '---Here are the summary stats:'
    # print df.T
    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)