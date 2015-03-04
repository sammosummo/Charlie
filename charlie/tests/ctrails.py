# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 11:06:45 2014

cTrails: Computerised trail-making test.

In this task, the proband must click on circles drawn on the screen in a
specified order, making a 'trail' between them. There are a total of six trials
in the test, distributed over three phases. In the first phase, the proband
draws trails between consequtive numbers starting from 1. In the second, the
proband does the same with letters starting from a. In the third, the proband
alternates between numbers and letters. Each phase contains a practice trial
with 8 cirles, and test trial with 25 circles.

The traditional trail-making test contains only two phases (parts A and B,
equivalent to 'number' and 'number-letter' phases in the present version). The
traditional test is also done with pen and paper, and requires an experienced
experimenter to administer it. Thus the current version should be more
convenient than the traditional test.

Summary statistics include total response times and number of errors per trial,
and response-time differences between trials.

Please note that this test has not been compared or verified with the pen-and-
paper trail-making test. It is unknown how performance on the two tests relate
to one another.

Time taken by me to complete: 3 min.

Useful references:

Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and B
of the Trail Making Test. J Clin Psychol, 43(4):402–409.

Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept Mot Skills, 8:271-276.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries

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
         (400, -300),    (250, -46),  (-200, 101),  (237, 103),   (35, 329),
                                                                (300, -329))
    },
'letter': {
'practice': ((-285, -22), (-44, 131), (-291, 138), (26, -219),
             (261, 41), (-324, -200), (258, -342), (191, 353)),
'test': ((344, 272),  (-58, 254), (-353, -329),  (243, -172),  (150, -400),
         (300, -309), (380, -18),  (-387, -47), (-186, -385), (-189, -153),
         (361, 125), (-311, 104),  (-231, 247),  (-71, -192),   (92, -310),
         (298, -88),   (-77, 36),     (98, 73),   (244, 187),    (33, 169),
         (146, 341), (-136, 336),  (-147, 201), (-294, -102),  (-33, -313), 
                                                                (80, -113))
    },
'number-letter': {
'practice': ((337, 13),    (-345, -3),  (396, 280),  (-365, 118),
             (86, -231), (-306, -275), (366, -125), (-165, -131)),
'test': ((-316, -140), (-385, 6), (-387, -346), (296, -328),   (303, -57),
         (308, 252),   (361, 23),    (127, 30), (-266, -64),  (-166, -64),
         (193, -217), (-88, 123),   (178, 213), (353, -240),  (-27, -399),
         (-65, -228), (-248, 58),   (-33, 270), (-371, 180), (-205, -274),
         (60, -276),  (-132, 28),    (76, 101),   (91, 346),  (-126, 345),
                                                              (-400, 366))
    }
}

_d = range(1, 27)
_l = 'abcdefghijklmnopqrstuvwxyz'

sequences = {
'number': {'practice': _d[:8], 'test': _d},
'letter': {'practice': list(_l[:8]), 'test': list(_l)},
'number-letter': {
    'practice': [i for l in zip(_d, _l)[:4] for i in l],
    'test': [i for l in zip(_d, _l)[:13] for i in l]
    }
}


def control_method(proband_id, instructions):
    """Generates a control iterable. For this test, this is a list of tuples in
    the format (proband_id, test_name, phase, trial_type)."""
    return [(proband_id, test_name, p, t) for p in phases for t in trial_types]


def trial_method(screen, instructions, trial_info):
    """Runs a single trial of the test."""
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


def summary_method(data, instructions):
    """Computes summary stats for the trails task."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)

    df = df[df.trial_type == 'test']
    
    for phase in df.phase.unique():
        cols += ['%s_nerrors' % phase, '%s_total_time' % phase]
        subdf = df[df.phase == phase]
        entries.append(len(subdf) - len(subdf[subdf['corr'] == 'Correct']))
        entries.append(list(subdf['total_time'])[0])
    
    cols += ['letter_minus_number_time',
             'number-letter_minus_number_time',
             'number-letter_minus_letter_time']
    a = list(df[df.phase == 'number']['total_time'])[0]
    b = list(df[df.phase == 'letter']['total_time'])[0]
    c = list(df[df.phase == 'number-letter']['total_time'])[0]
    entries += [b - a, c - a, c - b]
    
    dfsum = pandas.DataFrame(entries, cols).T
    return dfsum


#def main():
#    """Command-line executor."""
#    params = (test_name,
#              control_method,
#              trial_method,
#              output_format,
#              summary_method)
#    batch.run_single_test(*params)


if __name__ == '__main__':
    main()