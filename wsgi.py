#!/usr/bin/pathon
import sys, os, time
from datetime import datetime
import hashlib
import mimetypes
import re
import urllib
import json

# Third party lib
import markdown
import web
# web.py form util
from web import form

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

from models import page

# setup db
db = web.database(dbn="mysql", db="wiki", user="root", pw="cds")
store = web.session.DBStore(db, 'sessions')

web.config.debug = False;
web.config.db_parameters = {
            'dbn':'mysql',
            'db': 'wiki'
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
    '/version/(\d+)', 'Version',
    '/tags', 'Tags',
    '/tag/(.+)', 'Tag',
    '/user/(.+)', 'User',
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

class StaticFilesHandler:
    def GET(self, filename):
        web.header('Content-type', mimetypes.guess_type(filename)[0])
        string = open(abspath + '/static/' + filename, 'r').read()
        return string

class NewPage:
    wiki_form = form.Form(
        web.form.Textbox('title', web.form.notnull, description="Title:"),
        web.form.Textarea('content', web.form.notnull, rows=20, description="Content:"),
        web.form.Button('Create page'),
    )

    def GET(self):
        title = web.input(title='').title
        form = self.wiki_form()
        form.fill({'title':title})
        return render.new(form)

    def POST(self):
        form = self.wiki_form()
        if not form.validates():
            return render.new(form)
        page.create_page(form.d.title, form.d.content)
        raise web.seeother('/index')

class EditPage:
    form = form.Form(
        web.form.Textbox('title', web.form.notnull, description="Title:"),
        web.form.Textarea('content', web.form.notnull, rows=20, description="Content:"),
        web.form.Textbox('tags', description="Tags:"),
        web.form.Textbox('parent', description="Parent page:"),
        web.form.Button('Edit page'),
    )
    def GET(self, pageid):
        p = page.get_page_by_id(pageid)
        form = self.form()
        form.fill(p)
        return render.edit(p, form)

    def POST(self, pageid):
        form = self.form()
        p = page.get_page_by_id(int(pageid))
        if not form.validates():
            return render.edit(p, form)
        dbhash = hashlib.md5(p.content).hexdigest()
        formhash = hashlib.md5(form.d.content).hexdigest();
        if dbhash == formhash:
            return "no page content changes"
        else:
            p.update_page(int(pageid), form.d.title, form.d.content)
            raise web.seeother('/'+form.d.title)

class History:
    def GET(self, pageid):
        versions = page.get_page_versions(pageid)
        return render.history(versions=versions)

class Version:
    def GET(self, versionid):
        version = page.get_page_by_versionid(versionid)
        return render.version(version=version)

class Wiki:
    def GET(self, pagename):
        session.count += 1
        pagename = urllib.unquote_plus(pagename)
        p = page.get_page_by_title(pagename)
        if not p:
            raise web.seeother('/new?title=%s' % web.websafe(pagename))
        else:
            """
             p = re.compile( '(blue|white|red)')
             >>> p.sub( 'colour', 'blue socks and red shoes')
             'colour socks and colour shoes'
            """
            p.created = datetime.fromtimestamp(float(p.created))
            p.modified = datetime.fromtimestamp(float(p.modified))
            p.title = pagename
            return render.wiki(page=p)

class Home:
    def GET(self):
        raise web.seeother('/home')

class Index:
    def GET(self):
        pages = page.get_pages()
        return render.index(pages=pages)

class Login:
    form = form.Form(
        web.form.Textbox('username', web.form.notnull, description="Username"),
        web.form.Password('password', web.form.notnull, description="Password"),
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
        records = page.get_pages()
        for record in records:
            p = {}
            p['text'] = record['title']
            pages.append(p);
        return json.dumps(pages);
    def POST(self):
        pages = []
        records = page.get_pages()
        for record in records:
            p = {}
            p['text'] = "<a href='"+t_globals['wwwroot']+record['title']+"'>" + record['title'] + "</a>"
            pages.append(p);
        return json.dumps(pages);

if __name__ == '__main__':
    app.run
else:
    application = app.wsgifunc()
