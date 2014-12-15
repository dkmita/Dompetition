#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import common
from datetime import datetime

cookie = common.setup_cookies()
cursor = common.setup_mysql()
form   = common.setup_cgi_form()


common.print_html_header()
common.print_tab_jquery()

user_name, user_id = common.facebook_authentication(cursor, cookie)   
common.handle_upload(form, cursor, user_id)

print "<h1>The Dompetition</h1>"

common.print_divider()
common.print_competition_tabs(form, cursor, user_id, user_name)
common.print_html_end()
