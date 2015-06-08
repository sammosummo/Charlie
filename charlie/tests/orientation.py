# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

orientation: Orientation test.

This test is designed to be administered first in any battery. The proband sees
either a blue square (during the first 10 trials) or a blue square and a red
circle (during the last 10 trials) positioned randomly on the screen. The task
is to click on the blue square as quickly as possible. After each trial the
blue square becomes smaller and the red square becomes larger. It is similar to
the mouse practice task from [1].

Summary statistics:

    phase_1_time : time taken to complete the first 10 trials
    phase_2_time : time taken to complete the last 10 trials
    difference : difference in time between the two phases
    phase_2_errors : number of error clicks in the final 10 trials

References:

[1] Gur, R.C., Ragland, D., Moberg, P.J., Turner, T.H., Bilker, W.B., Kohler,
C., Siegel, S.J., & Gur, R.E. (2001). Computerized neurocognitive scanning: I.
Methodology and validation in healthy people. Neuropsychopharmacology, 25:766-
776.

"""

__version__ = 1.0
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch

test_name = 'orientation'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', str),
    ('posx', int),
    ('posy', int),
    ('dposx', int),
    ('dposy', int),
    ('rsp', int),
    ('rt', int),
    ('total_time', int)
]
phases = ('first', 'last')
positions = [
    (44, -336),
    (291, -190),
    (174, 158),
    (249, -155),
    (144, 171),
    (292, -24),
    (-136, -184),
    (-314, -191),
    (76, 54),
    (-192, 168),
    (-31, -224),
    (-273, -68),
    (178, 207),
    (40, -55),
    (-241, -116),
    (-95, -43),
    (287, 199),
    (124, 321),
    (-123, 133),
    (138, 284)
]
dist_positions = [
    (310, -249),
    (-198, -147),
    (-163, 283),
    (260, 315),
    (-346, -300),
    (174, -307),
    (209, -166),
    (-282, 128),
    (124, -343),
    (233, 131)
]


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, this is a list of tuples in
    the format (proband_id, test_name, phase). The trial_method is only called
    once per phase.
    """
    return [(proband_id, test_name, phase) for phase in phases]


def trial_method(screen, instructions, trial_info):
    """
    Runs a phase of the test. All the trials within a phase are looped within
    this function.
    """
    proband_id, test_name, phase = trial_info

    if phase == 'first':
        keydown = screen.splash(instructions[0], mouse=True)
        pos = positions[:10]
        if keydown == 'EXIT':
            return 'EXIT'
        screen.countdown_splash(5, instructions[1])
    else:
        pos = positions[10:]
    screen.wipe()

    trial_data = []

    path = data.pj(data.VISUAL_PATH, test_name)
    f1 = lambda x: data.pj(path, '%s_s.png' % str(x))
    f2 = lambda x: data.pj(path, '%s_c.png' % str(9 - x))

    trial_clock = events.Clock()
    total_time = trial_clock.tick_busy_loop()

    trialn = -1
    size = -1

    for x, y in pos:

        dpos = dist_positions[trialn]
        trialn += 1
        size += 1
        screen.wipe(update=False)
        screen.reset_zones()
        zones = []
        image, r = screen.blit_image(f1(trialn), (x, y), update=False)
        zones.append(r)
        if phase == 'last':
            image, r = screen.blit_image(f2(trialn), dpos, update=False)
            zones.append(r)
        screen.create_rect_zones(zones)
        screen.flip()

        clicked = False

        while not clicked:
            mouse_click = events.wait_for_valid_mouse_click(screen, 1)
            if mouse_click == 'EXIT':
                return 'EXIT'
            else:
                r, rt = mouse_click

            total_time += trial_clock.tick_busy_loop()
            t = (proband_id, test_name, phase, size, x, y, dpos[0], dpos[1], r,
                rt, total_time)
            trial_data.append(t)

            if r == 0:
                clicked = True
    print trial_data
    return trial_data


def summary_method(data_obj, instructions):
    """
    Computes summary stats for the trails task.
    """
    df = data_obj.to_df()
    stats = summaries.get_universal_stats(data_obj)

    df1 = df[df.phase == 'first']
    phase_1_time = float(df1.total_time.max())
    df1 = df[df.phase == 'last']
    phase_2_time = float(df1.total_time.max())
    difference = phase_2_time - phase_1_time
    errors = len(df[df.rsp == 1])

    stats += [
        ('phase_1_time', phase_1_time),
        ('phase_2_time', phase_2_time),
        ('difference', difference),
        ('errors', errors)
    ]
    
    df = summaries.make_df(stats)
    # print '---Here are the summary stats:'
    # print df.T
    return df


def main():
    """
    Run this test.
    """
    batch.run_a_test(test_name)


if __name__ == '__main__':
    batch.run_single_test(test_name)