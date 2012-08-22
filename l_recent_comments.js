var recent_comments = {
    load:function (the_node) {
	reload_html(the_node, 
                    config.recent_comments_url(),
                    null, null,
                    'rc');
    },
    init:function () {
	standard_init('recent_comments',function (el) {
	    recent_comments.load(el);
	})
    }
}
add_event(window, 'load', recent_comments.init, true);