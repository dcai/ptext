Introduction
------------
pText is a wiki app for personal knowledge management

Requirement
-----------
- web.py
- MySQLdb/SQLite/Psycopg
- Markdown

Installation
------------

- Setup mod_wsgi
- Setup apache to handler WSGI Inteface
`
<VirtualHost *:80>
    DocumentRoot "/www/wiki"
    ServerName   wiki.local
    WSGIDaemonProcess wiki
    WSGIProcessGroup  wiki
    WSGIScriptAlias   / /var/www/wiki/wsgi.py/
    Alias             /static  /www/webpy/static
    AddType           text/html  .py
    ServerAdmin root@tux.im
    LogLevel warn
    ErrorLog ${APACHE_LOG_DIR}/wiki-error.log
    CustomLog ${APACHE_LOG_DIR}/wiki-access.log combined
</VirtualHost>
`
- Setup DB
- Good to go
