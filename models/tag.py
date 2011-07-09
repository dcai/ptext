#!/usr/bin/python

import web
import time

#db = web.database(dbn="sqlite", db="db.sqlite")
db = web.database(dbn="mysql", db="wiki", user="root", pw="cds")

def get_tags():
    return db.select('tags', order='id DESC')

def get_tags_by_title(title):
    try:
        sql = """SELECT t.name
                   FROM pages p
                   JOIN tag_relationships tr
                        ON tr.pageid = p.id
                   JOIN tags t
                        ON t.id = tr.tagid
                  WHERE p.title = """ + web.sqlquote(title) + """
               ORDER BY t.id DESC"""
        tags = db.query(sql)
        return tags
    except IndexError:
        return None

def get_tag_by_id(pageid):
    try:
        sql = """SELECT p.id, p.created, p.title, v.content, v.version, v.created AS modified
                   FROM versions v
                   JOIN pages p
                        ON v.pageid = p.id
                  WHERE p.id = """ + web.sqlquote(pageid) + """
               ORDER BY version DESC"""
        pages = db.query(sql)
        page = pages[0]
        if not page.modified:
            page.modified = 0
        if not page.created:
            page.created = 0
        return page
    except IndexError:
        return None

def create_tag(title, content):
    created = time.time()
    modified = created
    page = get_page_by_title(title)
    if not page:
        pageid = db.insert('pages', title=title, created=created, modified=modified)
        db.insert('versions', content=content, format="markdown", created=created, pageid=pageid, version=1)
    else:
        db.insert('versions', content=page.content, format="markdown", created=created, pageid=page.id, version=1)

def delete_tag(pageid):
    db.delete('pages', where="id=$pageid")

def update_tag(pageid, title, text):

    sql = "SELECT MAX(v.version) AS version FROM versions v WHERE v.pageid = " + str(pageid)
    versions = db.query(sql)
    version = versions[0]
    version = (int(version.version) + 1)

    created = time.time()
    modified = created

    # update modified date
    db.update('pages', where="id=$pageid", vars=locals(), modified=modified)
    db.insert('versions', content=text, format="markdown", created=created, pageid=pageid, version=version)
