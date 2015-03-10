__author__ = 'smathias'

try:
    from PySide import QtGui, QtCore
    from PySide.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PySide.QtGui import QTableView, QApplication
except ImportError:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
    from PyQt4.QtGui import QTableView, QApplication
import charlie.tools.data as data


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

        (self.probands_list,
         self.users_list,
         self.projects_list) = data.populate_demographics()

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


        self.setup_ui()

    def setup_ui(self):

        widgets = []  # for easier layout management, all widgets in this list
        a = QtGui.QLabel(self.instr[3])
        widgets.append(a)

        # project and user boxes
        b = QtGui.QGroupBox(self.instr[4])
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(self.instr[5]), 0, 0)
        proj_list = QtGui.QComboBox()
        proj_list.setItemText(0, self.proj_id)
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
        widgets.append(b)

        # proband box
        c = QtGui.QGroupBox(self.instr[8])
        cols = 5
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(self.instr[9]), 0, 0, 1, cols)
        grid.addWidget(QtGui.QLabel(self.instr[10]), 1, 0)
        self.proband_id_label = QtGui.QLabel()
        self.set_text()
        grid.addWidget(self.proband_id_label, 1, 1, 1, cols-1)
        # self.view.setFont(QtGui.QFont("Courier New", 14))
        # self.view.resizeColumnsToContents()

        grid.addWidget(self.view, 2, 0, 1, cols)
        funcs = [
            self.select_proband, self.deselect_proband, self.edit_proband,
            self.new_proband, self.test_proband
        ]
        for i, func in enumerate(funcs):
            button = QtGui.QPushButton(self.instr[11+i])
            button.clicked.connect(func)
            grid.addWidget(button, 3, i)
        c.setLayout(grid)
        widgets.append(c)

        vbox = QtGui.QVBoxLayout()
        [vbox.addWidget(w) for w in widgets]
        self.setLayout(vbox)

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
        self.w = ProbandWindow(self.proband_id, self.model, self.view)
        # self.w.com.update_proband_table.connect(self.model.load_data)
        # self.w.show()


class ProbandWindow(QtGui.QWidget):

    """
    Proband edit/creation window. This pops up as a separate window from the
    manager. Includes proband ID, sex, and dob. The project and experimenter
    IDs are inherited from the the main window, so this is impossible if these
    fields are left blank.
    """

    def __init__(self, proband_id, model, view, parent=None):
        super(ProbandWindow, self).__init__(parent=parent)
        print model.data()

        # Load in the proband etc.
        db = tools.db
        self.proband = proband
        self.fields = db.PROBAND_ORDER
        self.field_descriptions = [db.FIELD_DESCRIPTIONS[f] \
                                   for f in self.fields]

        # Create a blank proband dict if needed
        if not self.proband:
            self.proband = dict(zip(self.fields, ['']*len(self.fields)))
            self.proband['createdby'] = experimenter
            self.proband['project'] = project
        self.proband['modifiedby'] = experimenter

        self.com = CustomSignals()
        self.setup_ui()


    def setup_ui(self):

        self.setWindowTitle(instructions[20])
        cols = 3
        grid = QtGui.QGridLayout()

        # Proband ID (not editable if existing proband loaded)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[0]+':'), 0, 0, 1,
                       cols)
        if not self.proband['id']:
            self.proband_id_box = QtGui.QLineEdit(self.proband['id'])
            self.proband_id_box.textEdited.connect(self.edit_proband_id)
        else:
            self.proband_id_box = QtGui.QLabel('<b>%s</b>' %self.proband['id'])
        grid.addWidget(self.proband_id_box, 1, 0, 1, cols)

        # Sex radio buttons
        grid.addWidget(QtGui.QLabel(self.field_descriptions[2]+':'), 2, 0)
        self.male = QtGui.QRadioButton('Male')
        if self.proband['sex'] == 'male':
            self.male.toggle()
        self.female = QtGui.QRadioButton('Female')
        if self.proband['sex'] == 'female':
            self.female.toggle()
        grid.addWidget(self.male, 2, 1)
        grid.addWidget(self.female, 2, 2)

        # Dob calendar
        grid.addWidget(QtGui.QLabel(self.field_descriptions[3]+':'), 3, 0, 1,
                       cols)
        self.calendar = QtGui.QCalendarWidget()
        dob = self.proband['dob']
        if dob:
            date = QtCore.QDate(*[int(d) for d in dob.split('-')])
            self.calendar.setSelectedDate(date)
        grid.addWidget(self.calendar, 4, 0, 1, cols)
        button = QtGui.QPushButton(instructions[22])
        button.clicked.connect(self.update_proband)
        grid.addWidget(button, 20, 0, 1, cols)

        # Otheer fields are displayed just for completeness
        grid.addWidget(QtGui.QLabel(self.field_descriptions[4]+':'), 5, 0, 1,
                       2)
        grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['createdby']), 5,
                       2, 1, 1)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[5]+':'), 6, 0, 1,
                       2)
        grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['created']), 6,
                       2, 1, 1)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[6]+':'), 7, 0, 1,
                       2)
        grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['modifiedby']),
                       7, 2, 1, 1)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[7]+':'), 8, 0, 1,
                       2)
        grid.addWidget(QtGui.QLabel('<b>%s</b>' %self.proband['modified']), 8,
                       2, 1, 1)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[8]+':'), 9, 0, 1,
                       2)
        l = self.proband['started'].split(',')
        if len(l) > 3:
            s = '\n'.join(l[:4]) + '... + %i more' %(len(l)-3)
        else:
            s = '\n'.join(l)
        grid.addWidget(QtGui.QLabel(s), 9, 2, 1, 1)
        grid.addWidget(QtGui.QLabel(self.field_descriptions[9]+':'), 10, 0, 1,
                       2)
        l = self.proband['completed'].split(',')
        if len(l) > 3:
            s = '\n'.join(l[:4]) + '... + %i more' %(len(l)-3)
        else:
            s = '\n'.join(l)
        grid.addWidget(QtGui.QLabel(s), 10, 2, 1, 1)
        self.setLayout(grid)
        self.show()

    def edit_proband_id(self):
        """Edits the proband ID (if new proband)."""
        self.proband['id'] = self.sender().text()

    def update_proband(self):
        """Updates the proband information in the table."""
        if self.check_data():
            tools.db.insert('probands', self.proband)
            self.com.update_proband_table.emit()
            self.close()

    def check_data(self):
        """Check that the proband details are all ok."""
        if not self.proband['id']:
            s = instructions[23]
            a = QtGui.QMessageBox()
            a.setText(s)
            a.exec_()
            return False
        if self.male.isChecked():
            self.proband['sex'] = 'male'
        elif self.female.isChecked():
            self.proband['sex'] = 'female'
        else:
            s = instructions[24]
            a = QtGui.QMessageBox()
            a.setText(s)
            a.exec_()
            return False
        d = self.calendar.selectedDate().toPython()
        dob = self.calendar.selectedDate().toString('yyyy-MM-dd')
        age = self.calculate_age(d)
        if age < 15:
            s = instructions[25]
            a = QtGui.QMessageBox()
            a.setText(s)
            a.exec_()
            return False
        else:
            self.proband['dob'] = dob
            return True

    def calculate_age(self, born):
        """Calculates someone's age in years."""
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < \
                                         (born.month, born.day))

    def closeEvent(self, event):
        """Closes the window and updates the table."""
        self.com.update_proband_table