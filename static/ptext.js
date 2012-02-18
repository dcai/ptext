YUI({
    charset: 'utf-8',
    loadOptional: true,
    combine: true,
    filter: 'raw' // can be debug
    //custom modules
    //modules: {
        //trueview: {
            //fullpath: '',
            //requires: []
        //}
    //}
}).use('node', 'yui2-treeview', 'autocomplete', 'autocomplete-filters', 'autocomplete-highlighters', function(Y) {
    function request(args, redraw) {
        var api = '/wiki/ajax';
        api = api + '?action='+args.action;
        var params = {};
        var scope = this;
        if (args['scope']) {
            scope = args['scope'];
        }
        // the form element only accept certain file types
        if (args['params']) {
            for (i in args['params']) {
                params[i] = args['params'][i];
            }
        }
        if (args.action == 'upload') {
            var list = [];
            for(var k in params) {
                var value = params[k];
                if(value instanceof Array) {
                    for(var i in value) {
                        list.push(k+'[]='+value[i]);
                    }
                } else {
                    list.push(k+'='+value);
                }
            }
            params = list.join('&');
        } else {
            params = build_querystring(params);
        }
        var cfg = {
            method: 'POST',
            on: {
                complete: function(id,o,p) {
                    if (!o) {
                        alert('IO FATAL');
                        return;
                    }
                    var data = null;
                    try {
                        data = Y.JSON.parse(o.responseText);
                    } catch(e) {
                        return;
                    }
                    // error checking
                    if (data && data.error) {
                        scope.print_msg(data.error, 'error');
                        scope.list();
                        return;
                    } else {
                        if (data.msg) {
                            //scope.print_msg(data.msg, 'info');
                        }
                        args.callback(id,data,p);
                    }
                }
            },
            arguments: {
                scope: scope
            },
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: params,
            context: this
        };
        Y.io(api, cfg);
    }
    function treeview_dynload(node, cb) {
        request({
            action: 'pagelist',
            salt: 'abc',
            callback: function(id, pages, args) {
                for(k in pages) {
                    build_tree(pages[k], node);
                }
                cb();
            }
        });
    }
    function build_tree(node, level) {
        if(node.children) {
            node.text = '<i><u>'+node.title+'</u></i>';
        }
        var info = {
            label:node.title,
        };
        var tmpNode = new YAHOO.widget.TextNode(info, level, false);
        if(node.children) {
            if(node.expanded) {
                tmpNode.expand();
            }
            tmpNode.isLeaf = false;
            if (node.path) {
                tmpNode.path = node.path;
            } else {
                tmpNode.path = '';
            }
            for(var c in node.children) {
                build_tree(node.children[c], tmpNode);
            }
        } else {
            tmpNode.isLeaf = true;
        }
    }
    var YAHOO = Y.YUI2;
    Y.one('body').addClass('yui3-skin-sam');
    var tags = ['javascrit', 'php', 'python', 'json'];
    var page_actions = new YAHOO.widget.TreeView('page_actions');
    page_actions.render();
    var treeview = new YAHOO.widget.TreeView(document.getElementById('pages_tree'));
    treeview.setDynamicLoad(treeview_dynload, 1);
    treeview.render();
    Y.one('#searchbox').plug(Y.Plugin.AutoComplete, {
        source: tags,
        resultFilters: 'phraseMatch',
        resultHighlighter: 'phraseMatch'
    });
})
function build_querystring(obj) {
    return convert_object_to_string(obj, '&');
}

function build_windowoptionsstring(obj) {
    return convert_object_to_string(obj, ',');
}

function convert_object_to_string(obj, separator) {
    if (typeof obj !== 'object') {
        return null;
    }
    var list = [];
    for(var k in obj) {
        k = encodeURIComponent(k);
        var value = obj[k];
        if(obj[k] instanceof Array) {
            for(var i in value) {
                list.push(k+'[]='+encodeURIComponent(value[i]));
            }
        } else {
            list.push(k+'='+encodeURIComponent(value));
        }
    }
    return list.join(separator);
}
