var post_comment = {
    fld_labels:["Subject", "Comment", "Name", "Email", "Website/blog"],
    first_time:0,
    click:function (e) {
        var the_node = e.target;
        toggle_visible(the_node);
	if (post_comment.first_time == 0) {
            document.forms[1].elements[1].focus();
	    post_comment.first_time = 1;
	}
    },
    load:function (the_node, comment_id) {
        the_node.setAttribute('comment_id', comment_id)
        add_event(the_node, 'click', post_comment.click, true)
        reload_html(the_node, 
                    config.post_url() + "c_url=" + encodeURIComponent(base64.encode(comment_id)), 
                    null, null,
                    'pc');
    },
    validate:function (thing_node) {
        var a;
        var post_body = "";
        var amp_string = "";
        ary = document.forms[1].elements;
        msg = "I'm sorry, but the following required fields are missing:\n\n"
        valided = true;
        for (a = 0; a < ary.length; a++) {
            if ((ary[a].value == "") && (a != 5)) {
                if (typeof(post_comment.fld_labels[a-1]) != 'undefined') {
                    msg = msg + post_comment.fld_labels[a-1] + "\n";
                    valided = false;
                }
            }
        }
        if (valided == false) {
            alert(msg);
        }
        return valided;
     
    },
    init:function () {
        standard_init('post_comment',
                      function (el) {
                          add_event(el, 
                                    'click',
                                    post_comment.click,
                                    true);
                          post_comment.load(el, document.location.href);
                      })
    }
}

add_event(window, 'load', post_comment.init, true);
