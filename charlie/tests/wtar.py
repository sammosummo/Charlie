# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

Wechsler Test of Adult Reading.

Computerised version of the standard WTAR. Probands relinquish control of the
testing computer to the experimenter, then read a list of 50 words out loud.
The experimenter marks their pronunciations using the GUI. The test terminates
automatically 12 consequtive errors.

Reference: Holdnack, H.A. (2001). Wechsler Test of Adult Reading: WTAR. San
Antonio, TX: The Psychological Corporation.

TODO: Add a title to the WTAR GUI.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
import numpy as np
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.summaries as summaries

test_name = 'wtar'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trialn', int),
                 ('word', str),
                 ('rsp', str)]
#WORDS = [tuple(l.split(',')) for l in self.instr[-1].split('\n')]

class MainWindow(QtGui.QMainWindow):
    """Experimenter-operated CVLT GUI object."""

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()
        self.data_obj = data_obj
        self.instr = instructions
        self.data_obj.consequtive_errors = 0
        self.next_phase = 'instruct'
        self.resize(800, 400)
        self.set_central_widget()
        self.show()

    def set_central_widget(self):
        """Saves the data_obj accrued thus far then sets the central widget
        contingent upon trial number and phase."""

        # save data_obj
        if self.data_obj.data and self.data_obj.proband_id != 'TEST' and not \
           self.data_obj.test_done:
            self.data_obj.update()
            self.data_obj.to_csv()

        if not self.data_obj.test_done:

            if self.next_phase == 'instruct':

                self.current_trial = self.data_obj.control[0]
                self.next_phase = 'respond'
                self.central_widget = InstructWidget(self)

            else:

                self.current_trial = self.data_obj.control.pop(0)
                self.central_widget = RespondWidget(self)

            self.setCentralWidget(self.central_widget)

            if self.data_obj.consequtive_errors >= 12:
                self.data_obj.test_done = True

            if not self.data_obj.control:
                self.data_obj.test_done = True

        else:
            if self.data_obj.proband_id != 'TEST':
                self.data_obj.update()
                self.data_obj.to_csv()
                self.data_obj.to_localdb(summary_method, self.instr)
            self.close()


class InstructWidget(QtGui.QWidget):
    """Widget for a instruction phase. Displays a message that the experimenter
    should read out load."""

    def __init__(self, parent):
        super(InstructWidget, self).__init__(parent)
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Creates the GUI."""
        message_box = QtGui.QGroupBox()
        self.label = QtGui.QLabel(self.instr[1])
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[2])
        self.button.clicked.connect(self.parent().set_central_widget)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        widget_layout.addWidget(self.button)
        self.setLayout(widget_layout)


class RespondWidget(QtGui.QWidget):
    """Widget for a response phase. Contains the word, the acceptable
    pronunciations, and correct/incorrect buttons. Clicking either one ends the
    trial."""

    def __init__(self, parent):
        super(RespondWidget, self).__init__(parent)

        _, _, _, self.word = self.parent().current_trial
        self.instr = self.parent().instr
        words = [tuple(l.split(',')) for l in self.instr[-1].split('\n')]
        self.pronunciations = dict(words)[self.word]
        self.setup_ui()
        self.show()

    def update_data_obj(self, response):
        """Formats the response into the usual trial_info format and appends it
        to the data_obj iterable in the data_obj object."""
        trial_info = tuple(list(self.parent().current_trial) + [response])
        self.parent().data_obj.data.append(trial_info)

    def setup_ui(self):
        """Sets up the gui for the widget."""
        message_box = QtGui.QGroupBox()
        msg = self.word + '\n\n' + self.pronunciations
        self.label = QtGui.QLabel(msg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.corr_button = QtGui.QPushButton(self.instr[3])
        self.corr_button.clicked.connect(self.corr_response)
        self.incorr_button = QtGui.QPushButton(self.instr[4])
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
        self.update_data_obj(str(True))
        self.parent().set_central_widget()

    def incorr_response(self):
        """Records a incorrect response then closes the widget."""
        self.update_data_obj(str(False))
        self.parent().data_obj.consequtive_errors += 1
        self.parent().set_central_widget()


def control_method(proband_id, instructions):
    """Generate a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, trialn, word)."""
    words = [tuple(l.split(',')) for l in instructions[-1].split('\n')]
    return [(proband_id, test_name, i, w[0]) for i, w in enumerate(words)]


def summary_method(data, instructions):
    """Computes summary statistics for the WTAR."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    cols += ['ntrials', 'ncorrect']
    entries += [len(df), len(df[df.rsp=='True'])]
    dfsum = pandas.DataFrame(entries, cols).T
    return dfsum