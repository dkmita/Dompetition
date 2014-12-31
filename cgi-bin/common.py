import os


def setup_mysql():
    # set up db connection
    from MySQLdb import connect
    mysql_pwd = os.environ['MYSQL_PWD']
    conn = connect(host="localhost",user="root",passwd=mysql_pwd,db="sentience")
    cursor = conn.cursor()
    conn.autocommit(True)
    return cursor


def setup_cookies():
    # parse cookies and set up session cookie if one is not already defined
    import Cookie
    cookie = Cookie.SimpleCookie()
    if 'HTTP_COOKIE' in os.environ:
        cookie_str = os.environ['HTTP_COOKIE']
        cookie.load(cookie_str)
    if 'session' not in cookie:
        from random import random
        cookie['session'] = str(int(random()*10**10))
    print cookie
    return cookie


def setup_cgi_form():
    import cgi, cgitb 
    cgitb.enable(logdir="/var/www/cgi-bin/cgi.log")
    return cgi.FieldStorage()


def facebook_authentication(cursor, cookie):
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
            apple_key = os.environ['APPLE_KEY']
            secret_key = os.environ['SECRET_KEY']
            fb_cookie = facebook.get_user_from_cookie(cookie,apple_key,secret_key)
            if fb_cookie:
                # parse data and update dbs if necessary
                access_token = fb_cookie["access_token"]
                profile = facebook.GraphAPI(access_token).get_object("me")
                first_name = profile["first_name"]
                last_name = profile["last_name"]
                user_name = first_name[0].lower()+last_name.lower() 
                if "email" in profile:
                    email = profile["email"]
                else:
                    email = "none"
                cursor.execute("SELECT id FROM user WHERE username='%(user_name)s'" % locals())
                if cursor.rowcount:
                    # this is an old user so try to update data
                    user_id, = cursor.fetchone()
                    cursor.execute( """
                        UPDATE user 
                        SET firstname='%(first_name)s', lastname='%(last_name)s', 
                            email='%(email)s' where id=%(user_id)s """ % locals() )
                else:   
                    # this is a new user so store in db    
                    cursor.execute( """
                        INSERT INTO user 
                            (id,username,firstname,lastname,email) 
                        VALUES
                            (null,'%(user_name)s','%(first_name)s','%(last_name)s','%(email)s')
                        """ % locals() )
                    cursor.execute("SELECT id FROM user WHERE username='%(user_name)s'" % locals())
                    user_id, = cursor.fetchone()
                cursor.execute( """
                    INSERT INTO session (id, user_id) 
                    VALUES (%(session_id)s,%(user_id)s )
                    """ % locals() ) 
    if user_name is None:
        print facebookLogin.facebookLoginHtml % locals()
    else:
        print "Welcome, ", first_name, last_name, "(" + user_name + ")"
    return user_name, user_id 

def handle_upload( form, cursor, user_id ):
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
            from datetime import datetime
            from subprocess import Popen, PIPE
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
                    mysql_datetime_str = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                        INSERT INTO competitor 
                        VALUES (null,%(user_id)s,%(competition)s,'%(fn_without_ending)s',
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


def print_html_header():
    print """
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" type="text/css" href="/style.css">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
</head>
<body>"""

def print_tab_jquery():
    print """  <script jquery>
    jQuery(document).ready(function() {
        jQuery('.tabs .tab-links a').on('click', function(e)  {
            var currentAttrValue = jQuery(this).attr('href');
     
            // Show/Hide Tabs
            jQuery('.tabs ' + currentAttrValue).show().siblings().hide();
     
            // Change/remove current tab to active
            jQuery(this).parent('li').addClass('active').siblings().removeClass('active');
     
            e.preventDefault();
        });
    });
  </script>"""


def print_top_table(user_name, comp_id, comp_name):
    print "    <table class=toptable border=0><tr><td>"
    print "      <h3>Upload your %(comp_name)s code:</h3>" % locals()
    print "      <form action='/cgi-bin/index.py' method=POST enctype='multipart/form-data'>"
    print "        <label for=file>Filename:</label>"
    print "        <input type=file name=file id=file><br />"
    print "        <input type=hidden name=competition value=%(comp_id)s>" % locals()
    print "        <input id=uploadsubmit type=submit name=submit value=Submit><br>"
    print "      </form>"
    if user_name is None:
        print "      <script>$('#uploadsubmit').prop('disabled', true);</script>"
    print "    </td><td valign=top>"
    print "      <h3>Tutorial</h3>"
    print "      <a href='/tutorial.html'>Follow these three quick steps to get started!</a>"
    print "    </td></tr></table><br />\n"


def print_divider():
    print "="*80, "<br />"


def get_competitor_map( cursor, comp_id ):
    # print competitor table
    cursor.execute( """
        SELECT
            cr.id,
            cr.filename,
            cr.classname,
            cr.upload_time,
            u.username,
            u.id
        FROM competitor cr
        JOIN user u
            ON cr.user_id = u.id
        JOIN competition cn
            ON cr.competition_id = cn.id 
        JOIN (
            SELECT cn.id, cr.user_id, cr.classname, MAX(cr.upload_time) AS upload_time
            FROM competitor cr
            JOIN competition cn
                ON cn.id = cr.competition_id
            WHERE cn.id = %(comp_id)s
            GROUP BY cn.id, cr.user_id, cr.classname
            ) latest
        ON cr.user_id = latest.user_id
            AND cr.classname = latest.classname
            AND cr.upload_time = latest.upload_time
            AND cn.id = %(comp_id)s
         """ % locals() )

    competitor_map = {}
    for cr_id, cr_fn, cr_class, cr_time, u_user, u_id in cursor.fetchall():
        time_str = cr_time.strftime("%Y%m%d%H%M%S")
        competitor_map[cr_id] = (cr_fn, cr_class, time_str, u_user, u_id)

    return competitor_map


def print_competition_table(competitor_map, user_id, cr1_id, cr2_id, num_turns, num_rounds, cn_id):
    print "    <form><table><tr><td>"
    print "      <table border=1><tr><th></th><th>Competitor</th><th>Creator</th></tr>"
    for id in sorted(competitor_map.keys()):
        fn, classname, upload_time, username,u_id = competitor_map[id]
        rowclass = "" if int(u_id) != int(user_id) else "class='green'"
        checked = ""
        if id == cr1_id:
            checked = "checked"
        print "        <tr %(rowclass)s>" % locals()
        print "          <td><input type=radio name=comp1 value=%(id)s %(checked)s></td>" % locals()
        print "          <td>%(classname)s</td>" % locals()
        print "          <td>%(username)s</td>" % locals()
        print "        </tr>"
    print "      </table></td>"
    print "    <td><table border=1><tr><th>Creator</th><th>Competitor</th><th></th></tr>"
    for id in sorted(competitor_map.keys()):
        fn, classname, upload_time, username, u_id = competitor_map[id]
        checked = ""
        if id == cr2_id:
            checked = "checked"
        print "        <tr>"
        print "          <td>%(username)s</td>" % locals()
        print "          <td>%(classname)s</td>" % locals()
        print "          <td><input type=radio name=comp2 value=%(id)s %(checked)s></td>" % locals()
        print "        </tr>"
    print "      </table>"
    print "    </td></tr></table>"
    print "    Num Turns:<select name=numturns>"
    for turns in ["10","100","250","1000","2000"]:
        select_str = "selected" if turns == num_turns else ""
        print "      <option value=%(turns)s %(select_str)s>%(turns)s</option>" % locals()
    print "      </select>"
    print "    Num Rounds:<select name=numrounds>"
    for rounds in ["1","5","10","100"]:
        select_str = "selected" if rounds == num_rounds else ""
        print "      <option value=%(rounds)s %(select_str)s>%(rounds)s</option>" % locals()
    print "      </select>"
    print "      <input type=hidden name=competition value=%(cn_id)s>" % locals()
    print "      <input type=submit value='Compete'>"
    print "    </form>"


def print_competition_results(competitor_map, cn_id, cr1_id, cr2_id, num_turns, num_rounds, cursor):
    from datetime import datetime
    from subprocess import Popen, PIPE
    cr1_filename, cr1_classname, cr1_time, user, u_id = competitor_map[cr1_id]
    cr2_filename, cr2_classname, cr2_time, user, u_id = competitor_map[cr2_id]
    cr1_filename = cr1_filename + cr1_time
    cr2_filename = cr2_filename + cr2_time

    cursor.execute("SELECT classname, filename FROM competition WHERE id = %(cn_id)s" % locals())
    cn_classname, cn_filename = cursor.fetchone()
   
    #get config
    arena = "/var/www/code/arena.py"
    command = ["python", arena, "none", cn_filename, cn_classname, \
               cr1_filename,cr1_classname, cr2_filename, cr2_classname, \
               num_turns, num_rounds, "config"]
    process = Popen( command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    config = stdout
   
    cursor.execute( """
        SELECT r.id
        FROM result r
        JOIN result_stats s1
            ON r.id = s1.result_id 
            AND s1.competitor_num = 1
        JOIN result_stats s2
            ON r.id = s2.result_id 
            AND s2.competitor_num = 2
        WHERE (
                s1.competitor_id = %(cr1_id)s 
                AND s2.competitor_id = %(cr2_id)s 
                AND r.config = %(config)s )
            OR (
                s1.competitor_id = %(cr2_id)s 
                AND s2.competitor_id = %(cr1_id)s 
                AND r.config = %(config)s )
        """ % locals() )
    result = cursor.fetchone()
    if result:
        result_id, = result
    else: 
        now_datetime = datetime.now()
        mysql_datetime_str = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute( """
            INSERT IGNORE INTO result
                (competition_id, config, timestamp)
            VALUES (%(cn_id)s, %(config)s, '%(mysql_datetime_str)s')""" % locals() )
        cursor.execute( """
            SELECT id 
            FROM result 
            WHERE timestamp='%(mysql_datetime_str)s'""" % locals() )
        result_id, = cursor.fetchone()
 
    #run in arena
    print_divider()
    print "<pre>"
    result_filename = "/var/www/results/" + str(result_id)
    command = ["python", arena, result_filename, cn_filename, cn_classname, \
               cr1_filename,cr1_classname, cr2_filename, cr2_classname, \
               num_turns, num_rounds, "compete"]
    print " ".join(command)
    process = Popen( command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
   
    #print outcome
    print stderr, "</br>"
    lines = stdout.split("\n") 
    for line in lines[1:]:
        print line
    print "</pre>"

    #put results in database 
    score1, score2 = lines[0].split()
    winner1 = 0
    winner2 = 0
    if int(score1) > int(score2):
        winner1 = 1
        winner2 = -1
    elif int(score2) > int(score1):
        winner1 = -1
        winner2 = 1
    config = int(config)
    
    cursor.execute( """
        INSERT IGNORE INTO result_stats
            (result_id, competitor_num, competitor_id, score, winner)
        VALUES (%(result_id)s, 1, %(cr1_id)s, %(score1)s, %(winner1)s),
            (%(result_id)s, 2, %(cr2_id)s, %(score2)s, %(winner2)s)""" % locals() )


def print_html_end():
    print """</body>
        </html>"""


def print_competition_tabs( form, cursor, user_id, user_name ):
    
    comp_id = int(form.getvalue("competition")) if form.getvalue("competition") else 1
    cr1_id = int(form.getvalue("comp1")) if form.getvalue("comp1") else None
    cr2_id = int(form.getvalue("comp2")) if form.getvalue("comp2") else None
    num_turns = form.getvalue("numturns","100")
    num_rounds = form.getvalue("numrounds","1")
    
    competitions_list = []
    cursor.execute("""SELECT id, name
                      FROM competition""")
    for id, name in cursor.fetchall():
        competitions_list += [(id, name)]
    
    
    print "<div class=tabs>"
    print "  <ul class=tab-links>"
    for id, name in competitions_list:
        classdetails = "class='active'" if id == comp_id else ""
        print "    <li %(classdetails)s><a href=#tab%(id)s>%(name)s</a></li>" % locals()
    print "  </ul>" 

    print "  <div class='tab-content'>"
    for id, name in competitions_list:
        classdetails = "class='tab active'" if id == comp_id else "class='tab'"
        print "    <div id=tab%(id)s %(classdetails)s>" % locals()
        print_top_table(user_name, id, name)
        competitor_map = get_competitor_map(cursor, id)
        print_competition_table( competitor_map, user_id, cr1_id, cr2_id, num_turns, num_rounds, id )
        if cr1_id and cr2_id and comp_id == id:
            print_competition_results( competitor_map, id, cr1_id, cr2_id, num_turns, num_rounds, cursor )
        print "    </div>\n"
    print "  </div>"
    print "</div>"

    
