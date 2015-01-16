# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

verbal_fluency: Verbal fluency test.

This test requires the proband to relinquish control to the experimenter.
Probands are instructed to list as many words as they can that begin with a
certain letter (first three trials) or as many animals (final trial) as they
can in 60 seconds. The experimenter records the number of correct and incorrect
responses.

TODO: Add references etc.

@author: Sam Mathias
@status: completed
@version: 1.0

"""

import pandas
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.data as data
import charlie.tools.summaries as summaries

test_name = 'verbal_fluency'
trials = 4
time_limit = 60
output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trialn', int),
                 ('rsp', str)]


class MainWindow(QtGui.QMainWindow):
    """Experimenter-operated GUI object."""

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()

        # load data object into this object
        self.data_obj = data_obj
        self.instr = instructions
        self.next_phase = 'instruct'

        # load central widget
        self.resize(800, 400)
        self.set_central_widget()
        self.show()

    def set_central_widget(self):
        """Saves the data accrued thus far then sets the central widget
        contingent upon trial number and phase."""

        if self.data_obj.data and self.data_obj.proband_id != 'TEST' and not \
           self.data_obj.test_done:
            self.data_obj.update()
            self.data_obj.to_csv()

        if not self.data_obj.test_done:

            if self.next_phase == 'instruct':

                self.current_trial = self.data_obj.control[0]
                self.trialn = self.current_trial[2]
                self.next_phase = 'respond'
                self.central_widget = InstructWidget(self)

            else:

                self.current_trial = self.data_obj.control.pop(0)
                self.next_phase = 'instruct'
                self.central_widget = RespondWidget(self)

            self.setCentralWidget(self.central_widget)
            if not self.data_obj.control:
                self.data_obj.test_done = True
            self.setWindowTitle(self.instr[1] % (self.trialn + 1))

        else:
            if self.data_obj.proband_id != 'TEST':
                self.data_obj.update()
                self.data_obj.to_csv()
                self.data_obj.to_localdb(summary_method, self.instr)
            self.close()


class InstructWidget(QtGui.QWidget):
    """Widget for an instruction phase. Displays a message that the
    experimenter should read out load."""

    def __init__(self, parent):
        super(InstructWidget, self).__init__(parent)

        # import variables from parent
        _, _, self.trialn = self.parent().current_trial
        self.instr = self.parent().instr

        # show contents
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Creates the ListenWidget GUI."""
        message_box = QtGui.QGroupBox(self.instr[2])
        self.label = QtGui.QLabel(self.instr[3 + self.trialn])
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[7])
        self.button.clicked.connect(self.parent().set_central_widget)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        widget_layout.addWidget(self.button)
        self.setLayout(widget_layout)


class RespondWidget(QtGui.QWidget):
    """Widget for a response phase. Contains a set of response buttons and two
    dynamic number displays. The first number records the total responses made,
    and the second is a timer that counts down TIME_LIMIT seconds. When the
    countdown reaches zero, the phase is over, and the gui allows no more
    responses to be recorded."""

    def __init__(self, parent):
        super(RespondWidget, self).__init__(parent)

        self.proband_id, _, self.trialn = self.parent().current_trial
        self.responses_made = 0
        self.countdown_over = False
        self.countdown_began = False
        self.seconds_left = time_limit
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def update_data(self, response):
        """Formats the response into the usual trial_info format and appends it
        to the data iterable in the data object."""
        trial_info = tuple(list(self.parent().current_trial) + [response])
        self.parent().data_obj.data.append(trial_info)

    def setup_ui(self):
        """Sets up the gui for the widget."""
        response_box = QtGui.QGroupBox(self.instr[8])
        response_grid = QtGui.QGridLayout()
        self.valid_rsp_button = QtGui.QPushButton(self.instr[9])
        response_grid.addWidget(self.valid_rsp_button, 1, 1)
        self.valid_rsp_button.clicked.connect(self.valid_response)
        self.invalid_rsp_button = QtGui.QPushButton(self.instr[10])
        response_grid.addWidget(self.invalid_rsp_button, 1, 2)
        self.invalid_rsp_button.clicked.connect(self.invalid_response)
        response_box_layout = QtGui.QVBoxLayout()
        response_box_layout.addLayout(response_grid)
        response_box.setLayout(response_box_layout)
        rsp_counter_box = QtGui.QGroupBox(self.instr[11])
        rsp_counter_layout = QtGui.QVBoxLayout()
        self.rsp_counter = QtGui.QLCDNumber()
        self.rsp_counter.setDigitCount(2)
        rsp_counter_layout.addWidget(self.rsp_counter)
        rsp_counter_box.setLayout(rsp_counter_layout)
        countdown_box = QtGui.QGroupBox(self.instr[12])
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

    def valid_response(self):
        self.response('True')

    def invalid_response(self):
        self.response('False')

    def response(self, valid):
        """Method called when any one of the response buttons are pressed.
        Formats the response and adds it to the data iterable, then updates the
        responses_made counter. If the countdown is not over, a reponse will
        reset the countdown and enable the pause button. If the cowntdown is
        over, responses are still counted."""
        self.update_data(valid)

        self.responses_made += 1
        self.rsp_counter.display(self.responses_made)

        if not self.countdown_over and not self.countdown_began:
            self.timer = QtCore.QBasicTimer()
            self.timer.start(1000, self)
            self.button.setText(self.instr[13])
            # HACK!!!!--------------------------
            try:
                self.button.clicked.disconnect()
            except:
                pass
            # ----------------------------------
            self.button.clicked.connect(self.pause_timer)
            self.countdown.display(self.seconds_left)
            self.countdown_began = True

    def timerEvent(self, _):
        """Reimplemented event handler that counts down from TIME_LIMIT. After
        which the pause button is replaced by a quit button, allowing the
        experimenter to move on to the next trial."""
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.countdown.display(self.seconds_left)
        else:
            self.timer.stop()
            self.countdown_over = True
            self.button.setText(self.instr[14])
            self.button.clicked.connect(self.parent().set_central_widget)

    def pause_timer(self):
        """When counting down, this pauses the countdown. Whilst already
        paused, allows the experimenter to quit the trial."""
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText(self.instr[14])
            self.button.clicked.connect(self.parent().set_central_widget)
            self.countdown_began = False


def control_method(proband_id, instructions):
    """Generate a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, trialn)."""
    return [(proband_id, test_name, trialn) for trialn in xrange(4)]


def summary_method(data, instructions):
    """Computes summary statistics for the verbal fluency task."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    for trialn in xrange(4):
        cols += ['trial_%i_%s' % (trialn, s) for s in ['nvrsp', 'nirsp']]
        subdf = df[df.trialn == trialn]
        entries += [len(subdf[subdf.rsp=='True']),
                    len(subdf[subdf.rsp=='False'])]
    dfsum = pandas.DataFrame(entries, cols).T
    return dfsum