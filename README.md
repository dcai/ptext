Introduction
------------

Plaintext is a wiki app for personal knowledge management


Installation
------------

# Setup mod_wsgi
# Install web.py and markdown using easy_install tool
# Setup apache to handler WSGI Inteface
`
<VirtualHost wiki.local:80>
    DocumentRoot "/www/webpy"
    ServerName   wiki.local
    WSGIScriptAlias   / /www/webpy/code.py/
    Alias             /static  /www/webpy/static
    AddType           text/html  .py
    ServerAdmin root@tux.im
    ErrorLog "/private/var/log/apache2/wiki-error_log"
    CustomLog "/private/var/log/apache2/wiki-access_log" common
</VirtualHost>
`
# Good to go
