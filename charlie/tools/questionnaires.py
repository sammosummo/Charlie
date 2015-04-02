"""
Administers a set of questionnaires.

"""

__version__ = 0.1
__author__ = 'Sam Mathias'


from datetime import datetime
from copy import copy
import cPickle
import sqlite3
import sys
import webbrowser
import numpy as np
import pandas
import web
import charlie.tools.data as data
import charlie.tools.summaries as summaries
import charlie.tools.arguments as arguments
import charlie.tools.questionnaire_process as qp
from os import listdir


class Index:
    """
    Web application. This is essentially just one web page containing the
    questionnaires and a submit button. Once submit is clicked, the data
    are transferred to the local database and the application is stopped.
    """
    def GET(self):
        # HACK!!!! See description below---------------------------------------
        sys.argv = original_args
        # ---------------------------------------------------------------------
        render = web.template.render(data.QUESTIONNAIRE_TEMPLATES_PATH)
        return render._questionnaires()

    def POST(self):
        dfs = qp.process_form_data(web.input())
        sys.exit(0)


def create_questionnaire_app(questionnaires, lang):
    """
    Creates a local web application for collecting self-report questionnaire
    data. The web page should open in a new browser window or tab
    automatically. If it does not open at all, the URL can be found in the
    terminal window.
    """
    abs_f = lambda f: data.pj(data.QUESTIONNAIRE_TEMPLATES_PATH, f)
    files = ['%s_%s.html' % (q, lang) for q in questionnaires]
    files = [abs_f(f) for f in files]
    form_code = ''.join(open(q, 'rU').read() for q in files)
    html_code = open(abs_f('template.html'), 'rU').read()
    html_code = html_code % ('Self-report questionnaires', form_code)
    open(abs_f('_questionnaires.html'), 'w').write(html_code)

    # MAJOR HACK!!!!!----------------------------------------------------------
    # webpy always takes the first command-line argument as the port number,
    # which is not what we want here. Therefore it is necessary to remove all
    # arguments from the command line temporarily, then reinstate them after
    # the web server has been initialised. This is horrible, but I don't see
    # any other way around it.

    global original_args
    original_args = copy(sys.argv)
    sys.argv = sys.argv[0:1]

    # -------------------------------------------------------------------------

    urls = ('/', 'Index')
    dic = {'Index': Index}
    app = web.application(urls, dic, True)
    webbrowser.open('http://localhost:8080/')
    app.run()
    print '---Please navigate to print http://localhost:8080/ if your browser does not do so automatically.'


def get_available_questionnaires(lang):
    """
    Returns a list of questionnaires available in the given language.
    """
    s = '_' + lang + '.html'
    files = listdir(data.QUESTIONNAIRE_TEMPLATES_PATH)
    f = lambda q: q.split('_')[0]
    return [f(q) for q in files if s in q]


def get_available_questionnaire_lists():
    """
    Returns a list of questionnaire lists.
    """
    s = '.txt'
    files = listdir(data.QUESTIONNAIRES_PATH)
    f = lambda q: q.strip(s)
    return [f(q) for q in files if s in q]


def questionnaires_in_list(q):
    """
    Returns a list of the questionnaires within a given questionnaire list
    file.
    """
    _q = open(data.pj(data.QUESTIONNAIRES_PATH, q + '.txt'), 'rU').readlines()
    quickfix = lambda f: f.replace('\n', '').replace('\r', '')
    qlist = [quickfix(l) for l in _q]
    return qlist