#!/usr/bin/python

import web
import time

#db = web.database(dbn="sqlite", db="db.sqlite")
db = web.database(dbn="mysql", db="wiki", user="root", pw="cds")

def get_pages():
    return db.select('pages', order='id DESC')

def get_page_versions(pageid):
    sql = """SELECT v.id, p.id AS pageid, p.created, p.title, v.content, v.version, v.created AS modified
               FROM versions v
               JOIN pages p
                    ON v.pageid = p.id
              WHERE p.id = """ + web.sqlquote(pageid) + """
           ORDER BY v.created DESC"""
    versions = db.query(sql)
    return versions

def get_page_by_versionid(versionid):
    sql = """SELECT v.id, p.id AS pageid, p.created, p.title, v.content, v.version, v.created AS modified
               FROM versions v
               JOIN pages p
                    ON v.pageid = p.id
              WHERE v.id = """ + web.sqlquote(versionid) + """
           ORDER BY v.created DESC"""
    versions = db.query(sql)
    version = versions[0]
    if not version.modified:
        version.modified = 0
    if not version.created:
        version.created = 0
    return version

def get_page_by_title(title):
    """
            >>> db.query("SELECT * FROM foo WHERE x = $x", vars=dict(x='f'), _test=True)
            <sql: "SELECT * FROM foo WHERE x = 'f'">
            >>> db.query("SELECT * FROM foo WHERE x = " + sqlquote('f'), _test=True)
    """
    try:
        sql = """SELECT p.id, p.created, p.title, v.content, v.version, v.created AS modified
                   FROM versions v
                   JOIN pages p
                        ON v.pageid = p.id
                  WHERE p.title = """ + web.sqlquote(title) + """
               ORDER BY version DESC"""
        pages = db.query(sql)
        page = pages[0]
        if not page.modified:
            page.modified = 0
        if not page.created:
            page.created = 0
        return page
        #return db.where('pages', title=title)[0]
    except IndexError:
        return None

def get_page_by_id(pageid):
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

def create_page(title, content):
    created = time.time()
    modified = created
    page = get_page_by_title(title)
    if not page:
        pageid = db.insert('pages', title=title, created=created, modified=modified)
        db.insert('versions', content=content, format="markdown", created=created, pageid=pageid, version=1)
    else:
        db.insert('versions', content=page.content, format="markdown", created=created, pageid=page.id, version=1)

def delete_page(pageid):
    db.delete('pages', where="id=$pageid")

def update_page(pageid, title, text):

    sql = "SELECT MAX(v.version) AS version FROM versions v WHERE v.pageid = " + str(pageid)
    versions = db.query(sql)
    version = versions[0]
    version = (int(version.version) + 1)

    created = time.time()
    modified = created

    # update modified date
    db.update('pages', where="id=$pageid", vars=locals(), modified=modified)
    db.insert('versions', content=text, format="markdown", created=created, pageid=pageid, version=version)
