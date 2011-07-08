#!/usr/bin/pathon
import sys, os, time
from datetime import datetime
import hashlib
import web
import mimetypes
import re
import markdown
import urllib
import json
from web import form

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import model

db = web.database(dbn="mysql", db="wiki", user="root", pw="cds")
store = web.session.DBStore(db, 'sessions')

web.config.debug = False;
web.config.db_parameters = {
            'dbn':'sqlite',
            'db': 'db.sqlite'
        }

urls = (
    '/', 'Home',
    '/static/(.+)', 'StaticFilesHandler',
    '/login', 'Login',
    '/logout', 'Logout',
    '/index', 'Index',
    '/new', 'NewPage',
    '/edit/(\d+)', 'EditPage',
    '/delete/(\d+)', 'delete',
    '/history/(\d+)', 'History',
    '/ajax', 'Ajax',
    '/(.+)', 'Wiki'
    )

app = web.application(urls, globals())
session = web.session.Session(app, store, initializer={'count': 0})

t_globals = {
            'session': session,
            'wwwroot': '',
            'markdown': markdown.Markdown(
                extensions = ['wikilinks', 'tables', 'fenced_code'],
                extension_configs = {
                    'wikilinks': [
                        ('base_url', ''),
                        ('end_url', ''),
                        ('html_class', 'wiki_link')
                        ]
                    }
                )
            }
render = web.template.render('templates', base='base', globals=t_globals)
wiki_form = form.Form(
    web.form.Textbox('title', web.form.notnull, description="Page title:"),
    web.form.Textarea('content', web.form.notnull, rows=20, description="Page content:"),
    web.form.Button('Create page'),
)

class StaticFilesHandler:
    def GET(self, filename):
        web.header('Content-type', mimetypes.guess_type(filename)[0])
        string = open(abspath + '/static/' + filename, 'r').read()
        return string


class NewPage:
    def GET(self):
        title = web.input(title='').title
        form = wiki_form()
        form.fill({'title':title})
        return render.new(form)

    def POST(self):
        form = wiki_form()
        if not form.validates():
            return render.new(form)
        model.create_page(form.d.title, form.d.content)
        raise web.seeother('/index')

class EditPage:
    form = form.Form(
        web.form.Textbox('title', web.form.notnull, description="Page title:"),
        web.form.Textarea('content', web.form.notnull, rows=20, description="Page content:"),
        web.form.Button('Edit page'),
    )
    def GET(self, pageid):
        page = model.get_page_by_id(pageid)
        form = self.form()
        form.fill(page)
        return render.edit(page, form)

    def POST(self, pageid):
        form = self.form()
        page = model.get_page_by_id(int(pageid))
        if not form.validates():
            return render.edit(page, form)
        model.update_page(int(pageid), form.d.title, form.d.content)
        raise web.seeother('/'+form.d.title)

class History:
    def GET(self, pageid):
        return 'Come back later'

class Wiki:
    def GET(self, pagename):
        session.count += 1
        pagename = urllib.unquote_plus(pagename)
        page = model.get_page_by_title(pagename)
        if not page:
            raise web.seeother('/new?title=%s' % web.websafe(pagename))
        else:
            """
             p = re.compile( '(blue|white|red)')
             >>> p.sub( 'colour', 'blue socks and red shoes')
             'colour socks and colour shoes'
            """
            page.created = datetime.fromtimestamp(float(page.created))
            page.modified = datetime.fromtimestamp(float(page.modified))
            page.title = pagename
            return render.wiki(page=page)

class Home:
    def GET(self):
        raise web.seeother('/home')

class Index:
    def GET(self):
        pages = model.get_pages()
        return render.index(pages=pages)

class Login:
    form = form.Form(
        web.form.Textbox('username', web.form.notnull, description="Username"),
        web.form.Textbox('password', web.form.notnull, description="Password"),
        web.form.Button('Login'),
    )
    def GET(self):
        form = self.form()
        return render.login(form)

    def POST(self):
        i = web.input()
        pwdhash = hashlib.md5(i.password).hexdigest()
        check = db.where('users', username=i.username, password=pwdhash)
        if check:
            session.loggedin = True
            session.username = i.username
            raise web.seeother('/')
        else:
            return 'Failed'
            raise web.seeother('/failed')

class Logout:
    def GET(self):
        session.kill()
        raise web.seeother('/');


class delete:
    def GET(self, todoid):
        db.delete('todo', where='id='+todoid)
        raise web.seeother('/');

class Ajax:
    def GET(self):
        pages = []
        records = model.get_pages()
        for record in records:
            page = {}
            page['text'] = record['title']
            pages.append(page);
        return json.dumps(pages);
    def POST(self):
        pages = []
        records = model.get_pages()
        for record in records:
            page = {}
            page['text'] = "<a href='"+t_globals['wwwroot']+record['title']+"'>" + record['title'] + "</a>"
            pages.append(page);
        return json.dumps(pages);

application = app.wsgifunc()

#app = web.application(urls, globals())

#app.wsgifunc()
