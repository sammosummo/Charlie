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
        tabs.addTab(setup_tab, self.tr(self.instr[2]))
        # test_tab = TestTab(self)
        # tabs.addTab(test_tab, self.tr(self.instr[26]))
        vbox.addWidget(tabs)

        self.setLayout(vbox)
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    _ = HomeWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()