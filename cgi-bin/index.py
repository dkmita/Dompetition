#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import os, sys
from datetime import datetime
from random import random
from subprocess import Popen, PIPE
from MySQLdb import connect

# set up cgi setings
import cgi, cgitb 
cgitb.enable(logdir="/var/www/cgi-bin/cgi.log")
form = cgi.FieldStorage()

# set up db connection
mysql_pwd = os.environ['MYSQL_PWD']
conn = connect(host="localhost",user="root",passwd=mysql_pwd,db="sentience")
cursor = conn.cursor()
conn.autocommit(True)

# retrieve environment variables
apple_key = os.environ['APPLE_KEY']
secret_key = os.environ['SECRET_KEY']

# parse cookies and set up session cookie if one is not already defined
import Cookie
cookie = Cookie.SimpleCookie()
if 'HTTP_COOKIE' in os.environ:
    cookie_str = os.environ['HTTP_COOKIE']
    cookie.load(cookie_str)
if 'session' not in cookie:
    cookie['session'] = str(int(random()*10**10))
print cookie

#########################
# start page
#########################
print """
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" type="text/css" href="/style.css">
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
</head>
<body>
"""

# authentication
import facebookLogin, facebook
user_name = None
user_id=0
if 'session' in cookie:
    # check to see if we have an access_token associated with the session_id
    session_id = cookie['session'].value
    cursor.execute("""SELECT u.id, u.username, u.firstname, u.lastname
                      FROM session s
                      JOIN user u
                        ON s.user_id=u.id
                      WHERE s.id=%(session_id)s""" % locals())
    if cursor.rowcount:
        user_id, user_name, first_name, last_name = cursor.fetchone()
    else: 
        # couldn't recognize session_id. request data from facebook using acess_otken
        fb_cookie = facebook.get_user_from_cookie(cookie,apple_key,secret_key)
        if fb_cookie:
            # parse data and update dbs if necessary
            access_token = fb_cookie["access_token"]
            profile = facebook.GraphAPI(access_token).get_object("me")
            first_name = profile["first_name"]
            last_name = profile["last_name"]
            user_name = first_name[0].lower()+last_name.lower() 
            email = profile["email"]
            cursor.execute("select id from user where username='%(user_name)s'" % locals())
            if cursor.rowcount:
                # this is an old user so try to update data
                user_id, = cursor.fetchone()
                cursor.execute("update user set firstname='%(first_name)s', lastname='%(last_name)s', \
                                 email='%(email)s' where id=%(user_id)s; " % locals() )
            else:   
                # this is a new user so store in db    
                cursor.execute("insert into user (user_id,username,firstname,lastname,email) values \
                                 (null,'%(user_name)s','%(first_name)s','%(last_name)s','%(email)s'); " % locals() )
                cursor.execute("select id from user where username='%(user_name)s'" % locals())
                user_id, = cursor.fetchone()
            cursor.execute("insert into session (id, user_id) values (%(session_id)s,%(user_id)s )" % locals() ) 
if user_name is None:
    print facebookLogin.facebookLoginHtml % locals()
else:
    print "Welcome, ", first_name, last_name, "(" + user_name + ")"
    

# handle file upload
upload_message = ""
fileitem = None
if "file" in form:
    fileitem = form["file"]
    competition = form.getvalue("competition")
    fn = os.path.basename(fileitem.filename)
    # ensure py or pyc file
    if len(fn)<=4 or (fn[-3:] != '.py' and fn[-4:] != '.pyc'):
        upload_message = 'The file needs to be .py or .pyc type'
    else:
        # write file to upload directory with upload_time appended to file name
        fn_without_ending = fn[:fn.index('.')]
        fn_ending = fn[fn.index('.'):]
        now_datetime = datetime.now()
        upload_time_string = now_datetime.strftime("%Y%m%d%H%M%S")
        fn_with_upload_time = fn_without_ending + upload_time_string 
        full_fn = fn_with_upload_time + fn_ending
        open('/var/www/html/uploads/' + full_fn, 'wb').write(fileitem.file.read())
        
        # check file using fileChecker.py
        command = ["python", "/var/www/code/fileChecker.py", fn_with_upload_time]
        process = Popen( command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            # successfully found a valid class enter into db
            upload_message = 'The file "' + fn + '" was uploaded with class(es): '
            outputlines = stdout.splitlines()
            for class_name in outputlines[0].split(' '):
                mysql_datetime_str = now_datetime.strftime("%Y-%m-%d %H:%M%S")
                cursor.execute("""insert into competitor values (null,%(user_id)s,
                                %(competition)s,'%(fn_without_ending)s',
                                '%(class_name)s','%(mysql_datetime_str)s')""" %locals())
                upload_message += class_name + " "
            if len(outputlines) > 1:
                upload_message += "<br />" + outputlines[1]
        else:
            # no valid classes found, remove uploaded files 
            py_path = "/var/www/html/uploads/" + full_fn
            if os.path.exists(py_path):
                os.remove(py_path)
            pyc_path = py_path + "c"
            if os.path.exists(pyc_path):
                os.remove(pyc_path)
            upload_message = stdout + stderr 
if upload_message:
    print "<pre>",upload_message,"</pre>"


print "<h1>The Dompetition</h1>"
# print file upload code
print """Upload your code: &nbsp&nbsp&nbsp&nbsp<span class=example-click>show example</span><br />
<table class=example>
<tr><td><pre>
class TheRock():

    def __init__(self):
        # initialize your competitor
        pass

    def process_and_decide(self, state):
        opponents_move = state.get_opponents_last_guess()
        # figure out what you want to do and then
        # return a (move, comment) tuple
        return ("R", "Can you smell what The Rock is cookin'?")
</pre></td></tr></table>
<script type="text/javascript">
    $('.example').hide()
    $('.example-click').on('click',function() {
        $('.example').toggle();
    });
</script>
<form action="/cgi-bin/index.py" method="POST" enctype="multipart/form-data">
<label for="file">Filename:</label>
<input type="file" name="file" id="file"><br />
<input type="hidden" name="competition" value=1 /> 
<input id=uploadsubmit type="submit" name="submit" value="Submit"><br>
</form>""" % locals()
if user_name is None:
    print "<script>$('#uploadsubmit').prop('disabled', true);</script>"

# divider
print "<br />", "="*80, "<br />"

# print competitor table
cursor.execute("""
select
    cr.id,
    cr.filename,
    cr.classname,
    cr.upload_time,
    cn.filename,
    cn.classname,
    u.username,
    u.id
from competitor cr
join user u
    on cr.user_id = u.id
join competition cn
    on cr.competition_id = cn.id 
join (
    select user_id, classname, max(upload_time) as upload_time
    from competitor
    group by user_id, classname
    ) latest
on cr.user_id = latest.user_id
    and cr.classname = latest.classname
    and cr.upload_time = latest.upload_time
 """)

competitor_map = {}
for cr_id, cr_fn, cr_class, cr_time, cn_fn, cn_class, u_user, u_id in cursor.fetchall():
    time_str = cr_time.strftime("%Y%m%d%H%M%S")
    competitor_map[cr_id] = (cr_fn, cr_class, time_str, cn_fn, cn_class, u_user, u_id)

# Get competitor details
cr1_id = int(form.getvalue("comp1")) if form.getvalue("comp1") else None
cr2_id = int(form.getvalue("comp2")) if form.getvalue("comp2") else None
num_rounds = form.getvalue("numrounds","100")

print """<form><table><tr><td>
            <table border=1><tr><th></th><th>Competitor</th><th>Creator</th></tr>"""
for id in sorted(competitor_map.keys()):
    fn, classname, upload_time, cnfn, cncn, username,u_id = competitor_map[id]
    rowclass = "" if int(u_id) != int(user_id) else "class='green'"
    checked = ""
    if id == cr1_id:
        checked = "checked"
    print """<tr %(rowclass)s>
        <td><input type=radio name=comp1 value=%(id)s %(checked)s></td>
        <td>%(classname)s</td>
        <td>%(username)s</td>
    </tr>""" % locals()
print "</table></td>"
print "<td><table border=1><tr><th>Creator</th><th>Competitor</th><th></th></tr>"
for id in sorted(competitor_map.keys()):
    fn, classname, upload_time, cnfn, cncn, username, u_id = competitor_map[id]
    checked = ""
    if id == cr2_id:
        checked = "checked"
    print """<tr>
        <td>%(username)s</td>
        <td>%(classname)s</td>
        <td><input type=radio name=comp2 value=%(id)s %(checked)s></td>
    </tr>""" % locals()
print "</table>"
print "</td></tr></table>"
print "Num Rounds:<select name=numrounds>"
for rounds in ["100","250","1000"]:
    select_str = "selected" if rounds == num_rounds else ""
    print "  <option value=%(rounds)s %(select_str)s>%(rounds)s</option>" % locals()
print "</select>"
print "<input type=submit value='Compete'>"
print "</form>"

if not cr1_id or not cr2_id:
    print "</body></html>"
    sys.exit()

cr1_filename, cr1_classname, cr1_time, cn1_filename, cn1_classname, user, u_id = competitor_map[cr1_id]
cr2_filename, cr2_classname, cr2_time, cn2_filename, cn2_classname, user, u_id = competitor_map[cr2_id]
cr1_filename = cr1_filename + cr1_time
cr2_filename = cr2_filename + cr2_time

if cn1_filename != cn2_filename or cn1_classname != cn2_classname:
    print "Competitors",cr1_classname,cr2_classname,"are not for the same competition"
    print "</body></html>"
    exit()
    
arena = "/var/www/code/arena.py"
print "<br />", "="*80, "<br />"
print "<pre>"

command = ["python",arena, cn1_filename, cn1_classname, cr1_filename,cr1_classname, \
          cr2_filename, cr2_classname, num_rounds]
#print ' '.join(command), "<br />"
process = Popen( command, stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

print stderr, "</br>"
print stdout, "</br>"

print "</pre>"
print """
</body>
</html>"""
