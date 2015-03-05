"""
Administers a set of questionnaires.

"""

__version__ = 0.1
__author__ = 'Sam Mathias'


import web
import webbrowser
import charlie.tools.data as data


render = web.template.render(data.QUESTIONNAIRE_TEMPLATES_PATH)


def make_web_page(test_name, questionnaires, lang):
    """
    Creates a new web page called _questionnaires.html within the
    questionnaire_templates subfolder. This is later loaded as a template using
    web.py.
    """
    abs_f = lambda f: data.pj(data.QUESTIONNAIRE_TEMPLATES_PATH, f)
    files = ['%s_%s.html' % (q, lang) for q in questionnaires]
    files = [abs_f(f) for f in files]
    form_code = ''.join(open(q, 'rU').read() for q in files)
    html_code = open(abs_f('template.html'), 'rU').read()
    html_code = html_code % (test_name, form_code)
    open(abs_f('_questionnaires.html'), 'w').write(html_code)


class Index:
    """
    Basic web.py object.
    """
    def GET(self):
        return render._questionnaires()

    def POST(self):
        form = web.input()
        return render.confirmation()
        app.stop()


def make_app(test_name, questionnaires, lang):
    """
    Returns a web.py app object.
    :return: app
    """
    make_web_page(test_name, questionnaires, lang)

    urls = ('/', 'Index')
    return web.application(urls, globals(), True)


if __name__ == "__main__":
    webbrowser.open('http://0.0.0.0:8080/')
    app = make_app()
    app.run()
