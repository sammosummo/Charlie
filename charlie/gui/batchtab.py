__author__ = 'smathias'


import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.batch as batch
import charlie.tools.questionnaires as questionnaires


m = 'Make sure the Proband ID is set correctly before running a batch!'


class BatchTab(QtGui.QWidget):

    """
    This tab allows the user to run batches of tests and questionnaires. Batch
    and questionnaire lists are saved as text files within Charlie.
    """
    #TODO: Add the ability to edit and save new batch files.

    def __init__(self, parent):
        super(BatchTab, self).__init__(parent)
        self.instr = self.parent().instr

        batches = [''] + batch.get_available_batches()
        qlists = [''] + questionnaires.get_available_questionnaire_lists()
        self._batch = None
        self._q = None

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(QtGui.QLabel(m))
        a = QtGui.QGroupBox('Batch mode:')
        grid = QtGui.QGridLayout()

        grid.addWidget(QtGui.QLabel('Available batches:'), 0, 0)
        batch_list = QtGui.QComboBox()
        batch_list.addItems(batches)
        batch_list.setInsertPolicy(batch_list.NoInsert)
        batch_list.setEditable(False)
        batch_list.activated.connect(self.set_current_batch)
        batch_list.editTextChanged.connect(self.set_current_batch)
        grid.addWidget(batch_list, 1, 0)
        grid.addWidget(QtGui.QLabel('Tests in selected batch:'), 3, 0)
        self.batch_contents = QtGui.QListWidget()
        grid.addWidget(self.batch_contents, 4, 0, 6, 1)

        grid.addWidget(QtGui.QLabel('Available questionnaire lists:'), 0, 1)
        q_list = QtGui.QComboBox()
        q_list.addItems(qlists)
        q_list.setInsertPolicy(q_list.NoInsert)
        q_list.setEditable(False)
        q_list.activated.connect(self.set_current_q)
        q_list.editTextChanged.connect(self.set_current_q)
        grid.addWidget(q_list, 1, 1)
        grid.addWidget(QtGui.QLabel('Questionnaire lists:'), 3, 1)
        self.q_contents = QtGui.QListWidget()
        grid.addWidget(self.q_contents, 4, 1, 6, 1)

        a.setLayout(grid)
        self.vbox.addWidget(a)

        b = QtGui.QGroupBox('Run selection:')
        vbox = QtGui.QVBoxLayout()
        button = QtGui.QPushButton('Run now...')
        button.clicked.connect(self.run)
        vbox.addWidget(button)
        b.setLayout(vbox)
        self.vbox.addWidget(b)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)
        self.show()

    def set_current_q(self):
        _q = self.sender().currentText()
        if _q:
            self._q = _q
            qlist = questionnaires.questionnaires_in_list(_q)
            self.q_contents.clear()
            self.q_contents.addItems(qlist)
        else:
            self.q_contents.clear()
            self._q = None

    def set_current_batch(self):
        _batch = self.sender().currentText()
        if _batch:
            self._batch = _batch
            test_list = batch.tests_in_batch(_batch)
            self.batch_contents.clear()
            self.batch_contents.addItems(test_list)
        else:
            self.batch_contents.clear()
            self._batch = None

    def run(self):
        self.parent().quit_and_run_batch()