Introduction
------------
pText is a wiki app for personal knowledge management

Requirement
-----------
- easy_install web.py
- easy_install mysql-python/SQLite/Psycopg
- easy_install Markdown

Installation
------------

- Setup mod_wsgi
- Setup apache to handler WSGI Inteface

```
<VirtualHost *:80>
    DocumentRoot      "/www/plaintext"
    ServerName        wiki.local
    LogLevel info
    WSGIDaemonProcess wiki python-eggs=/tmp
    WSGIProcessGroup  wiki
    WSGIScriptAlias   / /www/plaintext/wsgi.py/
    Alias             /static  /www/plaintext/static
    AddType           text/html  .py
    ErrorLog "/private/var/log/apache2/wiki-error_log"
    CustomLog "/private/var/log/apache2/wiki-access_log" common
    <Directory />
        Order Allow,Deny
        Allow from all
        Options -Indexes
    </Directory>
    <Directory "/www/plaintext">
        Options +Indexes
    </Directory>
</VirtualHost>
```

- Setup DB
- Good to go

Export DB
---------
Just database structure:
```
    mysqldump wiki --no-data --skip-comments
```
