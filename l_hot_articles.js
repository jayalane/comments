var hot_articles = {
    load:function (the_node) {
	reload_html(the_node, 
                    config.hot_arts_url(),
                    null, null,
                    'ha');
    },
    init:function () {
	standard_init('hot_articles',function (el) {
	    hot_articles.load(el)
	})
	
    }
}
add_event(window, 'load', hot_articles.init, true);