# -*- coding: utf-8 -*-
import os
import json
import jinja2
from google.appengine.api import memcache
from jinja2 import Template
from bottle import Bottle, request, response, static_file
from bottle import TEMPLATE_PATH as T


PROJECT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
STATIC_PATH = os.path.join(PROJECT_PATH, 'assets')

T.insert(0, TEMPLATE_PATH)

app = Bottle()


@app.route('/')
def index():

    def file_exist(file):
        return os.path.isfile("{}/images/logo/{}.png".format(
            STATIC_PATH, file))

    def bundle_list(file_name):
        return ",".join(open(file_name).read().replace("/", "\/").split("\n"))

    langs = memcache.get('langs')
    if not langs:
        langs = os.listdir("./vim_template/langs")
        memcache.add('langs', langs, 3600)

    awesomevim = json.loads(open("./awesomevim.json").read())
    plugins = {}
    for l in langs:
        file_name = "./vim_template/langs/{}/bundle.list".format(l)
        plugins[l] = ""
        if os.path.exists(file_name):
            plugins[l] = bundle_list(file_name)

    template = JINJA_ENVIRONMENT.get_template('index.html')
    return template.render({'langs': langs, 'file_exist': file_exist,
                            "awesomevim": awesomevim,
                            "plugins": plugins})


@app.route('/generate.vim', method='POST')
def generate():
    editor = request.POST.get("editor", "vim")
    langs = {"vim": {}, "editor": editor}
    langs["bundle"] = request.POST.getall('plugins')
    select_lang = request.POST.getall('langs')
    for l in select_lang:

        data = memcache.get('vim-{}'.format(l))
        if not data:
            cache = {}
            for ext in ["vim"]:
                with open("./vim_template/langs/{0}/{0}.{1}".format(
                        l, ext)) as f:
                    cache[ext] = langs[ext][l] = f.read()
            memcache.add('vim-{}'.format(l), cache, 3600)
        else:
            langs["vim"][l] = data['vim']

    template = None
    with open("./vim_template/vimrc") as f:
        template = Template(f.read().decode('utf-8'))

    if not template:
        template = Template("")

    response.headers['Content-Type'] = 'application/text'
    response.headers['Content-Disposition'] = 'attachment; \
            filename=.{}rc'.format(editor)
    langs['select_lang'] = ",".join(select_lang)
    return template.render(**langs)


@app.route('/langs')
def langs():

    langs = memcache.get('langs')
    if not langs:
        langs = os.listdir("./vim_template/langs")
        memcache.add('langs', langs, 3600)

    return ",".join(langs)


@app.route('/robots.txt')
def serve_robots():
    return static_file('robots.txt', root=STATIC_PATH)


@app.route('/assets/<path:path>', name='assets')
def static(path):
    yield static_file(path, root=STATIC_PATH)


@app.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.'
