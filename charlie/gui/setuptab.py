__author__ = 'smathias'

try:
    from PySide import QtGui, QtCore
    from PySide.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PySide.QtGui import QTableView, QApplication
except ImportError:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PyQt4.QtGui import QTableView, QApplication
import sys
import pandas
import charlie.tools.data as data
import charlie.tools.instructions as instructions
import numpy as np


class SetupTab(QtGui.QWidget):

    """
    First tab in the GUI. Allows the user to view, select, and edit the
    project, user, and proband information.
    """

    def __init__(self, parent=None):
        super(SetupTab, self).__init__(parent=parent)
        self.instr = self.parent().instr
        self.args = self.parent().args
        self.proband_id = self.args.proband_id
        self.user_id = self.args.user_id
        self.proj_id = self.args.proj_id
        self.df = data.populate_demographics()
        self.projects_list = [self.proj_id] + self.df.proj_id.dropna().unique().tolist()
        print self.projects_list
        self.users_list = [self.user_id] + self.df.user_id.dropna().unique().tolist()
        self.setup_ui()
        self.create_proband_table()

    def setup_ui(self):

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(QtGui.QLabel(self.instr[3]))

        # project and user boxes
        b = QtGui.QGroupBox(self.instr[4])
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(self.instr[5]), 0, 0)
        proj_list = QtGui.QComboBox()
        proj_list.addItems(self.projects_list)
        proj_list.setInsertPolicy(proj_list.NoInsert)
        proj_list.setEditable(True)
        proj_list.activated.connect(self.set_proj)
        proj_list.editTextChanged.connect(self.set_proj)
        proj_list.setCurrentIndex(0)
        grid.addWidget(proj_list, 1, 0)

        grid.addWidget(QtGui.QLabel(self.instr[6]), 0, 1)
        exp_list = QtGui.QComboBox()
        exp_list.setItemText(0, self.user_id)
        exp_list.addItems(self.users_list)
        exp_list.setInsertPolicy(exp_list.NoInsert)
        exp_list.setEditable(True)
        exp_list.activated.connect(self.set_user)
        exp_list.editTextChanged.connect(self.set_user)
        exp_list.setCurrentIndex(0)
        grid.addWidget(exp_list, 1, 1)
        grid.addWidget(QtGui.QLabel(self.instr[7]), 2, 0, 1, 2)
        b.setLayout(grid)
        self.vbox.addWidget(b)

        # proband box
        self.proband_groupbox = QtGui.QGroupBox(self.instr[8])
        self.proband_grid = QtGui.QGridLayout()
        self.proband_grid.addWidget(QtGui.QLabel(self.instr[9]), 0, 0, 1, 5)
        self.proband_grid.addWidget(QtGui.QLabel(self.instr[10]), 1, 0)
        self.proband_id_label = QtGui.QLabel()
        self.set_text()
        self.proband_grid.addWidget(self.proband_id_label, 1, 1, 1, 4)

        funcs = [
            self.select_proband, self.deselect_proband, self.edit_proband,
            self.new_proband, self.test_proband
        ]
        for i, func in enumerate(funcs):
            button = QtGui.QPushButton(self.instr[11+i])
            button.clicked.connect(func)
            self.proband_grid.addWidget(button, 3, i)
        self.proband_groupbox.setLayout(self.proband_grid)
        self.vbox.addWidget(self.proband_groupbox)
        self.setLayout(self.vbox)

    def create_proband_table(self):
        self.df = data.populate_demographics()
        self.probands_list = self.df.proband_id.unique().tolist()
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(data.LOCAL_DB_F)
        self.db.open()
        self.model = QSqlTableModel()
        self.model.setTable('probands')
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionMode(self.view.SingleSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)
        self.view.setSortingEnabled(True)
        self.proband_grid.addWidget(self.view, 2, 0, 1, 5)

    def set_text(self):
        """
        Displays the currently selected proband's ID, in green. Displays
        NONE in red if no proband is selected.
        """
        if self.proband_id:
            s = '<font color="green"><b>%s</b></font>' % self.proband_id
        else:
            s = '<font color="red"><b>None</b></font>'
        self.proband_id_label.setText(s)

    def set_proj(self):
        """
        Sets the project ID.
        """
        self.proj_id = self.sender().currentText()

    def set_user(self):
        """
        Sets the user (experimenter) ID.
        """
        self.user_id = self.sender().currentText()

    def select_proband(self):
        """
        Retrieves a proband from the database.
        """
        if self.check_project_and_experimenter():
            i = self.view.currentIndex()
            j = self.model.data(i, all_row=True)
            if j in self.probands_list:
                self.proband_id = j
                self.set_text()
            sys.argv = sys.argv[:1]
            sys.argv += ['-p', self.proband_id]
            print sys.argv

    def deselect_proband(self):
        """
        Sets PROBAND to None.
        """
        self.proband_id = ''
        self.set_text()

    def edit_proband(self):
        """
        Creates the proband editor pop-up window.
        """
        if self.check_project_and_experimenter() and self.check_proband():
            self.proband_window(False)

    def new_proband(self):
        """
        Creates the proband editor window with all entries blank.
        """
        if self.check_project_and_experimenter():
            self.proband_window(True)

    def test_proband(self):
        """
        Sets proband to TEST. This is used for debugging test scripts
        without saving data.
        """
        self.proband_id = 'TEST'
        self.set_text()

    def check_project_and_experimenter(self, dialog=True):
        """
        Just checks if project and experimenter IDs have been entered. If
        not, no testing can be done.
        """
        if not self.proj_id:
            if dialog:
                s = self.instr[16]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
            return False
        elif not self.user_id:
            if dialog:
                s = self.instr[17]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
            return False
        else:
            return True

    def check_proband(self, dialog=True):
        """
        Checks that a proband has been selected.
        """
        if not self.proband_id:
            if dialog:
                s = self.instr[18]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
                return False
        elif self.proband_id == 'TEST':
            if dialog:
                s = self.instr[19]
                a = QtGui.QMessageBox()
                a.setText(s)
                a.exec_()
        else:
            return True

    def proband_window(self, new):
        """
        Creates a proband window.
        """
        if new:
            self.deselect_proband()
        self.w = ProbandWindow(
            self.proband_id, self.proj_id, self.user_id, self.df
        )
        self.w.com.update_proband_table.connect(self.create_proband_table)


class ProbandWindow(QtGui.QWidget):

    """
    Proband edit/creation window. This pops up as a separate window from the
    manager. Includes proband ID, sex, and dob. The project and experimenter
    IDs are inherited from the the main window, so this is impossible if these
    fields are left blank.
    """

    def __init__(self, proband_id, proj_id, user_id, df, parent=None):
        super(ProbandWindow, self).__init__(parent=parent)

        self.df = df
        self.fields = ['proband_id', 'sex', 'age', 'user_id', 'proj_id']
        self.fd = [
            'Proband ID:',
            'Sex:',
            'Age in years:',
            'Assoc. project ID:',
            'Assoc. experimenter ID:'
        ]
        self.projects = [proj_id] + self.df.proj_id.dropna().unique().tolist()
        self.users = [user_id] + self.df.user_id.dropna().unique().tolist()
        self.com = CustomSignals()

        if proband_id:
            self.new_proband = False
            self._proband_id = proband_id
            self.proband = df.loc[proband_id]
            nulls = self.proband.isnull()
            if nulls.age == True:
                self._age = None
            else:
                self._age = int(self.proband.age)
            if nulls.sex == True:
                self._sex = None
            else:
                self._sex = self.proband.sex
            if nulls.proj_id == True:
                self._proj_id = proj_id
            else:
                self._proj_id = self.proband.proj_id
            if nulls.user_id == True:
                self._user_id = user_id
            else:
                self._user_id = self.proband.user_id
        else:
            self.new_proband = True
            self.proband = pandas.Series(index=self.fields)
            self._proband_id = None
            self._sex = None
            self._age = None
            self._proj_id = proj_id
            self._user_id = user_id
        self.highlighted_proj = self.projects.index(self._proj_id)
        self.highlighted_user = self.users.index(self._user_id)

        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle('Proband editor')
        grid = QtGui.QGridLayout()

        # proband ID field (not editable if existing proband loaded)
        grid.addWidget(QtGui.QLabel(self.fd[0]), 0, 0)
        if not self.new_proband:
            s = '<b>%s</b>' % self.proband.proband_id
            proband_id_field = QtGui.QLabel(s)
        else:
            proband_id_field = QtGui.QLineEdit()
            proband_id_field.textEdited.connect(self.edit_proband_id)
        grid.addWidget(proband_id_field, 0, 1, 1, 2)

        # sex field
        grid.addWidget(QtGui.QLabel(self.fd[1]), 1, 0)
        self.rbs = []
        for i, sex in enumerate(['Male', 'Female']):
            rb = QtGui.QRadioButton(sex)
            if self._sex == sex:
                rb.toggle()
            grid.addWidget(rb, 1, i + 1)
            self.rbs.append(rb)

        # age field
        grid.addWidget(QtGui.QLabel(self.fd[2]), 2, 0)
        if self._age:
            age_field = QtGui.QLineEdit('%i' % self._age)
        else:
            age_field = QtGui.QLineEdit()
        age_field.textEdited.connect(self.edit_age)
        grid.addWidget(age_field, 2, 1, 1, 2)

        # project ID field
        grid.addWidget(QtGui.QLabel(self.fd[3]), 3, 0)
        proj_field = QtGui.QComboBox()
        proj_field.addItems(self.projects)
        proj_field.setInsertPolicy(proj_field.NoInsert)
        proj_field.setEditable(True)
        proj_field.activated.connect(self.edit_proj)
        proj_field.editTextChanged.connect(self.edit_proj)
        proj_field.setCurrentIndex(self.highlighted_proj)
        grid.addWidget(proj_field, 3, 1, 1, 2)

         # user ID field
        grid.addWidget(QtGui.QLabel(self.fd[4]), 4, 0)
        proj_field = QtGui.QComboBox()
        proj_field.addItems(self.users)
        proj_field.setInsertPolicy(proj_field.NoInsert)
        proj_field.setEditable(True)
        proj_field.activated.connect(self.edit_user)
        proj_field.editTextChanged.connect(self.edit_user)
        proj_field.setCurrentIndex(self.highlighted_user)
        grid.addWidget(proj_field, 4, 1, 1, 2)

        # buttons
        btn_1 = QtGui.QPushButton('OK')
        btn_1.clicked.connect(self.submit)
        btn_2 = QtGui.QPushButton('Cancel')
        btn_2.clicked.connect(self.close)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(btn_1)
        hbox.addWidget(btn_2)
        grid.addLayout(hbox, 5, 0, 1, 3)

        self.setLayout(grid)
        self.show()
    #
    def edit_proband_id(self):
        self._proband_id = self.sender().text()

    def edit_age(self):
        self._age = self.sender().text()

    def edit_proj(self):
        """
        Sets the project ID.
        """
        self._proj_id = self.sender().currentText()

    def edit_user(self):
        """
        Sets the project ID.
        """
        self._user_id = self.sender().currentText()

    def submit(self):

        if not self._proband_id:
            s = 'Invalid proband ID.'
            _ = QtGui.QMessageBox()
            _.setText(s)
            _.exec_()
            return None

        if self.rbs[0].isChecked():
            self._sex = 'Male'
        elif self.rbs[1].isChecked():
            self._sex = 'Female'
        else:
            s = 'Sex not selected.'
            a = QtGui.QMessageBox()
            a.setText(s)
            a.exec_()
            return None

        try:
            self._age = int(self._age)
            if self._age < 15:
                s = 'Proband must be over 15.'
                _ = QtGui.QMessageBox()
                _.setText(s)
                _.exec_()
                return None
        except:
            s = 'Invalid age.'
            _ = QtGui.QMessageBox()
            _.setText(s)
            _.exec_()
            return None

        if not self._proj_id:
            s = 'Invalid proband ID.'
            _ = QtGui.QMessageBox()
            _.setText(s)
            _.exec_()
            return None

        if not self._user_id:
            s = 'Invalid user ID.'
            _ = QtGui.QMessageBox()
            _.setText(s)
            _.exec_()
            return None

        if self.new_proband and self._proband_id in self.df.index.tolist():
            s = 'Proband with this ID already exists.'
            _ = QtGui.QMessageBox()
            _.setText(s)
            _.exec_()
            return None

        self.proband.proband_id = self._proband_id
        self.proband.sex = self._sex
        self.proband.age = self._age
        self.proband.proj_id = self._proj_id
        self.proband.user_id = self._user_id

        self.df.loc[self._proband_id] = self.proband
        data.replace_demographics(self.df)
        self.com.update_proband_table.emit()
        self.close()


class CustomSignals(QtCore.QObject):

    update_proband_table = QtCore.Signal()