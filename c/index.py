


from mod_python import apache
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from string import capwords
from _fields import *
import os
import urllib
import base64
import c_mysite
import datetime
import smtplib
import sys

ignore_keys = { "submit" : 1, "generic": 1 , "generic_2" : 1, "current" : 1 } # note my ignorance of python

cols_per_row = 4
cols_per_row_edit = 3

db = DB("comments")

#__auth_realm__ = "SilverSpringZendo"
#def __auth__(req, user, passwd):
#    if user == "SSZendo" and passwd == "IsNotSeveral":
#        return 1
#    return 0

def my_db(req):
    return db.get_db(req)

def regexpify_url(url):
    "There should be some better method here"
    regexp_str = 'http://(www.)?(takoma|silverspringvoice).com/'
    url = url.replace("http://www.takoma.com/", regexp_str);
    url = url.replace("http://takoma.com/", regexp_str);
    url = url.replace("http://silverspringvoice.com/", regexp_str);
    url = url.replace("http://www.silverspringvoice.com/", regexp_str);
    return url

def build_where_clause (keys, the_args, field_set, req):
    result = ""
    and_str = ""
    for key in keys:
        if ignore_keys.has_key(key):
            continue
        if the_args[key] == "":
            continue
        if field_set.get_field_by_name(key).sql_type == SQL_INT:
            result = result + and_str + """ %s = %s """ % (key, the_args[key])
        else:
            if field_set.get_field_by_name(key).flags & UI_BASE64:
                result = result + and_str + """ %s regexp '%s' """ % (key, regexpify_url(base64.urlsafe_b64decode(the_args[key].strip("\'").strip(" "))))
            else:
                result = result + and_str + """ %s like '%s' """ % (key, the_args[key].strip("\'").strip(" ") + "%")
        and_str = " and "
    if and_str != "":
        result = " where " + result
    return result;

def do_smtp(args, req):
    if args.has_key('c_name'):
        name = args['c_name'];
    else:
        name = "Unknown"
    if args.has_key('c_body'):
        body = args['c_body'];
    else:
        body = "Unknown"

    msg = """To: 3012706524@mms.mycingular.com
From: lisp@austin-lane.net
Subject: Comment by %s

%s
""" % (name, body,)
    server = smtplib.SMTP('mail.austin-lane.net')
    try:
        server.sendmail("lisp@austin-lane.net", "3012706524@mms.mycingular.com", msg)
    except smtplib.SMTPException:
        req.log_error("SMTP Error, oh well")
    server.quit()


def do_sql(sql_str,req):
    try:
        qqq = my_db(req).cursor()
        d = qqq.execute(sql_str);
        my_db(req).commit()
        qqq.close()

    except MySQLdb.OperationalError:
        # oh well
        a = 0

def do_sql_with_return(sql_str,req):
    d = 0
    
    try:
        qqq = my_db(req).cursor()
        d = qqq.execute(sql_str);
    
    except MySQLdb.OperationalError:
        # oh well
        a = 0
        d = None;
    return (d,qqq);

def safe_html(unsafe_html):
    return unsafe_html.replace("<","&lt;").replace(">","&gt;")

def good_date(datet):
    n = datetime.datetime.now()
    if (n.year != datet.year):
        strstr = "%x"
    elif (n.month != datet.month):
        strstr = "%b&nbsp;%d"
    elif n.day != datet.day:
        strstr = "%b&nbsp;%d"
    else:
        strstr = "%I:%M&nbsp;%p"
    return datet.strftime(strstr).lstrip("0")

def run_stp_string(args, table_name, stp_name, field_set, req):
    qqq = my_db(req).cursor()
    sql_str_begin  = "call " + stp_name + "("
    comma_str = ""
    cid = 0
    for k in args.keys():
        if k == "submit":
            continue
        if k == "cid":
            cid = int(args[k])
            continue
        if not field_set.field_in_table(table_name, k):
            continue
        if args[k] == "None" or args[k] == "":
            sql_str_begin = sql_str_begin + comma_str + "NULL"
            comma_str = ","
        else:
            sql_str_begin = sql_str_begin + comma_str + safe_html(field_set.get_field_by_name(k).sql_value_value(args[k], my_db(req)))
            comma_str = ","

    return sql_str_begin + ");"
    
def index(req, **args):
    return query(req, **args)

def query(req, **args):
    if args.has_key("c_url"):
        req.log_error("Get comments " + base64.urlsafe_b64decode(args['c_url'].strip("\'").strip(" ")))
    else:
        req.log_error("Get comments no url");
    html_out = """<div class="comment_list" >
    <span onclick="toggle_visible(this.parentNode);" class='hide-open'>&#9660; Hide Comments</span>
    <span onclick="toggle_visible(this.parentNode);" class='hide-closed' style='display: none;'>&#9658; See %d Comment%s</span>
    <div class='hidable'>"""
    keys = args.keys()
    keys.sort()
    field_set = get_fields_by_table("comment") 
    field_set.sort("query")
    if args.has_key('c_url'):
        sql_str = """ select """
        sql_str = sql_str + " comment.c_id "
        for f in field_set:
            sql_str = sql_str + ", " + f.get_name();
        sql_str = sql_str + """ from comment """
        sql_str = sql_str + build_where_clause(keys, args, field_set, req)
        sql_str = sql_str + " order by c_date desc"
        qqq = my_db(req).cursor()
        d = qqq.execute(sql_str);
    else:
        d = 0;
    #html_out = html_out + sql_str;
    #return c_mysite.header("Search results") + html_out + c_mysite.footer()
    if d > 0:
        if d == 1:
            html_out = html_out % (1, '') + "<p>" + "First post:" + "</p>"
        else:
            html_out = html_out % (d, 's') + "<p>" + str(d) + " comments</p>"
    else:
        html_out = html_out % (0, 's')
    old_row = {}
    for i in range(d):
        the_row = qqq.fetchone()
        if ((the_row[3] != None) and (len(the_row[3]) > 0) and (the_row[3][0] == 'h')):
            html_out = html_out + ("""<div class="comment"><div class="comment_subject">%s</div><div class="comment_body">%s</div><div class="comment_name">--<a href="%s">%s</a></div><div class="comment_date">%s</div></div>""" %
               (the_row[5], the_row[4], the_row[3], the_row[2], good_date(the_row[9])))
        else:
            html_out = html_out + ("""<div class="comment"><div class="comment_subject">%s</div><div class="comment_body">%s</div><div class="comment_name">--%s</div><div class="comment_date">%s</div></div>""" %
               (the_row[5], the_row[4], the_row[2], good_date(the_row[9])))
        old_row = the_row
    html_out = html_out + "</div></div>"
    return c_mysite.header("Search results") + html_out + c_mysite.footer()

trans_field_names = { 'akkeoq': 'c_subject',
                      'akkeo': 'c_body',
                      'dfdf': 'c_url',
                      'abcnmo': 'c_name',
                      'adefdc': 'c_email',
                      'akkeop': 'c_blog' } 


def translate_form_names (args):
    new_args = {}
    for k in args.keys():
        new_args[trans_field_names[k]] = args[k]
    return new_args;

def post_comment_result(req, ** args):
    args = translate_form_names(args)
    if args.has_key("c_url"):
        req.log_error("Post comment " + args['c_url'])
    else:
        req.log_error("post comment no url");
    html_out = "<html><body>"
    for k in args.keys():
        html_out = html_out + k + "=" + args[k] + "<br/>"
    html_out = html_out + "</body></html>"
    field_set = get_fields_by_table("comment") 
    field_set.sort("query")
    args['c_ip'] = req.get_remote_host()
    sql_str = run_stp_string(args, "comment", "comments.insert_comment", field_set, req)
    do_sql(sql_str, req)
    do_smtp(args, req) 
    req.log_error("Comment posted by: " + req.headers_in['Referer']);
    req.log_error("                   " + sql_str);
    return """<html><head><title>Comment posted!</title><meta http-equiv="Refresh" content="3;url=%s"/></head>
    <body><h3>Comment posted!</h3><br/><h3>Site reloading....</h3></body></html>""" % (req.headers_in['Referer'], )

def hot_articles(req, ** args):
    html_out = ""
    args = {'c_num': 10};
    field_set = get_fields_by_table("comment") 
    field_set.sort("query")
    sql_str = run_stp_string(args, "comment", "comments.hot_articles", field_set, req);
    (num_rows, qqq) = do_sql_with_return(sql_str, req);
    if num_rows > 0:
        html_out = """<div class="article_list">"""
        for i in range(num_rows):
            the_row = qqq.fetchone();
            html_out = html_out + """<div class="article_item"><a href="%s">%s</a></div>""" % (the_row[0], the_row[1])
        html_out = html_out + "</div>"
        result = html_out;
    else:
        result = ""
    return result;

def recent_comments(req, ** args):
    html_out = ""
    args = {'c_num': 10};
    field_set = get_fields_by_table("comment") 
    field_set.sort("query")
    sql_str = run_stp_string(args, "comment", "comments.recent_comments", field_set, req);
    (num_rows, qqq) = do_sql_with_return(sql_str, req);
    if num_rows > 0:
        html_out = """<div class="recent_comment_list">"""
        for i in range(num_rows):
            the_row = qqq.fetchone();
            if the_row[3] == None:
                html_out = html_out + """<div class="recent_comments_item">At %s, about <a href="%s">%s</a>,&nbsp;%s said &quot;<span class="recent_quoted">%s...</span>&quot;</div>""" % (good_date(the_row[0]), the_row[1], the_row[2], the_row[3], the_row[5],)
            else:
                html_out = html_out + """<div class="recent_comments_item">At %s, about <a href="%s">%s</a>,&nbsp;<a href="%s">%s</a> said &quot;<span class="recent_quoted">%s...</span>&quot;</div>""" % (good_date(the_row[0]), the_row[1], the_row[2], the_row[4], the_row[3], the_row[5],)
        html_out = html_out + "</div>"
        result = html_out;
    else:
        result = ""
    return result
    
def post_comment(req, ** args):
    url = args['c_url']
    req.log_error("Post comment form " + base64.urlsafe_b64decode(args['c_url'].strip("\'").strip(" ")))
    return """
    <div class="post_comment_form">
    <span  onclick="toggle_visible(this.parentNode);" class='hide-open' style='display: none;'>&#9660; Post Your Comment!</span>
    <span  onclick="toggle_visible(this.parentNode);" class='hide-closed'>&#9658; Post Your Comment!</span>
    <div class="hidable" style='display: none;'>
    <div class="post_comment_body">
    <form action="http://comments.austin-lane.net/c/post_comment_result" method="post" onsubmit="return post_comment.validate(this);" id=""" + "'" + urllib.quote(url) + "'" + """>
    <input type="hidden" name="dfdf" value=""" + "'" + urllib.quote(url) + "'" + """/>
<div class="tablediv">
<div class="rowdiv">
<div class="celldivl"><label class="post_comment_field" for="akkeoq">Subject: (required) </label></div>
<div class="celldivr"><input type="text" name="akkeoq" maxlength="63" class="fld"></div></div>
<div class="rowdiv"><div class="celldivl"><label class="post_comment_field" for="akkeo">Comment: (required)</label></div>
<div class="celldivr"><textarea name="akkeo" rows="12" cols="17"></textarea></div></div>
<div class="rowdiv">
<div class="celldivl"><label class="post_comment_field" for="abcnmo">Name: (required)</label></div>
<div class="celldivr"><input type="text" name="abcnmo" maxlength="63" class="fld"></div></div>
<div class="rowdiv">
<div class="celldivl"><label class="post_comment_field" for="adefdc">Email (required, but not shown to the public):</label></div>
<div class="celldivr"><input type="text" name="adefdc" maxlength="127" class="fld"></div></div>
<div class="rowdiv">
<div class="celldivl"><label class="post_comment_field" for="akkeop">Website / blog:</label></div>
<div class="celldivr"><input type="text" name="akkeop" maxlength="127" class="fld"></div></div>
<div class="rowdiv">
<p style="cursor: pointer; cursor: hand;" onclick="if (document.forms[1].onsubmit()) { document.forms[1].submit();};"><b>Click to Save</b></p>
<span style="display: none;"><input type="submit"/></span>
</div>
</div></div>
    </form></div></div></div>"""
    
