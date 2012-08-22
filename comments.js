function inc(filename)
{
    var head = document.getElementsByTagName('head').item(0);
    script = document.createElement('script');
    script.src = "http://" + document.location.host + "/" + filename;
    script.type = 'text/javascript';
    head.appendChild(script)
}

inc("util.js");
inc("base64.js");
inc("config.js");
inc("l_get_comments.js");
inc("l_post_comment.js");
inc("l_hot_articles.js");
inc("l_recent_comments.js");

