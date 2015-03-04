# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

cvlt2: Computerised California verbal learning test.

This is a modified and abridged version of the adult CVLT-II [1]. This script
administers the "learning" portion to the CVLT. First, the proband sees a
screen instructing them to relinquish control of the testing computer to the
experimenter. The experimenter then operates the CVLT GUI. On each trial, the
proband hears audio recordings of 16 words [2], and then repeats out loud as
many of them as he/she can recall. The experimenter records the correctly
recalled words, as well as the number of intrusions (words not from the list),
using the GUI. After 15 seconds without a response, the experimenter prompts
the proband for their final response or responses, then exists the trial. There
are 5 such trials.

The official CVLT-II contains a second part in which another list of words is
learned. This is omitted from the current test. In addition to this script,
there are 'recall' and 'recognition' portions to our version of the CVLT. These
are executed by two other scripts in the battery.

Summary statistics:

    trial_X_valid : Number of valid responses on trial X.
    trial_X_intrusions : Number of intrusions on trial X.
    trial_X_repetitions : Number of repetitions on trial X.
    trial_X_semantic : List-based semantic clustering index on trial X [2].
    trial_X_serial : List-based serial recall index on trial X [2].
    trial_X_dprime : Recall discriminability index [4].
    trial_x_criterion : Recall bias [5].
    mean_* : Mean stats across the five trials.

References:

[1] Delis, D.C., Kramer, J.H., Kaplan, E., & Ober, B.A. (2000). California
verbal learning test - second edition. Adult version. Manual. Psychological
Corporation, San Antonio, TX.

[2] Words spoken and recorded by Scott Bressler at Boston University.

[3] Stricker, J.L., Brown, G.G., Wixted, J., Baldo, J.V., & Delis, D.C. (2002).
New semantic and serial clustering indices for the California Verbal Learning
Test–Second Edition: Background, rationale, and formulae. J. Int. Neuropsychol.
Soc., 8:425-435.

[4] Delis, D.C., Wetter, S.R., Jacobson, M.W., Peavy, G., Hamilton, J.,
Gongvatana, A., et al. (2005). Recall discriminability: utility of a new
CVLT-II measure in the differential diagnosis of dementia. J. Int.
Neuropsychol. Soc., 11(6):708-15.

[5] This measure was not included by Delis, but I don't see why not. It
provides an index of how many intrusions there were relative to the number of
hits.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'


try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore

import pandas
import charlie.tools.data as data
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch


test_name = 'cvlt2'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('trialn', int),
    ('rsp', str)
]
trials = 5
time_limit = 15
isi = 2000
clusters = [0, 1, 2, 3, 1, 0, 3, 2, 0, 3, 1, 2, 3, 0, 2, 1]


class MainWindow(QtGui.QMainWindow):
    """
    Experimenter-operated CVLT GUI object.
    """

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()

        # load data object into this object
        self.data_obj = data_obj
        self.next_phase = 'listen'

        # load stimuli filenames
        path = data.pj(data.AUDIO_PATH, test_name)
        self.instr = instructions
        self.words = self.instr[-1].split('\n')
        self.stimuli = [data.pj(path, w + '.wav') for w in self.words]

        # load central widget
        self.resize(800, 400)
        self.set_central_widget()
        self.show()

    def set_central_widget(self):
        """
        Saves the data accrued thus far then sets the central widget
        contingent upon trial number and phase.
        """

        # save data
        if self.data_obj.data and self.data_obj.proband_id != 'TEST' and not \
        self.data_obj.test_done:
            self.data_obj.update()
            self.data_obj.to_csv()

        if not self.data_obj.test_done:

            if self.next_phase == 'listen':

                self.current_trial = self.data_obj.control[0]
                self.trialn = self.current_trial[2]
                self.next_phase = 'respond'
                self.setWindowTitle(self.instr[1] % (self.trialn + 1))
                self.central_widget = ListenWidget(self)

            else:

                self.current_trial = self.data_obj.control.pop(0)
                self.next_phase = 'listen'
                self.setWindowTitle(self.instr[2] % (self.trialn + 1))
                self.central_widget = RespondWidget(self)

            self.setCentralWidget(self.central_widget)
            if not self.data_obj.control:
                self.data_obj.test_done = True

        else:
            if self.data_obj.proband_id != 'TEST':
                self.data_obj.update()
                self.data_obj.to_csv()
                self.data_obj.to_localdb(summary_method, self.instr)
            self.close()


class ListenWidget(QtGui.QWidget):
    """Widget for a listening phase. Displays a message that the experimenter
    should read out load, and button to play the stimuli."""

    def __init__(self, parent):
        super(ListenWidget, self).__init__(parent)

        # import variables from parent
        self.words = self.parent().words
        self.stimuli = self.parent().stimuli
        _, _, self.trialn = self.parent().current_trial
        self.instr = self.parent().instr

        # show contents
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """
        Creates the ListenWidget GUI.
        """
        message_box = QtGui.QGroupBox(self.instr[3])
        self.label = QtGui.QLabel(self.instr[4 + self.trialn])
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[9])
        self.button.clicked.connect(self.start_events)
        self.pbar = QtGui.QProgressBar()
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        widget_layout.addWidget(self.button)
        widget_layout.addWidget(self.pbar)
        self.setLayout(widget_layout)

    def start_events(self):
        """
        Starts playing the auditory stimuli.
        """
        self.button.setText(self.instr[10])
        self.button.clicked.disconnect()
        self.timer = QtCore.QBasicTimer()
        self.num_played = 0
        self.timer.start(isi, self)

    def timerEvent(self, e):
        """
        Reimplemented event handler that plays stimuli and updates the
        progress bar. Allows experimenter to proceed once done.
        """
        nstim = len(self.stimuli)
        if self.num_played < nstim:
            QtGui.QSound.play(self.stimuli[self.num_played])
            msg = self.instr[11] + '\n%s' % self.words[self.num_played]
            self.label.setText(msg)
            self.num_played += 1
            self.pbar.setValue(self.num_played / float(nstim) * 100)

        else:
            self.timer.stop()
            self.label.setText(self.instr[12])
            self.button.setText(self.instr[13])
            self.button.clicked.connect(self.parent().set_central_widget)


class RespondWidget(QtGui.QWidget):
    """
    Widget for a response phase. Contains a set of response buttons and two
    dynamic number displays. The first number records the total responses made,
    and the second is a timer that counts down 15 seconds since the last
    response. When the countdown reaches zero, the phase is over, and the gui
    allows no more responses to be recorded.
    """

    def __init__(self, parent):
        super(RespondWidget, self).__init__(parent)

        self.proband_id, _, self.trialn = self.parent().current_trial
        self.responses_made = 0
        self.countdown_over = False
        self.seconds_left = time_limit
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def update_data(self, response):
        """
        Formats the response into the usual trial_info format and appends it
        to the data iterable in the data object.
        """
        trial_info = tuple(list(self.parent().current_trial) + [response])
        self.parent().data_obj.data.append(trial_info)

    def setup_ui(self):
        """
        Sets up the gui for the widget.
        """
        response_box = QtGui.QGroupBox(self.instr[14])
        response_grid = QtGui.QGridLayout()
        for j, word in enumerate(self.parent().words):
            button = QtGui.QPushButton('%s' % word)
            button.clicked.connect(self.response)
            response_grid.addWidget(button, j / 2, j % 2)
        button = QtGui.QPushButton('intrusion')
        button.clicked.connect(self.response)
        response_box_layout = QtGui.QVBoxLayout()
        response_box_layout.addLayout(response_grid)
        response_box_layout.addWidget(button)
        response_box.setLayout(response_box_layout)
        rsp_counter_box = QtGui.QGroupBox(self.instr[16])
        rsp_counter_layout = QtGui.QVBoxLayout()
        self.rsp_counter = QtGui.QLCDNumber()
        self.rsp_counter.setDigitCount(2)
        rsp_counter_layout.addWidget(self.rsp_counter)
        rsp_counter_box.setLayout(rsp_counter_layout)
        countdown_box = QtGui.QGroupBox(self.instr[17])
        countdown_layout = QtGui.QVBoxLayout()
        self.countdown = QtGui.QLCDNumber()
        self.countdown.setDigitCount(2)
        countdown_layout.addWidget(self.countdown)
        countdown_box.setLayout(countdown_layout)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(response_box)
        layout.addWidget(rsp_counter_box)
        layout.addWidget(countdown_box)
        self.button = QtGui.QPushButton()
        layout2 = QtGui.QVBoxLayout()
        layout2.addLayout(layout)
        layout2.addWidget(self.button)
        self.setLayout(layout2)
        self.rsp_counter.display(self.responses_made)
        self.countdown.display(self.seconds_left)

    def response(self):
        """
        Method called when any one of the response buttons are pressed.
        Formats the response and adds it to the data iterable, then updates the
        responses_made counter. If the countdown is not over, a response will
        reset the countdown and enable the pause button. If the countdown is
        over, responses are still counted, but they do not reset the
        countdown.
        """
        sender = self.sender()
        self.update_data(sender.text())

        self.responses_made += 1
        self.rsp_counter.display(self.responses_made)

        if not self.countdown_over:
            self.seconds_left = time_limit
            self.timer = QtCore.QBasicTimer()
            self.timer.start(1000, self)
            self.button.setText(self.instr[19])
            # HACK!!!!--------------------------
            try:
                self.button.clicked.disconnect()
            except:
                pass
            # ----------------------------------
            self.button.clicked.connect(self.pause_timer)
            self.countdown.display(self.seconds_left)

    def timerEvent(self, _):
        """
        Reimplemented event handler that counts down from 15 seconds. After
        15 seconds, the pause button is replaced by a quit button, allowing the
        experimenter to move on to the next trial.
        """
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.countdown.display(self.seconds_left)
        else:
            self.timer.stop()
            self.countdown_over = True
            self.button.setText(self.instr[18])
            self.button.clicked.connect(self.parent().set_central_widget)

    def pause_timer(self):
        """
        When counting down, this pauses the countdown. Whilst already
        paused, allows the experimenter to quit the trial.
        """
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText(self.instr[18])
            self.button.clicked.connect(self.parent().set_central_widget)


def control_method(proband_id, instructions):
    """
    Generates a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, trialn).
    """
    return [(proband_id, test_name, trialn) for trialn in xrange(5)]


def semantic_clustering(words, clusters, responses):
    """
    List-based semantic clustering index from the CVLT-II.
    """
    dic = {w: c for w, c in zip(words, clusters)}
    dic['intrusion'] = None
    dic['repetition'] = None
    words_used = []
    for i in xrange(len(responses)):
        if responses[i] in words_used:
            responses[i] = 'repetition'
        words_used.append(responses[i])
    clusts = [dic[r] for r in responses]
    obs = 0
    for i in xrange(1, len(responses)):
        if clusts[i] is not None:
            if clusts[i] == clusts[i - 1]:
                obs += 1
    r = len(filter(None, clusts))
    return obs - ((r - 1) / 5.)


def serial_clustering(words, responses):
    """
    List-based serial clustering index from the CVLT-II.
    """
    words_used = []
    serial_positions = []
    for i in xrange(len(responses)):
        if responses[i] in words_used:
            responses[i] = 'repetition'
        words_used.append(responses[i])
        if responses[i] not in ['repetition', 'intrusion']:
            serial_positions.append(words.index(responses[i]))
        else:
            serial_positions.append(None)
    obs = 0
    for i in xrange(1, len(responses)):
        if serial_positions[i] is not None:
            if serial_positions[i - 1] is not None:
                if serial_positions[i] == serial_positions[i - 1] + 1:
                    obs += 1
    r = len(filter(None, serial_positions))
    return obs - ((r - 1) / 16.)


def summary_method(data_obj, instructions):
    """
    Computes summary statistics for this task.
    """
    df = data_obj.to_df()
    stats = summaries.get_universal_stats(data_obj)
    dvs = [
        'valid',
        'intrusions',
        'repetitions',
        'semantic',
        'serial',
        'dprime',
        'criterion'
    ]
    words = instructions[-1].split('\n')

    for trialn in xrange(5):

        cols = ['trial_%i_%s' % (trialn, dv) for dv in dvs]
        df2 = df[df.trialn == trialn]
        responses = df2.rsp.tolist()
        nintr = len(df2[df2.rsp == 'intrusion'])
        nvalid = len(df2[df2.rsp != 'intrusion'].drop_duplicates())
        nreps = len(df2[df2.rsp != 'intrusion']) - nvalid
        semantic = semantic_clustering(words, clusters, responses)
        serial = serial_clustering(words, responses)
        sdt = max([nintr, 16]), 16, nvalid, nintr
        d, c = summaries.sdt_yesno(*sdt)
        entries = [nvalid, nintr, nreps, semantic, serial, d, c]
        stats += zip(cols, entries)

    df = summaries.make_df(stats)

    cols = ['total_%s' % dv for dv in ['valid', 'intrusions', 'repetitions']]
    entries = []
    for dv in ['valid', 'intrusions', 'repetitions']:
        cs = [c for c in df.columns if '_' + dv in c]
        x = float(df[cs].sum(axis=1))
        entries.append(x)
    stats += zip(cols, entries)

    cols = ['mean_%s' % dv for dv in ['semantic', 'serial', 'dprime',
                                      'criterion']]
    entries = []
    for dv in ['semantic', 'serial', 'dprime', 'criterion']:
        cs = [c for c in df.columns if '_' + dv in c]
        x = float(df[cs].mean(axis=1))
        entries.append(x)
    stats += zip(cols, entries)

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