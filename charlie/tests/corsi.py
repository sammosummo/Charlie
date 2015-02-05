# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

corsi: Test of spatial working memory span

This test is based on the Corsi blocks test [1]. There are three phases to the
test. On trials in the first phase, the proband sees a grid on the screen.
After a  moment, between 2 and 12 circles will appear in the grid, and then
disappear. The proband must click on the cells that contained the circles.
Starting with 2, the number of circles increases every two trials. The grid is
initially 4-by-4, but expands to ensure that the number of blank squares always
outnumber those with circles by at least 1.

Trials in the second phase are identical to those in the first phase except
that the circles appear one at a time rather than all together, and probands
are required to reproduce the sequence in the correct order. A stopping rule
is applied whereby the phase is terminated if the subject makes more than

If the proband makes
any errors

was devised for an fMRI study by Leung et al [1]. On each trial, the
proband sees a 4-by-4 grid. One of the cells in the grid contains a circle. The
grid is then replaced by a 6-s sequence of arrows or dashes, that instruct the
proband how the circle moves within the grid. The sequence is followed by an
empty grid. The task is to click on the cell in which the circle ended up. The
independent variable is the number of updates made during the retention period
(0 up to 12). There are three trials at each level. The test ends prematurely
if the proband gets all three trials of a level incorrect.

Summary statistics:

    ntrials : number of trials completed
    ncorrect : number of trials correct
    pcorrect : proportion of trial correct

References:

[1] Leung, H.C., Oh, H., Ferri, J., & Yi, Y. (2007). Load response functions in
the human spatial working memory circuit during location memory updating.
Neuroimage, 35: 368-377.

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


test_name = 'updating'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('updates', int),
    ('origin', int),
    ('endpoint', int),
    ('moves', str),
    ('marginalpositions', str),
    ('rsp', int),
    ('rt', int)
]

study_duration = 4
wipe_period = 0.5
update_duration = 0.5


trial_details = [
('prac', 0,  0,  4,  4,  '------------', '4,4,4,4,4,4,4,4,4,4,4,4,4'),
('prac', 1,  1,  8,  12, '-----------d', '8,8,8,8,8,8,8,8,8,8,8,8,12'),
('prac', 2,  2,  9,  6,  '-----u-----r', '9,9,9,9,9,9,5,5,5,5,5,5,6'),
('test', 0,  0,  13, 13, '------------', '13,13,13,13,13,13,13,13,13,13,13,13,13'),
('test', 1,  0,  15, 15, '------------', '15,15,15,15,15,15,15,15,15,15,15,15,15'),
('test', 2,  0,  13, 13, '------------', '13,13,13,13,13,13,13,13,13,13,13,13,13'),
('test', 3,  1,  3,  2,  '-----------l', '3,3,3,3,3,3,3,3,3,3,3,3,2'),
('test', 4,  1,  1,  2,  '-----------r', '1,1,1,1,1,1,1,1,1,1,1,1,2'),
('test', 5,  1,  0,  4,  '-----------d', '0,0,0,0,0,0,0,0,0,0,0,0,4'),
('test', 6,  2,  5,  2,  '-----u-----r', '5,5,5,5,5,5,1,1,1,1,1,1,2'),
('test', 7,  2,  13, 8,  '-----l-----u', '13,13,13,13,13,13,12,12,12,12,12,12,8'),
('test', 8,  2,  7,  2,  '-----l-----u', '7,7,7,7,7,7,6,6,6,6,6,6,2'),
('test', 9,  3,  6,  15, '---d---d---r', '6,6,6,6,10,10,10,10,14,14,14,14,15'),
('test', 10, 3,  15, 11, '---l---r---u', '15,15,15,15,14,14,14,14,15,15,15,15,11'),
('test', 11, 3,  10, 6,  '---l---r---u', '10,10,10,10,9,9,9,9,10,10,10,10,6'),
('test', 12, 4,  13, 15, '--u--d--r--r', '13,13,13,9,9,9,13,13,13,14,14,14,15'),
('test', 13, 4,  3,  6,  '--d--u--d--l', '3,3,3,7,7,7,3,3,3,7,7,7,6'),
('test', 14, 4,  0,  5,  '--d--u--d--r', '0,0,0,4,4,4,0,0,0,4,4,4,5'),
('test', 15, 6,  14, 11, '-r-u-d-u-u-d', '14,14,15,15,11,11,15,15,11,11,7,7,11'),
('test', 16, 6,  0,  10, '-d-d-d-r-r-u', '0,0,4,4,8,8,12,12,13,13,14,14,10'),
('test', 17, 6,  1,  9,  '-d-d-d-r-u-l', '1,1,5,5,9,9,13,13,14,14,10,10,9'),
('test', 18, 8,  10, 7,  '-lu-lu-rr-dr', '10,10,9,5,5,4,0,0,1,2,2,6,7'),
('test', 19, 8,  14, 9,  '-rl-rl-ul-lr', '14,14,15,14,14,15,14,14,10,9,9,8,9'),
('test', 20, 8,  3,  1,  '-ld-rd-uu-ll', '3,3,2,6,6,7,11,11,7,3,3,2,1'),
('test', 21, 9,  5,  4,  '-udd-ldr-luu', '5,5,1,5,9,9,8,12,13,13,12,8,4'),
('test', 22, 9,  3,  0,  '-dll-rrl-llu', '3,3,7,6,5,5,6,7,6,6,5,4,0'),
('test', 23, 9,  10, 9,  '-dur-udl-dul', '10,10,14,10,11,11,7,11,10,10,14,10,9'),
('test', 24, 12, 1, 12,  'drududdldlrl', '1,5,6,2,6,2,6,10,9,13,12,13,12'),
('test', 25, 12, 12, 9,  'rluuurrlldrd', '12,13,12,8,4,0,1,2,1,0,4,5,9'),
('test', 26, 12, 11, 6,  'llrruddudluu', '11,10,9,10,11,7,11,15,11,15,14,10,6')]

"""
# The following is for generating new trials. Don't use!-----------------------
#updates = [0, 1, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3,
#           4, 4, 4, 6, 6, 6, 8, 8, 8, 9, 9, 9, 12, 12, 12]
#updates_dic = {0:  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#               1:  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#               2:  [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
#               3:  [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
#               4:  [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
#               6:  [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
#               8:  [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1],
#               9:  [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
#               12: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
#def calc_moves(nmoves):
#
#    done = False
#    while not done:
#        origin = np.random.randint(16)
#        directions = ['u', 'd', 'l', 'r']
#        blocked_moves = {0: ['u', 'l'], 1: ['u'], 2: ['u'],
#                         3: ['u', 'r'], 4: ['l'], 5: [], 6: [],
#                         7: ['r'], 8: ['l'], 9: [], 10: [], 11: ['r'],
#                         12: ['d', 'l'], 13: ['d'], 14: ['d'],
#                         15: ['d', 'r']}
#        moves = {'u': lambda x: x - 4, 'd': lambda x: x + 4,
#                 'l': lambda x: x - 1, 'r': lambda x: x + 1}
#        move_list = []
#        positions = [origin]
#        for i, m in enumerate(nmoves):
#            prev_pos = positions[i]
#            if m:
#                valid = False
#                while not valid:
#                    d = directions[np.random.randint(4)]
#                    if d not in blocked_moves[prev_pos]:
#                        valid = True
#                        move_list.append(d)
#                        positions.append(moves[d](prev_pos))
#            else:
#                move_list.append('-')
#                positions.append(prev_pos)
#        endpoint = positions[-1]
#        if not any(nmoves):
#            done = True
#        elif origin != endpoint:
#            done=True
#    mv = ''.join(move_list)
#    ps = ','.join(str(p) for p in positions)
#    return origin, endpoint, mv, ps
#
#
#for u in updates:
#    print calc_moves(updates_dic[u])
#------------------------------------------------------------------------------
"""


def control_method(proband_id, instructions):
    """Generates a control iterable."""
    return [tuple([proband_id, test_name] + list(trial)) for trial in \
    trial_details]


def set_up_grid(screen, imgf, pos=None):
    """
    Draw a 4x4 grid on the screen, optionally placing a circle in one of the
    cells.
    """
    screen.reset_zones()
    s = 100
    grid_rects = [visual.Rect(0, 0, s, s) for i in xrange(16)]
    grid_rects[0].bottomright = (screen.x0 - s, screen.y0 - s)
    grid_rects[1].bottomright = (screen.x0,     screen.y0 - s)
    grid_rects[2].bottomleft  = (screen.x0,     screen.y0 - s)
    grid_rects[3].bottomleft  = (screen.x0 + s, screen.y0 - s)
    grid_rects[4].bottomright = (screen.x0 - s, screen.y0)
    grid_rects[5].bottomright = (screen.x0,     screen.y0)
    grid_rects[6].bottomleft  = (screen.x0,     screen.y0)
    grid_rects[7].bottomleft  = (screen.x0 + s, screen.y0)
    grid_rects[8].topright    = (screen.x0 - s, screen.y0)
    grid_rects[9].topright    = (screen.x0,     screen.y0)
    grid_rects[10].topleft    = (screen.x0,     screen.y0)
    grid_rects[11].topleft    = (screen.x0 + s, screen.y0)
    grid_rects[12].topright  = (screen.x0 - s, screen.y0 + s)
    grid_rects[13].topright  = (screen.x0,     screen.y0 + s)
    grid_rects[14].topleft   = (screen.x0,     screen.y0 + s)
    grid_rects[15].topleft   = (screen.x0 + s, screen.y0 + s)
    screen.create_rect_zones(grid_rects)
    [screen.blit_rectangle(rect) for rect in grid_rects]
    if pos is None:
        screen.update()
        return None
    else:
        t = s / 2
        if pos in [0, 4, 8, 12]:
            x = - s - t
        if pos in [1, 5, 9, 13]:
            x = - t
        if pos in [2, 6, 10, 14]:
            x = t
        if pos in [3, 7, 11, 15]:
            x = s + t
        if pos in [0, 1, 2, 3]:
            y = - s - t
        if pos in [4, 5, 6, 7]:
            y = - t
        if pos in [8, 9, 10, 11]:
            y = t
        if pos in [12, 13, 14, 15]:
            y = s + t
        screen.blit_image(imgf, (x, y), update=False)
        screen.update()


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""
    _, _, phase, trialn, updates, origin, endpoint, moves, _ = trial_info
    imgf = data.pj(data.VISUAL_PATH, test_name, 'circle.png')

    # show instructions if first trial
    if phase == 'prac':
        phase = 'practice'  # correct silly typo in trial_details
        if not trialn:
            rsp = screen.splash(instructions[0], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'

    else:
        if not trialn:
            rsp = screen.splash(instructions[1], mouse=False)
            if rsp == 'EXIT':
                return 'EXIT'

    screen.wipe()

    # display study stimulus, show moves, show response grid
    set_up_grid(screen, imgf, origin)
    events.wait(study_duration)
    screen.wipe()
    events.wait(wipe_period)
    for move in moves.replace('-', 'a'):
        screen.wipe()
        f = data.pj(data.VISUAL_PATH, test_name, move + '.png')
        screen.blit_image(f, (0, 0), update=False)
        screen.update()
        events.wait(update_duration)
        screen.wipe()
        screen.update()
        events.wait(update_duration)
    screen.wipe()
    screen.update()
    events.wait(wipe_period)
    set_up_grid(screen, imgf, None)

    # wait for a response
    mouse_click = events.wait_for_valid_mouse_click(screen, 1)
    if mouse_click == 'EXIT':
        return 'EXIT'
    i, rt = mouse_click

    # show response
    if phase == 'practice':
        set_up_grid(screen, imgf, endpoint)
        corr = endpoint == i
        colour = [visual.RED, visual.GREEN][corr]
        screen.blit_rectangle(screen.zones[i], colour, alpha=100)
        screen.update()
        audio.play_feedback(corr)
        events.wait(events.DEFAULT_ITI_FEEDBACK)
    else:
        screen.blit_rectangle(screen.zones[i], visual.BLUE, alpha=100)
        events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    trial_info = tuple(list(trial_info) + [i, rt])
    return trial_info

timeout = 120


def stopping_rule(data):
    """
    Returns True if all three of the trials of a given moves length were
    incorrect.
    """
    print ''
    df = data.to_df()
    df = df[df.phase == 'test']
    if len(df) > 0:
        df = df.set_index('trialn', drop=False)
        last = df.ix[len(df) - 1].updates
        df = df[df['updates'] == last]
        if len(df) == 3:
            print 'checking ...'
            if len(df[df.endpoint == df.rsp]) == 0:
                return True


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '', ans_col='endpoint')

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





