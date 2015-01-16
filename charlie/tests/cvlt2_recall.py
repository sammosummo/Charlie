# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

cvlt2: Recall portion of the computerised California verbal learning test
(CVLT) version II.

This is designed to be adminstered after the CVLT learning portion. It is
essentially just another trial without playback of the word list beforehand.
Apart from this difference, the script works in exactly the same way as the
script for the learning portion. See that script (cvlt.py) for a more detailed
description.

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

test_name = 'cvlt2_recall'

output_format = [('proband_id', str),
                 ('test_name', str),
                 ('trialn', int),
                 ('rsp', str)]

trials = 1
time_limit = 15


class MainWindow(QtGui.QMainWindow):
    """Experimenter-operated CVLT GUI object."""

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()

        # load data object into this object
        self.data_obj = data_obj

        # load stimuli filenames
        path = data.pj(data.AUDIO_PATH, test_name, 'EN')
        self.instr = instructions
        self.words = self.instr[-1].split('\n')

        # load central widget
        self.next_phase = 'instruct'
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
        message_box = QtGui.QGroupBox(self.instr[3])
        self.label = QtGui.QLabel(self.instr[4])
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(self.label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[13])
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
    and the second is a timer that counts down 15 seconds since the last
    response. When the countdown reaches zero, the phase is over, and the gui
    allows no more responses to be recorded."""

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
        """Formats the response into the usual trial_info format and appends it
        to the data iterable in the data object."""
        trial_info = tuple(list(self.parent().current_trial) + [response])
        self.parent().data_obj.data.append(trial_info)

    def setup_ui(self):
        """Sets up the gui for the widget."""
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
        """Method called when any one of the response buttons are pressed.
        Formats the response and adds it to the data iterable, then updates the
        responses_made counter. If the countdown is not over, a reponse will
        reset the countdown and enable the pause button. If the cowntdown is
        over, responses are still counted, but they do not reset the
        countdown."""
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
        """Reimplemented event handler that counts down from 15 seconds. After
        15 seconds, the pause button is replaced by a quit button, allowing the
        experimenter to move on to the next trial."""
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.countdown.display(self.seconds_left)
        else:
            self.timer.stop()
            self.countdown_over = True
            self.button.setText(self.instr[18])
            self.button.clicked.connect(self.parent().set_central_widget)

    def pause_timer(self):
        """When counting down, this pauses the countdown. Whilst already
        paused, allows the experimenter to quit the trial."""
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText(self.instr[18])
            self.button.clicked.connect(self.parent().set_central_widget)


def control_method(proband_id, instructions):
    """Generate a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, trialn)."""
    return [(proband_id, test_name, trialn) for trialn in xrange(1)]


def summary_method(data, instructions):
    """Computes summary statistics for the CVLT."""
    df = data.to_df()
    cols, entries = summaries.get_universal_entries(data)
    for trialn in [0]:
        cols += ['trial_%i_%s' % (trialn, s) for s in ['rsp', 'int', 'rep']]
        subdf = df[df.trialn == trialn]
        subdf_intrusions = subdf[subdf.rsp == 'intrusion']
        subdf_nointrusions = subdf[subdf.rsp != 'intrusion']
        subdf_nointrusions_unique = subdf_nointrusions.drop_duplicates()
        entries += [len(subdf_nointrusions_unique), len(subdf_intrusions),
                    len(subdf_nointrusions) - len(subdf_nointrusions_unique)]
        dfsum = pandas.DataFrame(entries, cols).T
    return dfsum


def main():
    """Command-line executor."""

    tools.batch.run_single_test(test_name, control_method, None, output_format,
                                summary_method, others=globals())


if __name__ == '__main__':
    main()