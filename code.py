#!/usr/bin/pathon
import sys, os, time
from datetime import datetime
import hashlib
import web
import mimetypes
import re
import markdown
from creole import creole2html
import urllib
from web import form

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import model

web.config.debug = True;
web.config.db_parameters = {
            'dbn':'sqlite',
            'db': 'db.sqlite'
        }

urls = (
    '/', 'Home',
    '/static/(.+)', 'StaticFilesHandler',
    '/login', 'login',
    '/index', 'Index',
    '/new', 'NewPage',
    '/edit/(\d+)', 'EditPage',
    '/delete/(\d+)', 'delete',
    '/history/(\d+)', 'History',
    '/(.+)', 'Wiki'
    )

app = web.application(urls, globals())

t_globals = {
            'wwwroot': '',
            'markdown': markdown.Markdown(
                extensions = ['wikilinks'],
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
            return render.wiki(page=page)

class Home:
    def GET(self):
        raise web.seeother('/home')

class Index:
    def GET(self):
        pages = model.get_pages()
        return render.index(pages=pages)

class login:
    def POST(self):
        i = web.input()
        pwdhash = hashlib.md5(i.password).hexdigest()
        check = db.where('users', username=i.username, password=pwdhash)
        if check:
            #session.loggedin = True
            #session.username = i.username
            raise web.seeother('/loggedin')
        else:
            raise web.seeother('/failed')


class delete:
    def GET(self, todoid):
        db.delete('todo', where='id='+todoid)
        raise web.seeother('/');

application = app.wsgifunc()

#app = web.application(urls, globals())

#app.wsgifunc()
