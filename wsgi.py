#!/usr/bin/python
import sys, os, time
from datetime import datetime
from web.contrib.template import render_jinja
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
print abspath
os.chdir(abspath)

from models import page
from models import tag

# setup db
db = web.database(dbn="mysql", db="wiki", user="root", pw="cds")
store = web.session.DBStore(db, 'sessions')

web.config.debug = True;
web.config.db_parameters = {
    'dbn':'mysql',
    'db': 'wiki'
}

urls = (
    '/',             'Home',
    #'/static/(.+)', 'StaticFilesHandler',
    '/login',        'Login',
    '/logout',       'Logout',
    '/pages',        'Pages',
    '/new',          'NewPage',
    '/delete/(\d+)', 'delete',
    '/version/(\d+)','Version',
    '/tags',         'Tags',
    '/user/(.+)',    'User',
    '/edit/(\d+)',   'EditorController',
    '/history/(.+)', 'HistoryController',
    '/tag/(.+)',     'TagController',
    '/(.+)',         'WikiController'
)

app = web.application(urls, globals())
session = web.session.Session(app, store, initializer={'count': 0})

markdownengine = markdown.Markdown(
    extensions = ['wikilinks', 'tables', 'fenced_code'],
    extension_configs = {
        'wikilinks': [
            ('base_url', ''),
            ('end_url', ''),
            ('html_class', 'wiki_link')
        ]
    }
)

t_globals = {
    'session': session,
    'wwwroot': '',
}

#render = web.template.render('templates', base='base', globals=t_globals)
render = render_jinja('templates', encoding = 'utf-8', globals=t_globals)

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
        return render.new(form=form)

    def POST(self):
        form = self.wiki_form()
        if not form.validates():
            return render.new(form=form)
        page.create_page(form.d.title, form.d.content)
        raise web.seeother('/pages')

class EditorController:
    def GET(self, versionid):
        p = page.get_page_by_versionid(versionid)
        p.tags = tag.get_tags_by_title(p.title)
        return render.edit(page=p)

    def POST(self, versionid):
        wikipage = web.input()
        p = page.get_page_by_versionid(int(versionid))
        dbhash = hashlib.md5(p.content).hexdigest()
        formhash = hashlib.md5(wikipage.content).hexdigest();
        if dbhash == formhash:
            return "no page content changes"
        else:
            page.update_page(int(p.pageid), wikipage.title, wikipage.content, wikipage.message)
            raise web.seeother('/'+wikipage.title)

class HistoryController:
    def GET(self, pagename):
        versions = page.get_versions_by_title(pagename)
        return render.history(versions=versions, pagetypeclass="results")

class Version:
    def GET(self, versionid):
        version = page.get_page_by_versionid(versionid)
        return render.version(version=version)

class Pages:
    def GET(self):
        pages = page.get_pages()
        return render.index(pages=pages, pagetypeclass="results")

class WikiController:
    def GET(self, pagename):
        p = page.get_page_by_title(pagename)
        pagename = urllib.unquote_plus(pagename)

        tags = tag.get_tags_by_title(pagename)
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
            p.tags = tags
            p.content = markdownengine.convert(p.content)
            return render.wiki(page=p, pagetypeclass="page")

class TagController:
    def GET(self, tagname):
        pages = page.get_pages_by_tag(tagname)
        return render.tag(pages=pages, pagename="Tag: "+tagname, pagetypeclass="results")


class Home:
    def GET(self):
        raise web.seeother('/home')

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
    def POST(self):
        params = web.input()
        action = params.action
        pages = []
        records = page.get_pages()
        for record in records:
            p = {}
            p['title'] = record['title']
            pages.append(p);
        return json.dumps(pages);

if __name__ == '__main__':
    app.run()
else:
    application = app.wsgifunc()
