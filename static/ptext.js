$(document).ready(function() {
    //$('#content').autoGrow();
    $('#content').autoResize();
    $('#pages_tree').treeview({
        url: "/ajax",
        ajax: {
            data:{
            't':function(){
                console.info(this);
                return 'abc';
            }
            },
            type:"post"
        }
       });
});
