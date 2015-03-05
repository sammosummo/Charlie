__author__ = 'smathias'


import web
from os.path import abspath, dirname
import charlie.questionnaire_templates
f = dirname(abspath(charlie.questionnaire_templates.__file__))

urls = (
  '/', 'Index'
)

app = web.application(urls, globals())

render = web.template.render(f)

class Index(object):
    def GET(self):
        return render.hello_form()

    def POST(self):
        form = web.input(name="Nobody", greet="Hello")
        greeting = "%s, %s" % (form.greet, form.name)
        return render.confirmation(greeting = greeting)

if __name__ == "__main__":
    app.run()