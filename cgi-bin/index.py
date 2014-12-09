#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import common
from datetime import datetime

cookie = common.setup_cookies()
cursor = common.setup_mysql()
form   = common.setup_cgi_form()


common.print_html_header()
print """    <script jquery>
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

user_name, user_id = common.facebook_authentication( cursor, cookie )   

common.handle_upload( form )

print "<h1>The Dompetition</h1>"

common.print_top_table( user_name )
common.print_divider()

# Get competitor details

common.print_competition_tabs( form, cursor, user_id )


common.print_html_end()
