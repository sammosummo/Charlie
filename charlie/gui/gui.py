"""
Front-end GUI for Charlie.

"""
__version__ = 0.1
__author__ = 'smathias'

import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.arguments as arguments
import charlie.tools.data as data
import charlie.tools.instructions as instructions
from charlie.gui.setuptab import SetupTab
from charlie.gui.testtab import TestTab
from charlie.gui.qtab import QuestionnaireTab
from charlie.gui.batchtab import BatchTab
from charlie.gui.notestab import NotesTab
from charlie.gui.datatab import DataTab


class HomeWidget(QtGui.QWidget):

    """
    Main window widget.
    """

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent=parent)
        # data.populate_probands_table()
        self.args = arguments.get_args()
        self.instr = instructions.read_instructions('manager', self.args.lang)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.instr[0])
        vbox = QtGui.QVBoxLayout()

        pixmap = QtGui.QPixmap(data.pj(data.PACKAGE_DIR, 'charlie.png'))
        img = QtGui.QLabel()
        img.setPixmap(pixmap)
        img.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(img)

        txt = QtGui.QLabel(self.instr[1] % __version__)
        txt.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(txt)

        tabs = QtGui.QTabWidget()
        setup_tab = SetupTab(self)
        tabs.addTab(setup_tab, self.tr('Session setup'))
        batch_tab = BatchTab(self)
        tabs.addTab(batch_tab, self.tr('Batch'))
        test_tab = TestTab(self)
        tabs.addTab(test_tab, self.tr('Tests'))
        q_tab = QuestionnaireTab(self)
        tabs.addTab(q_tab, self.tr('Questionnaires'))

        notes_tab = NotesTab(self)
        tabs.addTab(notes_tab, self.tr('Notes'))
        data_tab = DataTab(self)
        tabs.addTab(data_tab, self.tr('Data transfer'))
        vbox.addWidget(tabs)

        self.setLayout(vbox)
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    _ = HomeWidget()
    app.exec_()


if __name__ == '__main__':
    main()