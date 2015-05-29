"""
Executing individual tests and batches of tests.
"""

import importlib
import os
import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore
import charlie.tools.arguments as arguments
import charlie.tools.data as data
import charlie.tools.instructions as instructions
import charlie.tools.questionnaires as questionnaires
import charlie.tools.misc as misc
import charlie.tools.visual as visual
import charlie.tools.backup as backup


class Test:

    """
    Test class. Initialised using the test_name, which must be a string with
    exactly the same name as a test in the test battery. Optionally supply a
    batch_mode bool.
    """

    def __init__(self, test_name, batch_mode=False, parent=None):

        print '---Test object initialised.'
        self.batch_mode = batch_mode
        args = arguments.get_args()
        self.test_name = test_name
        self.proband_id = args.proband_id
        self.user_id = args.user_id
        self.proj_id = args.proj_id
        self.lang = args.lang
        self.instr = instructions.read_instructions(self.test_name, self.lang)

        self.mod = importlib.import_module('charlie.tests.' + self.test_name)
        self.output_format = getattr(self.mod, 'output_format')
        self.control_method = getattr(self.mod, 'control_method')
        self._control = self.control_method(self.proband_id, self.instr)

        if hasattr(self.mod, 'trial_method'):
            self.user_controlled = False
        else:
            self.user_controlled = True

        print '---Creating a data object.'
        self.data_obj = data.load_data(
            self.proband_id,
            self.lang,
            self.user_id,
            self.proj_id,
            self.test_name,
            self.output_format
        )
        if not self.data_obj.control and not self.data_obj.data:
            print '---New proband detected.'
            self.data_obj.control = self._control
            self.data_obj.data = []
        else:
            print '---Previous data found for this proband in this test.'

    def run(self, from_gui=False):

        print '---Running test.'
        if self.user_controlled is False:
            return self.run_pygame()
        else:
            return self.run_qt(from_gui)

    def run_pygame(self):

        print '---This is a pygame test.'
        self.screen = visual.Screen()
        self.trial_method = getattr(self.mod, 'trial_method')

        if hasattr(self.mod, 'black_bg'):
            visual.BG_COLOUR = visual.BLACK
            visual.DEFAULT_TEXT_COLOUR = visual.WHITE
        else:
            visual.BG_COLOUR = visual.LIGHT_GREY
            visual.DEFAULT_TEXT_COLOUR = visual.BLACK

        img_path = data.pj(data.VISUAL_PATH, self.test_name)
        if os.path.exists(img_path):
            print '---Preloading images.'
            files = [data.pj(img_path, f) for f in os.listdir(img_path)]
            [self.screen.load_image(f) for f in files if misc.is_imgfile(f)]

        while self.data_obj.control:

            print '---New trial.'
            trial = self.data_obj.control.pop(0)
            trial_info = self.trial_method(self.screen, self.instr, trial)
            print trial_info

            if trial_info != 'EXIT':

                print '---Trial over.'
                if type(trial_info) == list:
                    self.data_obj.data += trial_info
                else:
                    self.data_obj.data.append(trial_info)

                if self.proband_id != 'TEST':
                    print '---Saving the data.'
                    self.data_obj.update()
                    self.data_obj.to_csv()

                if hasattr(self.mod, 'stopping_rule'):
                    stopping_rule = getattr(self.mod, 'stopping_rule')
                    if stopping_rule(self.data_obj):
                        print '---Stopping rule failed.'
                        self.data_obj.control = []

                if not self.data_obj.control:
                    print '---Test over.'
                    self.data_obj.test_done = True
                    if self.proband_id != 'TEST':
                        print '---Computing summary stats.'
                        summary_method = getattr(self.mod, 'summary_method')
                        self.data_obj.to_localdb(summary_method, self.instr)

            else:

                print '---Exit detected.'
                if self.batch_mode is False:
                    self.screen.kill()
                    break  # act as if the session is over

                else:
                    self.screen.kill()
                    return self.data_obj

        self.screen.kill()

    def run_qt(self, from_gui):

        if self.data_obj.test_done is False:

            if from_gui is False:

                screen = visual.Screen()
                screen.splash(self.instr[0])
                screen.kill()

                MainWindow = getattr(self.mod, 'MainWindow')
                app = QtGui.QApplication(sys.argv)
                app.aboutToQuit.connect(app.deleteLater)
                window = MainWindow(self.data_obj, self.instr)
                app.exec_()

            else:

                MainWindow = getattr(self.mod, 'MainWindow')
                self.window = MainWindow(self.data_obj, self.instr)
                self.window.raise_()


def run_batch():
    """
    Run a sequence of tests.
    """
    print '++++++++++\nBATCH MODE\n++++++++++\n'
    args = arguments.get_parser().parse_args()
    quickfix = lambda f: f.replace('\n', '').replace('\r', '')

    if args.questionnaires:
        print '---Loading questionnaires to administer first:'
        qlist = args.questionnaires.split()
        _qlist = []
        for q in qlist:
            try:
                _q = data.pj(data.QUESTIONNAIRES_PATH, q + '.txt')
                f = open(_q, 'rU').readlines()
                _qlist += f
            except:
                _qlist.append(q)
        qlist = [quickfix(l) for l in _qlist]
        print qlist
        questionnaires.create_questionnaire_app(qlist, args.lang)

    try:
        b = data.pj(data.BATCHES_PATH, args.batch_file + '.txt')
        f = open(b, 'rb')
    except:
        try:
            b = data.pj(data.BATCHES_PATH, args.batch_file)
            f = open(b, 'rb')
        except:
            b = data.BATCHES_PATH
            f = open(b, 'rb')

    test_names = [quickfix(l) for l in f]
    print '---Running the following tests in a batch:', test_names

    while test_names:

        test_name = test_names.pop(0)
        test = Test(test_name, True)
        _data_obj = test.run()
        print _data_obj

        if _data_obj is not None:

            choice = prompt()

            if choice == 'quit':

                sys.exit()

            elif choice == 'restart':

                data.delete_data(_data_obj)
                test_names = [test_name] + test_names

            elif choice == 'resume':

                test_names = [test_name] + test_names



def prompt():
    """
    Control-flow options.
    """
    msg = """
    ------------------------------------------------------------------
    PREMATURE EXIT DETECTED

    The previous test was exited before it was completed. Please type
    one of the following options to choose what to do next:

    resume     Resume the previous test from whenever it was exited.
               Usually, this means from the last trial the proband
               saw before exiting. However, for some tests (e.g., the
               IPCPTS), this means starting from the beginning of the
               last phase of trials. If you are running this batch
               script without a proband_id (i.e., in debug mode),
               'resume' is equivalent to 'restart'.

    restart    Start the previous test again, deleting any data
               previously collected from the proband in this test.

    skip       Move on to the next test in the batch, leaving the
               previous test incomplete. Note that summary statistics
               for incomplete tests will not appear in the local
               database.

    quit       Kill the batch.

    ------------------------------------------------------------------
    """
    print msg
    choices = ['resume', 'restart', 'skip', 'quit']
    choice = raw_input('Type an option >>>')
    if choice.lower() not in choices:
        print 'Not a valid option.'
        prompt()
    else:
        return choice


def get_available_batches():
    """
    Returns a list of batch files.
    """
    s = '.txt'
    files = data.ld(data.BATCHES_PATH)
    f = lambda q: q.strip(s)
    return [f(q) for q in files if s in q]


def tests_in_batch(b):
    """
    Returns a list of the tests within a given batch file.
    """
    _b = open(data.pj(data.BATCHES_PATH, b + '.txt'), 'rU').readlines()
    quickfix = lambda f: f.replace('\n', '').replace('\r', '')
    blist = [quickfix(l) for l in _b]
    return blist


def run_single_test(test_name):
    """
    Convenience function for running a single test.
    """
    test = Test(test_name)
    test.run()


def main():
    args = arguments.get_parser().parse_args()
    quickfix = lambda f: f.replace('\n', '').replace('\r', '')
    data.create_paths()
    data.create_db()

    if args.questionnaires:
        print '---Loading questionnaires to administer first:'
        qlist = args.questionnaires.split()
        _qlist = []
        for q in qlist:
            try:
                _q = data.pj(data.QUESTIONNAIRES_PATH, q + '.txt')
                f = open(_q, 'rU').readlines()
                _qlist += f
            except:
                _qlist.append(q)
        qlist = [quickfix(l) for l in _qlist]
        print qlist
        questionnaires.create_questionnaire_app(qlist, args.lang)
    if args.batch_file:
        run_batch()
    elif args.test_name:
        test = Test(args.test_name)
        test.run()
    backup.backup('sftp', 5)