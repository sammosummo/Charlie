"""
This is a rewrite of the batch module. This was necessary because it was
impossible to run Qt-based tests from the gui, because there can be only one Qt
application at one time.
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
import charlie.tools.misc as misc
import charlie.tools.visual as visual




class Test:

    def __init__(self, test_name, batch_mode=False, parent=None):
        super(Test, self).__init__(parent=parent)

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

        if not hasattr(self.mod, 'trial_method'):
            self.user_controlled = False
        else:
            self.user_controlled = True

        self.data_obj = data.load_data(
            self.proband_id,
            self.lang,
            self.user_id,
            self.proj_id,
            self.test_name,
            self.output_format
        )
        if not self.data_obj.control and not self.data_obj.data:
            self.data_obj.control = self._control
            self.data_obj.data = []

    def run(self, from_gui=False):

        if self.user_controlled is False:
            self.run_pygame()
        else:
            self.run_qt(from_gui)

    def run_pygame(self):

        self.screen = visual.Screen()
        self.trial_method = getattr(self.mod, 'trial_method')

        if hasattr(self.mod, 'black_bg'):
            visual.BG_COLOUR = visual.BLACK
            visual.DEFAULT_TEXT_COLOUR = visual.WHITE
        else:
            visual.BG_COLOUR = visual.LIGHT_GREY
            visual.DEFAULT_TEXT_COLOUR = visual.BLACK

        img_path = os.path.join(data.VISUAL_PATH, self.test_name)
        load = lambda f: self.screen.load_image(os.path.join(img_path, f))
        [load(f) for f in os.listdir(img_path) if misc.is_imgfile(f)]

        while self.data_obj.control:

            trial = self.data_obj.control.pop(0)
            trial_info = self.trial_method(self.screen, self.instr, self.trial)

            if trial_info != 'EXIT':

                if type(trial_info) == list:
                    self.data_obj.data += trial_info
                else:
                    self.data_obj.data.append(trial_info)

                if self.proband_id != 'TEST':
                    self.data_obj.update()
                    self.data_obj.to_csv()

                if hasattr(self.mod, 'stopping_rule'):
                    stopping_rule = getattr(self.mod, 'stopping_rule')
                    if stopping_rule(self.data_obj):
                        self.data_obj.control = []
                    else:
                        print 'passed.'

                if not self.data_obj.control:
                    self.data_obj.test_done = True
                    if self.proband_id != 'TEST':
                        summary_method = getattr(self.mod, 'summary_method')
                        self.data_obj.to_localdb(summary_method, self.instr)

            else:

                if self.batch_mode is False:
                    self.screen.kill()
                    break  # act as if the session is over

                else:
                    self.screen.kill()
                    return prompt(self.batch_mode), self.data_obj

    def run_qt(self, from_gui):

        if from_gui is False:

            screen = visual.Screen()
            screen.splash(self.instr[0])
            screen.kill()
#
        QtGui = getattr(self.mod, 'QtGui')
        MainWindow = getattr(self.mod, 'MainWindow')
        app = QtGui.QApplication(sys.argv)
        app.aboutToQuit.connect(app.deleteLater)
        window = MainWindow(self.data_obj, self.instr)
        app.exec_()



# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# """
# Created on Tue Jan  6 16:15:06 2015
#
#
# @author: Sam
# """
#
# import importlib
# import os
# from os.path import join as pj
# import sys
# import charlie.tools.instructions as instructions
# import charlie.tools.data as data
# import charlie.tools.visual as visual
# import charlie.tools.questionnaires as questionnaires
# import charlie.tools.arguments as arguments
# from os import listdir
#
#
# def run_a_test(test_name, batch_mode=False):
#     """
#     Initialises and runs a single test from the battery. The test script needs
#     to be present in the 'test' subdirectory.
#
#     This function loads the instructions in the specified language; checks to
#     see whether a pickled data object already exists for this proband on this
#     test; loads this object or creates a new one (along with a new control
#     iterable inside the object); creates a pygame screen; runs each trial until
#     the control iterable is empty; saves the data and computes summary
#     statistics; and finally calls the quit_single_test() function.
#
#     The function also optionally checks if the user exited the test (by hitting
#     escape) rather than exiting normally (when the control file is empty).  If
#     so, a prompt is displayed with various control-flow options.
#     """
#     print '--------' + ('-' * len(test_name))
#     print 'RUNNING %s' % test_name.upper()
#     print '--------' + ('-' * len(test_name)) + '\n'
#
#     # copy system arguments into local namespace
#     args = arguments.get_args()
#     proband_id = args.proband_id
#     user_id = args.user_id
#     proj_id = args.proj_id
#     lang = args.lang
#
#     # import the test module
#     mod = importlib.import_module('charlie.tests.' + test_name)
#     print '---Printing docstring for this test.'
#     print mod.__doc__
#
#     # load language-dependent task instructions
#     instr = instructions.read_instructions(test_name, lang)
#
#     # load data object
#     print '---Loading data from %s, if exists.' % proband_id
#     data_obj = data.load_data(proband_id,
#                               lang,
#                               user_id,
#                               proj_id,
#                               test_name,
#                               getattr(mod, 'output_format'))
#     if not data_obj.control and not data_obj.data:
#         print '---New proband detected.'
#         control_method = getattr(mod, 'control_method')
#         data_obj.control = control_method(proband_id, instr)
#         data_obj.data = []
#
#     # load the experimenter gui, if appropriate
#     if not hasattr(mod, 'trial_method'):
#
#         print '---No trial_method, must be an experimenter-operated test.'
#         if not threaded:
#             screen = visual.Screen()
#             screen.splash(instr[0])
#             screen.kill()
#
#         QtGui = getattr(mod, 'QtGui')
#         QtCore = getattr(mod, 'QtCore')
#         MainWindow = getattr(mod, 'MainWindow')
#         app = QtGui.QApplication.instance()
#         if not app: # create QApplication if it doesnt exist
#             app = QtGui.QApplication(sys.argv)
#             app.aboutToQuit.connect(app.deleteLater)
#             _ = MainWindow(data_obj, instr)
#     #            sys.exit(app.exec_())
#             app.exec_()
#
#     # set up a normal pygame session
#     else:
#
#         print '---Loading Pygame, etc..'
#
#         # make screen and load all images
#         screen = visual.Screen()
#         if hasattr(mod, 'black_bg'):
#             visual.BG_COLOUR = visual.BLACK
#             visual.DEFAULT_TEXT_COLOUR = visual.WHITE
#         else:
#             visual.BG_COLOUR = visual.LIGHT_GREY
#             visual.DEFAULT_TEXT_COLOUR = visual.BLACK
#         p = pj(data.VISUAL_PATH, test_name)
#         imgfs = ['.png', '.jpg', '.gif', '.bmp']
#         if os.path.exists(p):
#             print '---Loading visual stimuli.'
#             imgs = [f for f in data.ld(p) if f[-4:].lower() in imgfs]
#             [screen.load_image(pj(p, i)) for i in imgs]
#
#         # run trials
#         while data_obj.control:
#
#             print '---Running new trial.'
#             t = data_obj.control.pop(0)
#             trial_method = getattr(mod, 'trial_method')
#             trial_info = trial_method(screen, instr, t)
#
#             # record the outcome of the trial
#             if trial_info != 'EXIT':
#
#                 if type(trial_info) == list:
#                     data_obj.data += trial_info
#                 else:
#                     data_obj.data.append(trial_info)
#
#                 if proband_id != 'TEST':
#                     print '---Saving and writing csv.'
#                     data_obj.update()
#                     data_obj.to_csv()
#
#                 # check for a stopping rule
#                 if hasattr(mod, 'stopping_rule'):
#                     stopping_rule = getattr(mod, 'stopping_rule')
#                     print '--Testing stopping rule ...',
#                     if stopping_rule(data_obj):
#                         print 'failed.'
#                         data_obj.control = []
#                     else:
#                         print 'passed.'
#
#                 # check for remaining trials
#                 if not data_obj.control:
#                     print '---No more trials in the queue.'
#                     data_obj.test_done = True
#                     if proband_id != 'TEST':
#                         print '---Computing summary stats.'
#                         summary_method = getattr(mod, 'summary_method')
#                         data_obj.to_localdb(summary_method, instr)
#
#             # premature exit
#             else:
#
#                 print "---'EXIT' detected."
#                 if not batch_mode:
#                     screen.kill()
#                     break  # act as if the session is over
#
#                 else:
#                     screen.kill()
#                     return prompt(batch_mode), data_obj
#     print '---All trials done.\n---------'
#     print 'TEST OVER'
#     print '---------'
#     screen.kill()
#     return None, data_obj
#
#
# def run_a_batch():
#     """
#     Run a sequence of tests. The command-line option -b must be a text file
#     containing the names of the tests to be included in the batch, in the order
#     they should be run.
#     """
#     print '++++++++++\nBATCH MODE\n++++++++++\n'
#     args = arguments.get_parser().parse_args()
#     quickfix = lambda f: f.replace('\n', '').replace('\r', '')
#
#     if args.questionnaires:
#         print '---Loading questionnaires to administer first:'
#         qlist = args.questionnaires.split()
#         _qlist = []
#         for q in qlist:
#             try:
#                 _q = data.pj(data.QUESTIONNAIRES_PATH, q + '.txt')
#                 f = open(_q, 'rU').readlines()
#                 _qlist += f
#             except:
#                 _qlist.append(q)
#         qlist = [quickfix(l) for l in _qlist]
#         print qlist
#         questionnaires.create_questionnaire_app(qlist, args.lang)
#     try:
#         b = data.pj(data.BATCHES_PATH, args.batch_file + '.txt')
#         f = open(b, 'rb')
#     except:
#         try:
#             b = data.pj(data.BATCHES_PATH, args.batch_file)
#             f = open(b, 'rb')
#         except:
#             b = data.BATCHES_PATH
#             f = open(b, 'rb')
#
#     test_names = [quickfix(l) for l in f]
#     print '---Running the following tests in a batch:', test_names
#
#     for test_name in test_names:
#
#         repeat = True
#         while repeat:
#
#             choice, data_obj = run_a_test(test_name, True)
#
#             if not choice or choice == 'skip':
#
#                 repeat = False
#
#             elif choice == 'quit':
#
#                 sys.exit()
#
#             elif choice == 'restart':
#
#                 data.delete_data(data_obj)
#
#
# def prompt(batch_mode):
#     """
#     Control-flow options.
#     """
#     msg = """
#     ------------------------------------------------------------------
#     PREMATURE EXIT DETECTED
#
#     The previous test was exited before it was completed. Please type
#     one of the following options to choose what to do next:
#
#     resume     Resume the previous test from whenever it was exited.
#                Usually, this means from the last trial the proband
#                saw before exiting. However, for some tests (e.g., the
#                IPCPTS), this means starting from the beginning of the
#                last phase of trials. Also, if you are running this
#                batch script without a proband_id (i.e., in debug
#                mode), 'resume' is equivalent to 'restart'.
#
#     restart    Start the previous test again, deleting any data
#                previously collected from the proband in this test.
#
#     skip       Move on to the next test in the batch, leaving the
#                previous test incomplete. Note that summary statistics
#                for incomplete tests will not appear in the localdb.
#
#     quit       Kill the batch.
#
#     ------------------------------------------------------------------
#     """
#     print msg
#     choices = ['resume', 'restart', 'skip', 'quit']
#     choice = raw_input('Type an option >>>')
#     if choice.lower() not in choices:
#         print 'Not a valid option.'
#         prompt(batch_mode)
#     else:
#         return choice
#
#
# def get_available_batches():
#     """
#     Returns a list of batch files.
#     """
#     s = '.txt'
#     files = listdir(data.BATCHES_PATH)
#     f = lambda q: q.strip(s)
#     return [f(q) for q in files if s in q]
#
#
# def tests_in_batch(b):
#     """
#     Returns a list of the tests within a given batch file.
#     """
#     _b = open(data.pj(data.BATCHES_PATH, b + '.txt'), 'rU').readlines()
#     quickfix = lambda f: f.replace('\n', '').replace('\r', '')
#     blist = [quickfix(l) for l in _b]
#     return blist
#
#
# def main():
#     """
#     Main function.
#     """
#     args = arguments.get_parser().parse_args()
#     if args.batch_file:
#         run_a_batch()
#     elif args.test_name:
#         run_a_test(args.test_name)
#
#
# if __name__ == '__main__':
#     main()