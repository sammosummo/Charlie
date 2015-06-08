# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 16:52:26 2014

trails: Pen-and-paper trail-making test.


This is identical to the STAN version of the trail-making test (TMT) [1].
This test requires three sheets of paper with trail configurations printed on
them. First the proband is instructed to relinquish control of the testing
computer to the experimenter. The experimenter then gives the proband the
printed sheets and performs the TMT as per the usual protocol. This test
contains a GUI to keep track of response times.

Normally, the TMT contains two parts, A and B. In part A, the proband must make
a trail between consecutive digits, and in part B, he/she must alternate
between letters and numbers. Given that the difference between parts A and B
have been considered useful [2], these are computed here. I'm not sure why but
the STAN also contained an intermediate part in which the proband makes a trail
between letters. This is preserved here.

Version history:

    1.1     Now saving summary stats to the database.

Summary statistics:

    [number or letter or number-letter]*

    errors : number of errors the proband makes
    rt : response time in seconds

References:

[1] Reitan, R.M. (1958). Validity of the Trail Making test as an indicator of
organic brain damage. Percept. Mot. Skills, 8:271-276.

[2] Corrigan, J.D., & Hinkeldey, M.S. (1987). Relationships between parts A and
B of the Trail Making Test. J Clin Psychol, 43(4):402–409.

"""
__version__ = 1.1
__author__ = 'Sam Mathias'

import pandas
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.data as data
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch


test_name = 'trails'
output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trial_type', str),
    ('rt', int),
    ('nerrors', int)
]


class MainWindow(QtGui.QMainWindow):
    """Experimenter-operated GUI object."""

    def __init__(self, data_obj, instructions):
        super(MainWindow, self).__init__()
        self.data_obj = data_obj
        self._rt = None
        self.resize(800, 400)
        self.instr = instructions
        self.next_trial()
        self.show()

    def next_trial(self):
        """Checks to see if the test should stop, saves the data, then either
        quits or moves on to the next trial."""
        if self.data_obj.data and self.data_obj.proband_id != 'TEST':
            self.data_obj.update()
            self.data_obj.to_csv()

        if not self.data_obj.control:
            self.data_obj.test_done = True
            if self.data_obj.proband_id != 'TEST':
                self.data_obj.to_localdb(summary_method, self.instr)
            self.close()
        else:
            self.current_trial = self.data_obj.control.pop(0)
            _, _, self.phase, self.trial_type = self.current_trial
            self.central_widget = InstructWidget(self)
            self.setCentralWidget(self.central_widget)

    def set_central_widget_to_respond(self):
        """When the central widget is set to InstructWidget, we need a method
        that switches it to RespondWidget without popping another trial."""
        self.central_widget = RespondWidget(self)
        self.setCentralWidget(self.central_widget)

    def set_central_widget_to_record(self):
        """When the central widget is set to RespondWidget, we need a method
        that switches it to RecordWidget without popping another trial."""
        self.central_widget = RecordWidget(self)
        self.setCentralWidget(self.central_widget)


class InstructWidget(QtGui.QWidget):
    """Widget for a instruction phase. Displays a message that the experimenter
    should read out load."""

    def __init__(self, parent):
        super(InstructWidget, self).__init__(parent)

        self.phase = self.parent().phase
        self.trial_type = self.parent().trial_type
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.scwtr = self.parent().set_central_widget_to_respond
        self.instr = self.parent().instr
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Creates the GUI."""
        message_box = QtGui.QGroupBox()
        if self.phase == 'number':
            if self.trial_type == 'practice':
                title, msg = self.instr[1:3]
            else:
                title, msg = self.instr[3:5]
        elif self.phase == 'letter':
            if self.trial_type == 'practice':
                title, msg = self.instr[5:7]
            else:
                title, msg = self.instr[7:9]
        else:
            if self.trial_type == 'practice':
                title, msg = self.instr[9:11]
            else:
                title, msg = self.instr[11:13]

        message_box = QtGui.QGroupBox(title)
        label = QtGui.QLabel(msg)
        label.setAlignment(QtCore.Qt.AlignCenter)
        message_layout = QtGui.QVBoxLayout()
        message_layout.addWidget(label)
        message_box.setLayout(message_layout)
        self.button = QtGui.QPushButton(self.instr[13])
        self.button.clicked.connect(self.scwtr)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addStretch(1)
        widget_layout.addWidget(message_box)
        widget_layout.addStretch(1)
        widget_layout.addWidget(self.button)
        self.setLayout(widget_layout)

    def keyPressEvent(self, e):
        """Reimplemented event handler."""
        if e.key() == 32:
            self.button.click()


class RespondWidget(QtGui.QWidget):
    """Widget for a response phase. Contains a timer (rounded to the nearest
    second but records with higher precision), three buttons, and a method for
    interpreting spacebar pushes. Initialisation starts a timer that can be
    paused by clicking the left button or pushing the spacebar. Clicking or
    pushing again will resume the timer, clicking the middle button will
    restart the timer, and clicking the right button will exit the trial.
    Time on exit is recorded."""

    def __init__(self, parent):
        super(RespondWidget, self).__init__(parent)

        self.instr = self.parent().instr
        self.time_elapsed = 0
        self.resolution = 10  # number of milliseconds between timer ticks
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setup_ui()
        self.start_timer()
        self.show()

    def setup_ui(self):
        """Sets up the gui for the widget."""
        timer_box = QtGui.QGroupBox(self.instr[14])
        timer_layout = QtGui.QVBoxLayout()
        self.timer_display = QtGui.QLCDNumber()
        self.timer_display.setDigitCount(3)
        timer_layout.addWidget(self.timer_display)
        timer_box.setLayout(timer_layout)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(timer_box)
        layout2 = QtGui.QHBoxLayout()
        self.left_button = QtGui.QPushButton()
        layout2.addWidget(self.left_button)
        self.middle_button = QtGui.QPushButton()
        layout2.addWidget(self.middle_button)
        self.right_button = QtGui.QPushButton()
        layout2.addWidget(self.right_button)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def start_timer(self):
        """Method called by first button click or spacebar. Starts the timer
        and swtiches the function of button and spacebar to pause_timer."""
        self.timer = QtCore.QBasicTimer()
        self.timer.start(10, self)
        self.left_button.clicked.connect(self.pause_timer)
        self.left_button.setText(self.instr[15])
        # HACK!!!!--------------------------------
        try:
            self.middle_button.clicked.disconnect()
            self.middle_button.setText('')
            self.right_button.clicked.disconnect()
            self.right_button.setText('')
        except:
            pass
        # ----------------------------------------

    def timerEvent(self, _):
        """Reimplemented event handler."""
        self.time_elapsed += self.resolution
        self.timer_display.display(round(self.time_elapsed / 1000.))

    def keyPressEvent(self, e):
        """Reimplemented event handler."""
        if e.key() == 32:
            self.left_button.click()

    def pause_timer(self):
        """Pause the timer."""
        self.timer.stop()
        self.left_button.clicked.connect(self.resume_timer)
        self.left_button.setText(self.instr[16])
        self.middle_button.clicked.connect(self.restart_timer)
        self.middle_button.setText(self.instr[17])
        self.right_button.clicked.connect(self.end_trial)
        self.right_button.setText(self.instr[18])

    def restart_timer(self):
        """Restart the timer."""
        self.time_elapsed = 0
        self.start_timer()

    def resume_timer(self):
        """Resume the timer."""
        self.start_timer()

    def end_trial(self):
        """Temporarily store response time and end the trial."""
        self.parent()._rt =  int(self.time_elapsed)
        self.parent().set_central_widget_to_record()


class RecordWidget(QtGui.QWidget):
    """Widget to record the number of errors made during a trial."""

    def __init__(self, parent):
        super(RecordWidget, self).__init__(parent)
        self.instr = self.parent().instr
        self.nerrors = None
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Sets up GUI for this widget."""
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(self.instr[-2]))
        self.errors_box = QtGui.QLineEdit()
        self.errors_box.setValidator(QtGui.QIntValidator(0, 99, self))
        self.errors_box.textEdited.connect(self.set_nerrors)
        layout.addWidget(self.errors_box)
        self.button = QtGui.QPushButton(self.instr[-1])
        self.button.clicked.connect(self.end_trial)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def set_nerrors(self):
        """Set the number of errors to the value entered in the errors_box."""
        try:
            self.nerrors = int(self.sender().text())
        except ValueError:
            self.nerrors = None

    def end_trial(self):
        """Record the number of errors, update the data object, and move on to
        the next trial."""
        if self.nerrors is not None:
            trial_info = list(self.parent().current_trial)
            trial_info.append(self.parent()._rt)
            trial_info.append(self.nerrors)
            self.parent().data_obj.data.append(tuple(trial_info))
            self.parent().next_trial()


def control_method(proband_id, instructions):
    """Generate a control iterable, a list of tuples in the format (proband_id,
    TEST_NAME, phase, trial_type)."""
    phases = ['number', 'letter', 'number-letter']
    trial_types = ['practice', 'test']
    return [(proband_id, test_name, p, t) for p in phases for t in trial_types]


def summary_method(data, instructions):
    """Computes summary stats for the trails task."""
    df = data.to_df()
    df = df[df.trial_type == 'test']
    cols, entries = summaries.get_universal_entries(data)
    for phase in df.phase.unique():
        cols += ['%s_rt' % phase, '%s_nerrors' % phase]
        entries += [int(df[df.phase == phase].rt),
                    int(df[df.phase == phase].nerrors)]
    dfsum = pandas.DataFrame(entries, cols).T
    # print '---Here are the summary stats:'
    # print dfsum.T

    return dfsum


if __name__ == '__main__':
    batch.run_single_test(test_name)