var get_comments = {
    load:function (the_node, comment_id) {
	the_node.setAttribute('comment_id', comment_id);
	add_event(the_node, 'click', get_comments.click, true);
	reload_html(the_node, 
                config.get_url() + "c_url=" + encodeURIComponent(base64.encode(comment_id)),
                null, null,
                'gc');
    },
    click:function (e) {
	var the_node = e.target;
	toggle_visible(get_elements_by_class(the_node, 'comment_list', 'div'));
    },
    init:function () {
	standard_init('get_comments',function (el) {
	    add_event(el, 
		      'click', 
		      get_comments.click,
		      true);
	    get_comments.load(el, document.location.href);
	})

    }
}
add_event(window, 'load', get_comments.init, true);