# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

verbal_working_memory: Wechsler verbal working memory test

This test is a combination of the digit span forward, digit span backward, and
letter-number sequencing tests from the WAIS-III and WMC-III [1]. This test
requires the proband to relinquish control to the experimenter. There are four
phases to the test. In the first phase, the experimenter reads aloud sequences
of letters and digits to the proband. The proband then repeats the sequence
back to the experimenter, in the same order. The first sequence is two digits
in length; sequence length increases by one digit every two sequences. If the
proband responds incorrectly to both sequences of the same length, the phase is
terminated. The second phase is the same as the first except that probands
repeat the sequences in reverse order. In the third phase, the sequences
contain both digits and letters, and probands repeat the letters in numerical
order, followed by the letters in alphabetical order. The third phase serves as
a practice for the fourth phase. In the fourth phase there are three sequences
of the same length; if probands get all three wrong, the phase is terminated.

Summary statistics:

    forward_*
    backward_*
    sequencing_*

    *ntrials: number of trials
    *ncorrect: number of correct trials
    *k: longest sequence correctly reported [3]

References:

[1] The Psychological Corporation. (1997). WAIS-III/WMS-III technical manual.
San Antonio, TX: The Psychological Corporation.

[2] For forward and backward, this value reflects 50% correct threshold. For
letter-number sequencing, it reflects 33% correct.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'

import pandas
import numpy as np
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch


test_name = 'verbal_working_memory'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('sequence', str),
    ('rsp', str)
]
#sequences = [tuple(s.split('\n')) for s in self.instr[-4:]]


class MainWindow(QtGui.QMainWindow):
    """Experimenter-operated CVLT GUI object."""

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()
        self.data_obj = data_obj
        self.instr = instructions
        self.resize(800, 400)
        self.next_trial()
        self.show()

    def next_trial(self):
        """Checks to see if the test should stop, saves the data, then either
        quits or moves on to the next trial."""
        
        self.stopping_rule()
        
        if not self.data_obj.control:
            
            self.data_obj.test_done = True
            self.data_obj.update()
            self.data_obj.to_csv()
            self.data_obj.to_localdb(summary_method, self.instr)
            self.close()
            
        else:
            if self.data_obj.data:
                self.data_obj.update()
                self.data_obj.to_csv()
        
            self.current_trial = self.data_obj.control.pop(0)
            _, _, self.phase, self.trialn, self.sequence = self.current_trial
            if self.trialn == 0:
                self.central_widget = InstructWidget(self)
            else:
                self.central_widget = RespondWidget(self)
            self.setCentralWidget(self.central_widget)

    def set_central_widget_to_respond(self):
        """When the central widget is set to InstructWidget, we need a method
        that switches it to RespondWidget without popping another trial."""
        self.central_widget = RespondWidget(self)
        self.setCentralWidget(self.central_widget)

    def stopping_rule(self):
        """Checks to see if the proband got both or all three (depending on the
        phase) sequences of the same length incorrect. If True, all sequences
        of this phase remaining in the control iterable are removed."""
        if self.data_obj.data:
            last_trial = self.data_obj.data[-1]
            this_phase = last_trial[2]
            this_n = len(last_trial[4])
            corrects = [t[-1] for t in self.data_obj.data if t[2] == this_phase \
                        and len(t[4]) == this_n]
            if this_phase != 'digit letter':
                n = 2
            else:
                n = 3
            if len(corrects) == n and all(t == 'False' for t in corrects):
                new_c = [c for c in self.data_obj.control if c[2] != this_phase]
                self.data_obj.control = new_c


class InstructWidget(QtGui.QWidget):
    """Widget for a instruction phase. Displays a message that the experimenter
    should read out load."""

    def __init__(self, parent):
        super(InstructWidget, self).__init__(parent)

        self.phase = self.parent().phase
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Creates the GUI."""
        message_box = QtGui.QGroupBox()
        if self.phase == 'forward':
            msg = self.instr[3]
        elif self.phase == 'backward':
            msg = self.instr[4]
        elif self.phase == 'practice':
            msg = self.instr[5]
        else:
            msg = self.instr[6]
        self.label = QtGui.QLabel(msg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[7])
        self.button.clicked.connect(self.parent().set_central_widget_to_respond)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        widget_layout.addWidget(self.button)
        self.setLayout(widget_layout)


class RespondWidget(QtGui.QWidget):
    """Widget for a response phase. Contains the sequence which the
    experimenter must read out loud, the correct-response button (with the
    correct response written in it), and an incorrect response button. Clicking
    either button ends the trial."""

    def __init__(self, parent):
        super(RespondWidget, self).__init__(parent)

        self.phase = self.parent().phase
        self.sequence = self.parent().sequence
        self.ans = self.corr_order()
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def corr_order(self):
        """Provides the correct response for a given sequence given the current
        phase."""
        if self.phase == 'forward':
            return self.sequence
        elif self.phase == 'backward':
            return self.sequence[::-1]
        else:
            return ''.join(sorted(self.sequence))

    def update_data(self, response):
        """Formats the response into the usual trial_info format and appends it
        to the data iterable in the data object."""
        trial_info = tuple(list(self.parent().current_trial) + [response])
        self.parent().data_obj.data.append(trial_info)

    def setup_ui(self):
        """Sets up the gui for the widget."""
        message_box = QtGui.QGroupBox()
        msg = self.instr[8] % '-'.join(self.sequence)
        self.label = QtGui.QLabel(msg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        msg = self.instr[9] % '-'.join(self.ans)
        self.corr_button = QtGui.QPushButton(msg)
        self.corr_button.clicked.connect(self.corr_response)
        self.incorr_button = QtGui.QPushButton(self.instr[10])
        self.incorr_button.clicked.connect(self.incorr_response)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addWidget(self.corr_button)
        buttons_layout.addWidget(self.incorr_button)
        widget_layout.addLayout(buttons_layout)
        self.setLayout(widget_layout)

    def corr_response(self):
        """Records a correct response then closes the widget."""
        self.update_data(str(True))
        self.parent().next_trial()

    def incorr_response(self):
        """Records a incorrect response then closes the widget."""
        self.update_data(str(False))
        self.parent().next_trial()


def control_method(proband_id, instructions):
    """Generate a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, phase, trialn, sequence)."""
    phases = ['forward', 'backward', 'practice', 'digit letter']
    control = []
    for i, p in enumerate(phases):
        sequences = [tuple(s.split('\n')) for s in instructions[-4:]][i]
        for j, s in enumerate(sequences):
            control.append((proband_id, test_name, p, j, s))
    return control


def summary_method(data, instructions):
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    for phase in df.phase.unique():
        p = phase.replace(' ', '_')
        if p == 'digit_letter':
            p = 'sequencing'
        subdf = df[df.phase==phase]
        corrects = subdf[subdf.rsp=='True']
        cols += ['%s_ntrials' % p, '%s_ncorrect' % p, '%s_k' % p]
        entries += [len(subdf), len(corrects)]
        if len(corrects.tail(1)):
            kmax = len(np.ravel(corrects.tail(1).sequence)[0])
        else:
            kmax = 0
        entries.append(kmax)
    df = pandas.DataFrame(entries, cols).T
    print '---Here are the summary stats:'
    print df.T
    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)
