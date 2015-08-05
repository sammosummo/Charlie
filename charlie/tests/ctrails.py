# -*- coding: utf-8 -*-
"""
cTrails: Computerised trail-making test.

In this task, the proband must click on circles drawn on the screen in a
specified order, making a 'trail' between them. There are a total of six trials
in the test, distributed over three phases. In the first phase, the proband
draws trails between consecutive numbers, starting with 1. In the second phase,
the proband does the same with letters starting with a. In the third phase, the
proband alternates between numbers and letters. Each phase contains a practice
trial with 8 circles, and test trial with 25 circles.

The traditional trail-making test [1, 2] contains only two phases (equivalent
to the 'number' and 'number-letter' phases in the present version). The
traditional test is also done with pen and paper, and requires an experienced
experimenter to administer it. Thus the current version should be more
convenient than the traditional test.

Please note that this test has not yet been verified against the pen-and-paper
trail-making test. However, preliminary data from our study suggests that they
are correlated.

Time required: ~4 min

Version history:

    1.1     To be more consistent with the original TMT, the present version
            has 25 circles per test trial.

            During pilot testing, one subject clicked the same (incorrect)
            circle over and over, racking up a large number of errors. Now the
            total number of errors and the total number of unique errors are
            recorded separately. The latter statistic is probably better.

            Audio feedback on incorrect responses.

Summary statistics:

    [phase]_* : number, letter, or number-letter

    *nerrors : number of errors
    *nuniqueerrors : number of unique errors
    *time : total time taken to complete the trial

References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept Mot Skills, 8:271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and
B of the Trail Making Test. J Clin Psychol, 43(4):402–409.

"""
__version__ = 1.1
__author__ = 'Sam Mathias'


import pandas
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch
import charlie.tools.audio as audio


test_name = 'ctrails'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('phase', str),
                 ('trial_type', str),
                 ('n', int),
                 ('rsp', str),
                 ('corr', str),
                 ('rt', int),
                 ('total_time', int)]

phases = ('number', 'letter', 'number-letter')
trial_types = ('practice', 'test')

positions = {
'number': {
'practice': ((-238, -111), (387, 60), (347, -269), (135, -157),
             (34, -360),  (-227, 17),  (130, 122),  (400, 320)),
'test': ((-264, -59),    (257, 205),  (-156, 238),  (90, -144), (370, -146),
         (205, -348),  (-209, -253), (-358, -211),  (-43, -37), (122, -264),
         (-176, -359), (-139, -185),    (170, 12),    (400, 0),   (396, 88),
         (347, 316),      (-5, 172),   (138, -67), (-11, -165), (211, -216),
         (400, -300),    (250, -46),  (-200, 101),  (237, 103),   (35, 329)
         )
    },
'letter': {
'practice': ((-285, -22), (-44, 131), (-291, 138), (26, -219),
             (261, 41), (-324, -200), (258, -342), (191, 353)),
'test': ((344, 272),  (-58, 254), (-353, -329),  (243, -172),  (150, -400),
         (300, -309), (380, -18),  (-387, -47), (-186, -385), (-189, -153),
         (361, 125), (-311, 104),  (-231, 247),  (-71, -192),   (92, -310),
         (298, -88),   (-77, 36),     (98, 73),   (244, 187),    (33, 169),
         (146, 341), (-136, 336),  (-147, 201), (-294, -102),  (-33, -313)
         )
    },
'number-letter': {
'practice': ((337, 13),    (-345, -3),  (396, 280),  (-365, 118),
             (86, -231), (-306, -275), (366, -125), (-165, -131)),
'test': ((-316, -140), (-385, 6), (-387, -346), (296, -328),   (303, -57),
         (308, 252),   (361, 23),    (127, 30), (-266, -64),  (-166, -64),
         (193, -217), (-88, 123),   (178, 213), (353, -240),  (-27, -399),
         (-65, -228), (-248, 58),   (-33, 270), (-371, 180), (-205, -274),
         (60, -276),  (-132, 28),    (76, 101),   (91, 346),  (-126, 345)
         )
    }
}

_d = range(1, 26)
_l = 'abcdefghijklmnopqrstuvwxy'

sequences = {
'number': {'practice': _d[:8], 'test': _d},
'letter': {'practice': list(_l[:8]), 'test': list(_l)},
'number-letter': {
    'practice': [i for l in zip(_d, _l)[:4] for i in l],
    'test': [i for l in zip(_d, _l)[:12] for i in l] + [13]
    }
}


def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, this is a list of tuples in
    the format (proband_id, test_name, phase, trial_type).
    """
    return [(proband_id, test_name, p, t) for p in phases for t in trial_types]


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """
    _, _, phase, trial_type = trial_info

    # gather correct instructions from the instructions list
    ix = phases.index(phase)
    instructions = instructions[ix * 3 : ix * 3 + 3]
    if trial_type == 'test':
        _ = instructions.pop(0)
    del _
    
    # show initial instructions
    keydown = screen.splash(instructions.pop(0), mouse=True)
    if keydown == 'EXIT':
        return 'EXIT'
    screen.wipe()
    
    # set up countdown
    if trial_type == 'test':
        screen.countdown_splash(5, instructions.pop(0))

    # set up trial
    trial_clock = events.Clock()
    trial_clock.tick_busy_loop()
    path = data.pj(data.VISUAL_PATH, test_name)
    filename = lambda x: data.pj(path, 'a_%s.png' % str(x))
    pos = positions[phase][trial_type]
    sequence = sequences[phase][trial_type]
    screen.wipe(update=False)
    screen.reset_zones()
    zones = []
    for item, position in zip(sequence, pos):
        image, r = screen.blit_image(filename(item), position, update=False)
        zones.append(r)
    screen.create_rect_zones(zones)
    screen.flip()
    all_responses = []
    all_rts = []
    remaining_responses = list(sequence)
    clicked_zones = []
    
    # trial loop
    screen.reset_mouse_pos()
    while remaining_responses:
    
        mouse_click = events.wait_for_valid_mouse_click(screen, 1)
        
        if mouse_click == 'EXIT':
            return 'EXIT'
        else:
            r, rt = mouse_click
        
        response = sequence[r]
        
        if response is remaining_responses[0]:
            remaining_responses.pop(0)
            clicked_zones.append(zones[r])
            
            if len(clicked_zones) > 1:
                
                # draw a trail
                screen.blit_line(clicked_zones[-2], clicked_zones[-1], 10)
            
            else:
                # draw a tick
                x1, y1 = clicked_zones[-1].center
                x0, y0 = x1 - 10, y1 - 20
                x2, y2 = x1 + 20, y1 - 50
                screen.blit_line((x0, y0), (x1, y1), 10, prc=False)
                screen.blit_line((x1, y1), (x2, y2), 10, prc=False)
            
            screen.update()

        else:
            audio.play_feedback(False)
        
        # record response
        response = sequence[r]
        all_responses.append(response)
        all_rts.append(rt)       
        
    # trial over; consolidate data
    total_time = trial_clock.tick_busy_loop()
    data_from_this_trial = []
    remaining_responses = list(sequence)
    
    for i, response, rt in zip(xrange(len(all_rts)), all_responses, all_rts):
        
        t = list(trial_info) + [i, response]
        if response is remaining_responses[0]:
            t.append('Correct')
            remaining_responses.pop(0)
        else:
            t.append('Incorrect')
        t += [rt, total_time]
        t = tuple(t)
        
        data_from_this_trial.append(t)
    
    return data_from_this_trial


def summary_method(data_obj, _):
    """
    Computes summary stats for the ctrails task.
    """
    df = data_obj.to_df()
    df = df[df.trial_type == 'test']

    stats = summaries.get_universal_stats(data_obj)
    for phase in df.phase.unique():

        _df = df[df.phase == phase]
        _errors = _df[_df['corr'] != 'Correct']
        stats += [('%s_nerrors' % phase, len(_errors))]
        _ue = _errors.rsp.unique()
        stats += [('%s_nuniqueerrors' % phase, len(_ue))]
        stats += [('%s_time' % phase, _df.total_time.tolist()[0])]

    df = summaries.make_df(stats)
    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)