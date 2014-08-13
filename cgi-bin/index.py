#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import os, sys, cgi, cgitb
import facebookLogin
from datetime import datetime
from subprocess import Popen, PIPE
from MySQLdb import connect
cgitb.enable(logdir="/Users/dkmita/www/cgi-bin/cgi.log")
form = cgi.FieldStorage()

conn = connect(host="localhost",user="root",passwd="Lamecat1",db="sentience")
cursor = conn.cursor()
conn.autocommit(True)
competitions = []
cursor.execute("""select name, id from competition""")
for name, id in cursor.fetchall():
    competitions += [(name, id)]

usernames = []
cursor.execute("""select username, id from user where username!='sentience'""")
for name, id in cursor.fetchall():
    usernames += [(name, id)]



# A nested FieldStorage instance holds the file
fileitem = None
upload_message = ""
if "file" in form:
    fileitem = form["file"]
    
    user = form.getvalue("username")
    competition = form.getvalue("competition")

    #strip leading path from file name to avoid directory traversal attacks
    fn = os.path.basename(fileitem.filename)
    if len(fn)<=4 or (fn[-3:] != '.py' and fn[-4:] != '.pyc'):
        upload_message = 'The file needs to be .py or .pyc type'
    else:
        fn_without_ending = fn[:fn.index('.')]
        fn_ending = fn[fn.index('.'):]

        now_datetime = datetime.now()
        upload_time_string = now_datetime.strftime("%Y%m%d%H%M%S")
        fn_with_upload_time = fn_without_ending + upload_time_string 
        full_fn = fn_with_upload_time + fn_ending

        open('/var/www/uploads/' + full_fn, 'wb').write(fileitem.file.read())
        
        command = ["python", "/var/www/code/fileChecker.py", fn_with_upload_time]
        process = Popen( command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            
            upload_message = 'The file "' + fn + '" was uploaded with class(es): '
            outputlines = stdout.splitlines()
            for class_name in outputlines[0].split(' '):
                mysql_datetime_str = now_datetime.strftime("%Y-%m-%d %H:%M%S")
                cursor.execute("""insert into competitor values (null,%(user)s,
                                %(competition)s,'%(fn_without_ending)s',
                                '%(class_name)s','%(mysql_datetime_str)s')""" %locals())
                upload_message += class_name
            if len(outputlines) > 1:
                upload_message += "<br />" + outputlines[1]
        else:
            py_path = "/var/www/uploads/" + full_fn
            if os.path.exists(py_path):
                os.remove(py_path)
            pyc_path = py_path + "c"
            if os.path.exists(pyc_path):
                os.remove(pyc_path)
            upload_message = stdout + stderr 
             

print """
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" type="text/css" href="/style.css">
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
</head>
<body>
"""
facebookLogin.facebookLogin()
if upload_message:
    print "<pre>",upload_message,"</pre>"
print """ <h1>The Dompetition</h1>
Upload your code: &nbsp&nbsp&nbsp&nbsp<span class=example-click>show example</span><br />
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
Username: <select name=username>"""
for name, id in usernames:
    print "<option value=%(id)s>%(name)s</option>" % locals()
print """</select>
Competition: <select name=competition>"""
for name, id in competitions:
    print "<option value=%(id)s>%(name)s</option>" % locals()
print """</select>
<input type="submit" name="submit" value="Submit"><br>
</form>"""
print "<br />", "="*80, "<br />"

cursor.execute("""
select
    cr.id,
    cr.filename,
    cr.classname,
    cr.upload_time,
    cn.filename,
    cn.classname,
    u.username
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
for cr_id, cr_filename, cr_classname, cr_upload_time, cn_filename, cn_classname, \
    cr_creator in cursor.fetchall():

    upload_string = cr_upload_time.strftime("%Y%m%d%H%M%S")
    competitor_map[cr_id] = (cr_filename, cr_classname, upload_string, \
        cn_filename, cn_classname, cr_creator)

# Get competitor details
cr1_id = int(form.getvalue("comp1")) if form.getvalue("comp1") else None
cr2_id = int(form.getvalue("comp2")) if form.getvalue("comp2") else None

print """<form><table><tr><td>
            <table border=1><tr><th></th><th>Competitor</th><th>Creator</th></tr>"""
for id in sorted(competitor_map.keys()):
    fn, classname, upload_time, cnfn, cncn, username = competitor_map[id]
    checked = ""
    if id == cr1_id:
        checked = "checked"
    print """<tr>
        <td><input type=radio name=comp1 value=%(id)s %(checked)s></td>
        <td>%(classname)s</td>
        <td>%(username)s</td>
    </tr>""" % locals()
print "</table></td>"
print "<td><table border=1><tr><th>Creator</th><th>Competitor</th><th></th></tr>"
for id in sorted(competitor_map.keys()):
    fn, classname, upload_time, cnfn, cncn, username = competitor_map[id]
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
print "<input type=submit value='Compete'>"
print "</form>"

if not cr1_id or not cr2_id:
    print "</body></html>"
    sys.exit()

cr1_filename, cr1_classname, cr1_time, cn1_filename, cn1_classname, user = competitor_map[cr1_id]
cr2_filename, cr2_classname, cr2_time, cn2_filename, cn2_classname, user = competitor_map[cr2_id]
cr1_filename = cr1_filename + cr1_time
cr2_filename = cr2_filename + cr2_time

if cn1_filename != cn2_filename or cn1_classname != cn2_classname:
    print "Competitors",cr1_classname,cr2_classname,"are not for the same competition"
    print "</body></html>"
    exit()
    
arena_filename = "/var/www/code/arena.py"
print "<br />", "="*80, "<br />"
print "<pre>"

command = ["python",arena_filename,cn1_filename, cn1_classname, cr1_filename,cr1_classname, \
          cr2_filename, cr2_classname]
#print ' '.join(command), "<br />"
process = Popen( command, stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

print stderr, "</br>"
print stdout, "</br>"

print "</pre>"
print """
</body>
</html>"""
