__author__ = 'smathias'

try:
    from PySide import QtGui, QtCore
    from PySide.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PySide.QtGui import QTableView, QApplication
except ImportError:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PyQt4.QtGui import QTableView, QApplication
import pandas
import charlie.tools.data as data
import charlie.tools.instructions as instructions
import numpy as np
from pkgutil import iter_modules
import charlie.tests
from os.path import dirname
import importlib
import sys
import charlie.tools.batch as batch
import charlie.tools.questionnaires as questionnaires


class QuestionnaireTab(QtGui.QWidget):

    """
    Second tab in the GUI. Allows the user to run individual tests or batches
    of tests.
    """

    def __init__(self, parent=None):
        super(QuestionnaireTab, self).__init__(parent=parent)
        self.instr = self.parent().instr
        self._questionnaires = []
        self._qlist = None
        self._q = []
        self.vbox = QtGui.QVBoxLayout()
        a = QtGui.QGroupBox('Questionnaire selection:')
        grid = QtGui.QGridLayout()

        grid.addWidget(QtGui.QLabel('Built-in sets:'), 0, 0)
        set_list = QtGui.QComboBox()
        x = [''] + questionnaires.get_available_questionnaire_lists()
        set_list.addItems(x)
        set_list.setInsertPolicy(set_list.NoInsert)
        set_list.setEditable(False)
        set_list.activated.connect(self.set_current_qlist)
        set_list.editTextChanged.connect(self.set_current_qlist)
        grid.addWidget(set_list, 1, 0)
        button1 = QtGui.QPushButton('Add to list --->')
        button1.clicked.connect(self.add_qlist_to_queue)
        grid.addWidget(button1, 2, 0)

        grid.addWidget(QtGui.QLabel('Individual questionnaires:'), 3, 0)
        q_list = QtGui.QComboBox()
        x = [''] + questionnaires.get_available_questionnaires('EN')
        q_list.addItems(x)
        q_list.setInsertPolicy(set_list.NoInsert)
        q_list.setEditable(False)
        q_list.activated.connect(self.set_current_q)
        q_list.editTextChanged.connect(self.set_current_q)
        grid.addWidget(q_list, 4, 0)
        button2 = QtGui.QPushButton('Add to list --->')
        button2.clicked.connect(self.add_q_to_queue)
        grid.addWidget(button2, 5, 0)

        # # self.doc_box = QtGui.QTextEdit()
        # # self.doc_box.insertPlainText(self.instr[33])
        # # grid.addWidget(self.doc_box, 1, 0, 4, 5)
        grid.addWidget(QtGui.QLabel('Currently in list:'), 0, 1)
        self.q_list_contents = QtGui.QListWidget()
        button3 = QtGui.QPushButton('Clear list')
        button3.clicked.connect(self.clear)
        grid.addWidget(button3, 6, 0)

        grid.addWidget(self.q_list_contents, 1, 1, 6, 1)

        a.setLayout(grid)
        self.vbox.addWidget(a)

        b = QtGui.QGroupBox('Run selection:')
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(QtGui.QLabel('Questionnaires can also be administered in batch mode.'))
        button = QtGui.QPushButton('Run now...')
        button.clicked.connect(self.run)
        vbox.addWidget(button)
        b.setLayout(vbox)
        self.vbox.addWidget(b)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)
        self.show()

    def set_current_qlist(self):
        _qlist = self.sender().currentText()
        if _qlist:
            self._qlist = _qlist
        else:
            self._qlist = None

    def set_current_q(self):
        _q = self.sender().currentText()
        if _q:
            self._q = _q
        else:
            self._qlist = None

    def add_qlist_to_queue(self):
        if self._qlist is not None:
            _questionnaires = questionnaires.questionnaires_in_list(self._qlist)
            for q in _questionnaires:
                if q not in self._questionnaires:
                    self._questionnaires.append(q)
        self.q_list_contents.clear()
        self.q_list_contents.addItems(self._questionnaires)

    def add_q_to_queue(self):
        if self._q is not None and self._q not in self._questionnaires:
            self._questionnaires.append(self._q)
        self.q_list_contents.clear()
        self.q_list_contents.addItems(self._questionnaires)

    def clear(self):
        self.q_list_contents.clear()
        self._questionnaires = []

    def run(self):
        questionnaires.create_questionnaire_app(self._questionnaires, 'EN')
